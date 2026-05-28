"""
Copyright ©2025. The Regents of the University of California (Regents). All Rights Reserved.

Permission to use, copy, modify, and distribute this software and its documentation
for educational, research, and not-for-profit purposes, without fee and without a
signed licensing agreement, is hereby granted, provided that the above copyright
notice, this paragraph and the following two paragraphs appear in all copies,
modifications, and distributions.

Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.

IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
OF THE POSSIBILITY OF SUCH DAMAGE.

REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
"AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
ENHANCEMENTS, OR MODIFICATIONS.
"""

import time

from flask import current_app as app
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait as Wait
from teena.pages.ripley.course_sections_tables import CourseSectionsTables
from teena.pages.ripley.site_creation_page import SiteCreationPage
from teena.test_utils import utils


class CreateCourseSitePage(CourseSectionsTables, SiteCreationPage):

    NEED_HELP = By.ID, 'toggle-help-notice-btn'
    INSTR_MODE_LINK = By.ID, 'link-to-httpsberkeleyservicenowcomkb_viewdosysparm_articleKB0010732instructionmode'

    SWITCH_TO_INSTRUCTOR = By.ID, 'radio-btn-mode-act-as'
    AS_INSTRUCTOR_BUTTON = By.ID, 'sections-by-uid-button'
    INSTRUCTOR_UID = By.ID, 'instructor-uid'
    SWITCH_TO_CCN = By.ID, 'radio-btn-mode-section-id'
    REVIEW_CCNS_BUTTON = By.ID, 'sections-by-ids-button'
    CCN_LIST = By.ID, 'page-create-course-site-section-id-list'

    NEXT_BUTTON = By.ID, 'page-create-course-site-continue'
    CANCEL_BUTTON = By.ID, 'page-create-course-site-cancel'

    SITE_NAME_INPUT = By.ID, 'course-site-name'
    SITE_ABBREVIATION = By.ID, 'course-site-abbreviation'
    SITE_NAME_ERROR = By.XPATH, '//div[text()="Please provide site name."]'
    SITE_ABBREVIATION_ERROR = By.XPATH, '//div[text()="Please provide site abbreviation."]'

    CREATE_SITE_BUTTON = By.ID, 'create-course-site-button'
    GO_BACK_BUTTON = By.ID, 'go-back-button'

    @staticmethod
    def term_button(term):
        return By.XPATH, f'//button[contains(., "{term.name}")]'

    def choose_term(self, course):
        Wait(self.driver, utils.get_medium_timeout()).until(ec.any_of(
            ec.presence_of_element_located(self.term_button(course.term)),
            ec.presence_of_element_located((By.ID, 'official-sections-heading')),
        ))
        if self.is_present(self.term_button(course.term)):
            if 'v-btn--active' in self.element(self.term_button(course.term)).get_dom_attribute('class'):
                app.logger.info(f'Term {course.term.name} is already selected')
            else:
                app.logger.info(f'Selecting term {course.term.name}')
                self.wait_for_element_and_click(self.term_button(course.term))
        else:
            app.logger.info('Only one term exists')

    def search_for_course(self, course_site):
        app.logger.info(f'Searching for {course_site.course.code} in {course_site.course.term.name}')
        if course_site.create_site_workflow == 'uid':
            teacher = course_site.course.teachers[0]
            app.logger.info(f'Searching by instructor UID {teacher.uid}')
            self.wait_for_element_and_click(self.SWITCH_TO_INSTRUCTOR)
            self.wait_for_element_clear_and_send_keys(self.INSTRUCTOR_UID, teacher.uid)
            self.wait_for_element_and_click(self.AS_INSTRUCTOR_BUTTON)
            self.choose_term(course_site.course)

        elif course_site.create_site_workflow == 'ccn':
            app.logger.info('Searching by CCN list')
            self.wait_for_element_and_click(self.SWITCH_TO_CCN)
            self.choose_term(course_site.course)
            time.sleep(1)
            ccn_list = [str(section.section_id) for section in course_site.sections]
            app.logger.info(f'CCN list is {ccn_list}')
            self.wait_for_element_clear_and_send_keys(self.CCN_LIST, ', '.join(ccn_list))
            self.wait_for_element_and_click(self.REVIEW_CCNS_BUTTON)
        else:
            app.logger.info('Searching as the instructor')
            self.choose_term(course_site.course)

    def click_need_help(self):
        self.wait_for_element_and_click(self.NEED_HELP)

    @staticmethod
    def section_checkbox(section_id):
        return By.ID, f'template-canvas-manage-sections-checkbox-{section_id}'

    def select_sections(self, sections):
        sections.sort(key=lambda s: s.section_id)
        for section in sections:
            if self.element(self.section_checkbox(section.section_id)).is_selected():
                app.logger.info(f'Section {section.section_id} is already selected')
            else:
                app.logger.info(f'Selecting section {section.section_id}')
                self.wait_for_element_and_click(self.section_checkbox(section.section_id))

    def section_course_code(self, section_id):
        loc = By.XPATH, f'//td[contains(@id, "{section_id}-course")]'
        self.when_present(loc, utils.get_short_timeout())
        return self.element(loc).text.strip()

    def section_label(self, section_id):
        loc = By.XPATH, f'//td[contains(@id, "{section_id}-name")]'
        self.when_present(loc, utils.get_short_timeout())
        return self.element(loc).text.strip()

    def section_schedules(self, section_id):
        loc = By.XPATH, f'//td[contains(@id, "{section_id}-schedule")]/*'
        self.when_present(loc, utils.get_short_timeout())
        return [el.text.strip().upper() for el in self.elements(loc) if el.text.strip()]

    def section_locations(self, section_id):
        loc = By.XPATH, f'//td[contains(@id, "{section_id}-location")]/*'
        self.when_present(loc, utils.get_short_timeout())
        return [el.text.strip() for el in self.elements(loc) if el.text.strip()]

    def section_instructors(self, section_id):
        loc = By.XPATH, f'//td[contains(@id, "{section_id}-instructors")]/*'
        self.when_present(loc, utils.get_short_timeout())
        return [el.text.strip() for el in self.elements(loc) if el.text.strip()]

    def section_data(self, section_id):
        return {
            'code': self.section_course_code(section_id),
            'label': self.section_label(section_id),
            'id': section_id,
            'schedules': self.section_schedules(section_id),
            'locations': self.section_locations(section_id),
            'instructors_and_roles': self.section_instructors(section_id),
        }

    SECTION_ID = By.XPATH, '//td[@class="td-section-id"]'

    def visible_section_ids(self):
        self.when_present(self.SECTION_ID, 3)
        time.sleep(1)
        els = self.elements(self.SECTION_ID)
        app.logger.info(f'There are {len(els)} section ids')
        return [(el.text).replace('Section ID:', '') for el in els]

    def course_section_ids(self, course):
        identifier = f"{'-'.join(course.code.lower().split())}-{course.term.code}"
        return [(el.text).replace('Section ID:', '') for el in self.elements(
            (By.XPATH, f'//div[@id="sections-course-{identifier}"]//td[@class="td-section-id"]'))]

    def click_next(self):
        self.wait_for_element_and_click(self.NEXT_BUTTON)
        self.when_present(self.SITE_NAME_INPUT, utils.get_short_timeout())

    def enter_site_name(self, string):
        self.wait_for_element_remove_chars_send_keys(self.SITE_NAME_INPUT, string)

    def enter_site_abbreviation(self, string):
        self.wait_for_element_remove_chars_send_keys(self.SITE_ABBREVIATION, string)

    def enter_site_titles(self, course):
        site_abbrev = f'QA bCourses Test {utils.get_test_identifier()}'
        self.enter_site_name(f'{site_abbrev} - {course.code}')
        self.enter_site_abbreviation(site_abbrev)
        return site_abbrev

    def click_create_site(self):
        self.wait_for_element_and_click(self.CREATE_SITE_BUTTON)

    def click_cancel_site_creation(self):
        self.wait_for_element_and_click(self.CANCEL_BUTTON)

    def click_go_back(self):
        app.logger.info('Clicking go-back button')
        self.wait_for_element_and_click(self.GO_BACK_BUTTON)

    def provision_course_site(self, course_site):
        self.load_embedded_tool(course_site.course.teachers[0])
        self.click_create_course_site()
        self.search_for_course(course_site)
        self.expand_available_course_sections(course_site.course, course_site.sections[0])
        if course_site.sections == course_site.course.sections:
            self.wait_for_element_and_click(self.available_sections_select_all(course_site.course))
        else:
            self.select_sections(course_site.sections)
        self.click_next()
        course_site.course.title = self.enter_site_titles(course_site.course)
        self.click_create_site()
        self.wait_for_site_id(course_site)
