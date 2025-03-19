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
from teena.pages.ripley.course_sections_tables import CourseSectionsTables
from teena.pages.ripley.site_creation_page import SiteCreationPage
from teena.test_utils import utils


class OfficialSectionsPage(CourseSectionsTables, SiteCreationPage):

    OFFICIAL_SECTIONS_LINK = By.LINK_TEXT, 'Official Sections'
    EDIT_SECTIONS_BUTTON = By.ID, 'official-sections-edit-btn'

    SECTION_NAME_MSG = By.XPATH, '//div[contains(., "The section name in bCourses no longer matches")]'
    CANCEL_BUTTON = By.ID, 'official-sections-cancel-btn'
    SAVE_CHANGES_BUTTON = By.ID, 'official-sections-save-btn'

    UPDATING_SECTIONS_MSG = By.XPATH, '//*[contains(., "Updating Official Sections in Course Site")]'
    SECTIONS_UPDATED_MSG = By.XPATH, '//div[text()="The sections in this course site have been updated successfully."]'
    UPDATE_MSG_CLOSE_BUTTON = By.XPATH, '//div[contains(text(), "updated successfully")]/../following-sibling::div/button'

    def click_edit_sections(self):
        app.logger.info('Clicking edit sections button')
        self.wait_for_page_and_click(self.EDIT_SECTIONS_BUTTON)
        self.when_visible(self.SAVE_CHANGES_BUTTON, utils.get_short_timeout())

    def click_save_changes(self):
        app.logger.info('Clicking save changes button')
        self.wait_for_element_and_click(self.SAVE_CHANGES_BUTTON)

    def save_changes_and_wait_for_success(self):
        self.click_save_changes()
        self.when_visible(self.UPDATING_SECTIONS_MSG, utils.get_short_timeout())
        self.when_visible(self.SECTIONS_UPDATED_MSG, utils.get_long_timeout())

    def close_section_update_success(self):
        app.logger.info('Closing the section update success message')
        self.wait_for_element_and_click(self.UPDATE_MSG_CLOSE_BUTTON)

    @staticmethod
    def expected_instructors(section):
        if section.instructors_with_roles:
            names = [i.user.full_name for i in section.instructors_with_roles]
            names.sort()
            return names
        else:
            return ['—']

    # STATIC VIEW - CURRENT SECTIONS

    STATIC_VIEW_SECTION_ROW = By.XPATH, '//tr[contains(@id, "template-sections-table-preview")]'
    STATIC_VIEW_SECTIONS_TABLE = By.ID, 'template-sections-table-preview'

    def static_sections_count(self):
        self.when_visible(self.STATIC_VIEW_SECTIONS_TABLE, utils.get_medium_timeout())
        self.when_present(self.STATIC_VIEW_SECTION_ROW, utils.get_short_timeout())
        return len(self.elements(self.STATIC_VIEW_SECTION_ROW))

    @staticmethod
    def static_section_row(section):
        return By.ID, f'template-sections-table-preview-{section.section_id}'

    def static_section_data(self, section):
        course_loc = By.ID, f'template-sections-table-preview-{section.section_id}-course'
        label_loc = By.ID, f'template-sections-table-preview-{section.section_id}-name'
        section_id_loc = By.ID, f'template-sections-table-preview-{section.section_id}-id'
        schedules_loc = By.XPATH, f'//td[contains(@id, "{section.section_id}-schedule")]/*'
        locations_loc = By.XPATH, f'//td[contains(@id, "{section.section_id}-location")]/*'
        instructor_loc = By.XPATH, f'//td[contains(@id, "{section.section_id}-instructors")]'
        return {
            'course': self.el_text_if_exists(course_loc),
            'label': self.el_text_if_exists(label_loc),
            'section_id': self.el_text_if_exists(section_id_loc),
            'schedules': [sch.upper() for sch in self.els_text_if_exist(schedules_loc) if sch],
            'locations': [loc for loc in self.els_text_if_exist(locations_loc) if loc],
            'instructors': self.el_text_if_exists(instructor_loc, 'Instructors:').split('\n'),
        }

    # EDIT MODE - CURRENT SECTIONS

    CURRENT_SECTIONS_TABLE = By.ID, 'template-sections-table'
    CURRENT_SECTIONS_TABLE_ROW = By.XPATH, '//table[@id="template-sections-table"]/tbody/tr'

    @staticmethod
    def current_sections_table_xpath():
        return '//table[@id="template-sections-table"]'

    def current_sections_count(self):
        self.when_visible(self.CURRENT_SECTIONS_TABLE, utils.get_medium_timeout())
        self.when_present(self.CURRENT_SECTIONS_TABLE_ROW, utils.get_short_timeout())
        return len(self.elements(self.CURRENT_SECTIONS_TABLE_ROW))

    @staticmethod
    def current_section_row(section):
        return By.ID, f'template-sections-table-{section.section_id}'

    def current_section_data(self, section):
        table_xpath = self.current_sections_table_xpath()
        course_loc = By.ID, f'template-sections-table-{section.section_id}-course'
        label_loc = By.ID, f'template-sections-table-{section.section_id}-name'
        section_id_loc = By.ID, f'template-sections-table-{section.section_id}-id'
        schedules_loc = By.XPATH, f'{table_xpath}//td[contains(@id, "{section.section_id}-schedule")]/*'
        locations_loc = By.XPATH, f'{table_xpath}//td[contains(@id, "{section.section_id}-location")]/*'
        instructor_loc = By.XPATH, f'{table_xpath}//td[contains(@id, "{section.section_id}-instructors")]'
        return {
            'course': self.el_text_if_exists(course_loc),
            'label': self.el_text_if_exists(label_loc),
            'section_id': self.el_text_if_exists(section_id_loc),
            'schedules': [sch.upper() for sch in self.els_text_if_exist(schedules_loc) if sch],
            'locations': [loc for loc in self.els_text_if_exist(locations_loc) if loc],
            'instructors': self.el_text_if_exists(instructor_loc, 'Instructors:').split('\n'),
        }

    @staticmethod
    def section_update_button(section):
        return By.ID, f'section-{section.section_id}-update-btn'

    def click_update_section(self, section):
        app.logger.info(f'Clicking update button for section {section.section_id}')
        self.wait_for_element_and_click(self.section_update_button(section))
        time.sleep(1)

    @staticmethod
    def section_delete_button(section):
        return By.ID, f'section-{section.section_id}-unlink-btn'

    def click_delete_section(self, section):
        app.logger.info(f'Clicking delete button for section {section.section_id}')
        self.wait_for_element_and_click(self.section_delete_button(section))
        time.sleep(1)

    def delete_sections(self, sections):
        for section in sections:
            self.click_delete_section(section)
        self.click_save_changes()

    @staticmethod
    def section_undo_add_button(section):
        return By.ID, f'section-{section.section_id}-undo-link-btn'

    def click_undo_add_section(self, section):
        app.logger.info(f'Clicking undo add button for section {section.section_id}')
        self.wait_for_element_and_click(self.section_undo_add_button(section))
        time.sleep(1)

    # EDIT MODE - AVAILABLE SECTIONS

    def available_sections_count(self, course, section):
        return len(self.elements(
            (By.XPATH, f'{self.available_sections_table_xpath(course, section)}//td[contains(@id, "-course")]')))

    def available_section_row(self, course, section):
        return (By.XPATH,
                f'{self.available_sections_table_xpath(course, section)}//tr[contains(@id, "#{section.section_id}")]')

    def available_section_data(self, course, section):
        table_xpath = self.available_sections_table_xpath(course, section)
        course_loc = By.XPATH, f'{table_xpath}//td[contains(@id, "{section.section_id}-course")]'
        label_loc = By.XPATH, f'{table_xpath}//td[contains(@id, "{section.section_id}-name")]'
        section_id_loc = By.XPATH, f'{table_xpath}//td[contains(@id, "{section.section_id}-id")]'
        schedules_loc = By.XPATH, f'{table_xpath}//td[contains(@id, "{section.section_id}-schedule")]/*'
        locations_loc = By.XPATH, f'{table_xpath}//td[contains(@id, "{section.section_id}-location")]/*'
        instructor_loc = By.XPATH, f'{table_xpath}//td[contains(@id, "{section.section_id}-instructors")]'
        return {
            'course': self.el_text_if_exists(course_loc),
            'label': self.el_text_if_exists(label_loc),
            'section_id': self.el_text_if_exists(section_id_loc),
            'schedules': [sch.upper() for sch in self.els_text_if_exist(schedules_loc) if sch],
            'locations': [loc for loc in self.els_text_if_exist(locations_loc) if loc],
            'instructors': self.el_text_if_exists(instructor_loc, 'Instructors:').split('\n'),
        }

    @staticmethod
    def section_add_button(section):
        return By.ID, f'section-{section.section_id}-link-btn'

    def click_add_section(self, course, section):
        app.logger.info(f'Clicking add button for section {section.section_id}')
        self.wait_for_element_and_click(self.section_add_button(section))
        time.sleep(1)

    def add_sections(self, course, sections):
        for section in sections:
            self.click_add_section(course, section)
        self.click_save_changes()

    def section_added_element(self, course, section):
        table_xpath = self.available_sections_table_xpath(course, section)
        return By.XPATH, f'{table_xpath}//td[contains(@id, "{section.section_id}-actions")]/div[contains(.,"Linked")]'

    @staticmethod
    def section_undo_delete_button(section):
        return By.ID, f'section-{section.section_id}-undo-unlink-btn'

    def click_undo_delete_section(self, section):
        app.logger.info(f'Clicking undo delete button for section {section.section_id}')
        self.wait_for_element_and_click(self.section_undo_delete_button(section))
        time.sleep(1)
