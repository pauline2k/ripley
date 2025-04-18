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
from teena.models.ripley_tool import RipleyTools
from teena.pages.ripley.ripley_pages import RipleyPages
from teena.test_utils import utils


class MailingListPage(RipleyPages):

    MAILING_LIST_LINK = By.LINK_TEXT, RipleyTools.MAILING_LIST.name
    NO_LIST_MSG = By.XPATH, '//div[text()="No Mailing List has been created for this site."]'
    CREATE_LIST_BUTTON = By.ID, 'btn-create-mailing-list'
    LIST_CREATED_MSG = By.XPATH, '//div[contains(., "A Mailing List has been created")]'
    LIST_ADDRESS = By.XPATH, '//div[@role="alert"]//strong'
    LIST_DUPE_EMAIL_MSG = By.XPATH, '//div[contains(., "is used by another bCourses site and is not available")]'

    @staticmethod
    def embedded_tool_path(course_site):
        return f'/courses/{course_site.site_id}/external_tools/#{RipleyTools.MAILING_LIST.value.tool_id}'

    def hit_embedded_tool_url(self, course_site):
        self.navigate_to(f'{utils.canvas_base_url()}{self.embedded_tool_path(course_site)}')

    def load_embedded_tool(self, course_site):
        app.logger.info(f'Loading embedded instructor Mailing List tool for course {course_site.site_id}')
        self.load_tool_in_canvas(self.embedded_tool_path(course_site))

    def click_create_list(self):
        app.logger.info('Clicking create-list button')
        self.wait_for_element_and_click(self.CREATE_LIST_BUTTON)

    def create_list(self):
        self.click_create_list()
        self.when_present(self.LIST_CREATED_MSG, utils.get_short_timeout())

    # WELCOME EMAIL

    WELCOME_EMAIL_LINK = By.ID, 'link-to-httpsberkeleyservicenowcomkb_viewdosysparm_articleKB0013900'
    EMAIL_SUBJECT_INPUT = By.ID, 'input-subject'
    EMAIL_BODY_TEXT_AREA = By.XPATH, '//div[@role="textbox"]'
    EMAIL_SAVE_BUTTON = By.ID, 'btn-save-welcome-email'
    EMAIL_ACTIVATION_TOGGLE = By.ID, 'toggle-welcome-email-active'
    EMAIL_ACTIVATION_DISABLED_MSG = By.XPATH, '//span[contains(., "You can activate the welcome email")]'
    EMAIL_PAUSED_MSG = By.XPATH, '//span[text()="Sending welcome emails is paused."]'
    EMAIL_ACTIVATED_MSG = By.XPATH, '//span[text()="Welcome email  activated."]'
    EMAIL_SUBJECT = By.ID, 'page-site-mailing-list-subject'
    EMAIL_BODY = By.ID, 'page-site-mailing-list-body'
    EMAIL_EDIT_BUTTON = By.ID, 'btn-edit-welcome-email'
    EMAIL_EDIT_CANCEL_BUTTON = By.ID, 'btn-cancel-welcome-email-edit'
    EMAIL_LOG_DOWNLOAD_BUTTON = By.ID, 'btn-download-sent-message-log'

    def enter_email_subject(self, subject):
        app.logger.info(f'Entering subject {subject}')
        self.wait_for_element_clear_and_send_keys(self.EMAIL_SUBJECT_INPUT, subject)

    def enter_email_body(self, body):
        app.logger.info(f'Entering body {body}')
        self.wait_for_element_clear_and_send_keys(self.EMAIL_BODY_TEXT_AREA, body)

    def click_save_email_button(self):
        app.logger.info('Clicking the save email button')
        self.wait_for_element_and_click(self.EMAIL_SAVE_BUTTON)
        self.when_visible(self.EMAIL_SUBJECT, utils.get_short_timeout())

    def click_edit_email_button(self):
        app.logger.info('Clicking the edit button')
        self.wait_for_element_and_click(self.EMAIL_EDIT_BUTTON)

    def click_cancel_edit_button(self):
        app.logger.info('Clicking the cancel email edit button')
        self.wait_for_element_and_click(self.EMAIL_EDIT_CANCEL_BUTTON)

    def click_activation_toggle(self):
        app.logger.info('Clicking email activation toggle')
        self.wait_for_element_and_click(self.EMAIL_ACTIVATION_TOGGLE)
        time.sleep(2)

    def download_email_csv(self):
        app.logger.info('Downloading mail audit CSV')
        return self.download_csv(self.EMAIL_LOG_DOWNLOAD_BUTTON)
