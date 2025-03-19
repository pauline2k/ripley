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
from teena.pages.page import Page
from teena.test_utils import utils


class CourseSectionsTables(Page):

    @staticmethod
    def available_course_heading_xpath(course):
        return f'//*[starts-with(text(), "{course.code}")]'

    def available_sections_form_button(self, course):
        return By.XPATH, f'{self.available_course_heading_xpath(course)}/ancestor::button'

    def available_sections_course_title(self, course):
        path = '/descendant::span[starts-with(text(), "— ") or starts-with(text(), " — ")]'
        loc = By.XPATH, f'{self.available_course_heading_xpath(course)}{path}'
        try:
            self.when_present(loc, utils.get_short_timeout())
            return self.element(loc).text
        except TimeoutError:
            return ''

    def available_sections_select_all(self, course):
        path = '/ancestor::button/following-sibling::div//input[starts-with(@id, "select-all-toggle")]'
        return By.XPATH, f'{self.available_course_heading_xpath(course)}{path}'

    def available_sections_table_xpath(self, course, section):
        path = f'/ancestor::button/following-sibling::div//table[contains(., "{section.id}")]'
        return f'{self.available_course_heading_xpath(course)}{path}'

    def available_sections_table(self, course, section):
        return By.XPATH, self.available_sections_table_xpath(course, section)

    SECTION_PANEL = By.XPATH, '//div[contains(@id, "sections-course-")]'

    def expand_all_available_sections(self):
        app.logger.info('Expanding all available sections')
        self.when_present(self.SECTION_PANEL, utils.get_medium_timeout())
        panels = self.elements(self.SECTION_PANEL)
        app.logger.info(f'There are {len(panels)} sets of sections to expand')
        for el in panels:
            idx = panels.index(el)
            btn_loc = By.XPATH, f'(//button[contains(@class, "v-expansion-panel-title")])[{idx + 1}]'
            self.when_present(btn_loc, 3)
            if self.element(btn_loc).get_dom_attribute('aria-expanded') == 'false':
                app.logger.info(f'Expanding course section set {idx}')
                self.wait_for_element_and_click(btn_loc)
            else:
                app.logger.info(f'Course section set {idx} is already expanded')

    def expand_available_course_sections(self, course, section):
        self.when_present(self.SECTION_PANEL, utils.get_short_timeout())
        self.scroll_to_top()
        if self.is_visible(self.available_sections_table(course, section)):
            app.logger.info(f'The available sections table is already expanded for {course.code}')
        else:
            app.logger.info(f'Expanding available sections table for {course.code}')
            self.wait_for_element_and_click(self.available_sections_form_button(course))
            self.when_visible(self.available_sections_table(course, section), utils.get_short_timeout())
            time.sleep(2)

    def collapse_available_sections(self, course, section):
        if self.is_visible(self.available_sections_table(course, section)):
            app.logger.info(f'Collapsing available sections table for {course.code}')
            self.wait_for_element_and_click(self.available_sections_form_button(course))
            self.when_not_visible(self.available_sections_table(course, section), utils.get_short_timeout())
        else:
            app.logger.info(f'The available sections table is already expanded for {course.code}')
