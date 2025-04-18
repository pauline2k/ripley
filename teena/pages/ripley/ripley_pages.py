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

from flask import current_app as app
from selenium.webdriver.common.by import By
from teena.pages.page import Page
from teena.test_utils import utils


class RipleyPages(Page):

    HEADER = By.XPATH, '//header'
    HEADER_MENU_BUTTON = By.XPATH, '//button[@aria-haspopup="menu"]'
    LOG_OUT_LINK = By.ID, 'log-out'

    def hide_header(self):
        self.when_present(self.HEADER, utils.get_medium_timeout())
        snippet = """const header = document.evaluate(
            "//header",
            document,
            null,
            XPathResult.FIRST_ORDERED_NODE_TYPE,
            null,
          ).singleNodeValue;
         header.style.display="none";"""
        self.driver.execute_script(snippet)

    def log_out(self):
        self.wait_for_element_and_click(self.HEADER_MENU_BUTTON)
        if 'Welcome. Please log in. | bCourses Support' not in self.title():
            self.wait_for_element_and_click(self.LOG_OUT_LINK)
        self.when_not_present(self.LOG_OUT_LINK, utils.get_short_timeout())

    def load_tool_in_canvas(self, path):
        self.navigate_to(f'{utils.canvas_base_url()}{path}')
        self.switch_to_canvas_iframe(utils.ripley_base_url())

    ERROR_MSG = By.ID, 'error-message'
    UNAUTH_MSG = By.XPATH, '//div[contains(., "Unauthorized") or contains(., "not authorized") or contains(., "Authorization check failed")]'
    SIS_IMPORT_ERROR = By.XPATH, '//div[text()="An error has occurred with your request. Please try again or contact bCourses support."]'

    MAINTENANCE_NOTICE = By.XPATH, '//div[contains(., "you may experience delays of up to 10 minutes")]'
    MAINTENANCE_DETAIL = By.XPATH, '//div[contains(., "bCourses performs scheduled maintenance every day")]'
    BCOURSES_SERVICE_LINK = By.ID, 'link-to-httpsrtlberkeleyeduservicesprogramsbcourses'

    def wait_for_unauthorized_msg(self):
        self.when_present(self.UNAUTH_MSG, utils.get_medium_timeout())

    def expand_maintenance_notice(self):
        self.wait_for_page_and_click(self.MAINTENANCE_NOTICE)
        self.when_visible(self.MAINTENANCE_DETAIL, utils.get_short_timeout())

    def hide_maintenance_notice(self):
        self.wait_for_page_and_click(self.MAINTENANCE_NOTICE)
        self.when_not_visible(self.MAINTENANCE_DETAIL, utils.get_short_timeout())

    CONTINUE_BUTTON = By.ID, 'continue-button'
    CANCEL_BUTTON = By.ID, 'cancel-button'

    def click_continue(self):
        app.logger.info('Clicking continue')
        self.wait_for_page_and_click(self.CONTINUE_BUTTON)

    def click_cancel(self, course_site):
        app.logger.info('Clicking cancel')
        self.wait_for_page_and_click(self.CANCEL_BUTTON)
        self.when_url_contains(f'{utils.canvas_base_url()}/courses/{course_site.site_id}/gradebook')
