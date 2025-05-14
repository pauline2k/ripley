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
from selenium.webdriver.support.select import Select
from teena.models.ripley_tool import RipleyTools
from teena.pages.ripley.ripley_pages import RipleyPages
from teena.test_utils import utils


class AddUserPage(RipleyPages):

    PAGE_HEADING = By.XPATH, '//h1[text()="Find a Person to Add"]'
    NO_RESULTS_MSG = By.XPATH, '//div[contains(text(), "Your search did not match anyone with a CalNet ID")]'
    TOO_MANY_RESULTS_MSG = By.XPATH, '//div[contains(text(), "Please refine your search to limit the number of results.")]'
    NO_UID_RESULTS_MSG = By.XPATH, '//div[contains(text(), "Your search did not match anyone with a CalNet ID")]'
    SUCCESS_MSG = By.ID, 'success-message'

    SEARCH_TERM = By.ID, 'search-text'
    SEARCH_BY_NAME = By.ID, 'radio-btn-name'
    SEARCH_BY_EMAIL = By.ID, 'radio-btn-email'
    SEARCH_BY_UID = By.ID, 'radio-btn-uid'
    SEARCH_BUTTON = By.ID, 'add-user-submit-search-btn'

    CAL_NET_DIR_LINK = By.ID, 'link-to-httpdirectoryberkeleyedu'
    CAL_NET_GUEST_ACCT_LINK = By.ID, 'link-to-httpsidcberkeleyeduguests'
    BCOURSES_HELP_LINK = By.ID, 'link-to-httpsberkeleyservicenowcomkb_viewdosysparm_articleKB0010842'

    RESULTS_TABLE = By.XPATH, '//h2[text()="User Search Results"]/following-sibling::div//table'
    RESULT_NAME = By.XPATH, '//td[contains(@id, "user-search-result-row-select")]'
    RESULT_UID = By.XPATH, '//td[contains(@id, "user-search-result-row-ldap-uid")]'
    RESULT_EMAIL = By.XPATH, '//td[contains(@id, "user-search-result-row-email")]'

    USER_ROLE = By.ID, 'user-role'
    COURSE_SECTION = By.ID, 'course-section'
    COURSE_SECTION_OPTS = By.XPATH, '//select[@id="course-section"]/option'
    ADD_USER_BUTTON = By.ID, 'add-user-btn'
    START_OVER_BUTTON = By.ID, 'start-over-btn'

    @staticmethod
    def embedded_tool_path(course_site):
        return f'/courses/{course_site.site_id}/external_tools/{RipleyTools.ADD_USER.value.tool_id}'

    def hit_embedded_tool_url(self, course_site):
        self.navigate_to(f'{utils.canvas_base_url()}{self.embedded_tool_path(course_site)}')

    def load_embedded_tool(self, course_site):
        app.logger.info('Loading embedded version of Find a Person to Add tool')
        self.load_tool_in_canvas(self.embedded_tool_path(course_site))

    # SEARCH

    def search(self, text, option):
        app.logger.info(f'Searching for "{text}" by {option}')
        if option == 'Last Name, First Name':
            loc = self.SEARCH_BY_NAME
        elif option == 'Email':
            loc = self.SEARCH_BY_EMAIL
        else:
            loc = self.SEARCH_BY_UID
        self.wait_for_element_and_click(loc)
        self.wait_for_element_remove_chars_send_keys(self.SEARCH_TERM, text)
        self.wait_for_element_and_click(self.SEARCH_BUTTON)

    def wait_for_no_results(self):
        self.when_present(self.NO_RESULTS_MSG, utils.get_short_timeout())

    def wait_for_too_many_results(self):
        self.when_present(self.TOO_MANY_RESULTS_MSG, utils.get_short_timeout())

    # Name

    def name_results(self):
        return self.els_text_if_exist(self.RESULT_NAME)

    def wait_for_name_results(self):
        self.when_present(self.RESULT_NAME, utils.get_short_timeout())

    # UID

    def uid_results(self):
        return self.els_text_if_exist(self.RESULT_UID)

    def wait_for_uid_results(self):
        self.when_present(self.RESULT_UID, utils.get_short_timeout())

    def wait_for_uid_result(self, uid):
        self.wait_for_uid_results()
        utils.assert_actual_includes_expected(self.uid_results(), uid)

    # Email

    def email_results(self):
        return self.els_text_if_exist(self.RESULT_EMAIL)

    def wait_for_email_results(self):
        self.when_present(self.RESULT_EMAIL, utils.get_short_timeout())

    # ADD USER

    @staticmethod
    def user_checkbox(user):
        return By.XPATH, f'//td[contains(., "{user.uid}")]/ancestor::tr//input[@name="selectedUser"]'

    def visible_user_role_options(self):
        self.when_visible(self.USER_ROLE, utils.get_short_timeout())
        sel = Select(self.element(self.USER_ROLE))
        opts = sel.options
        return [opt.get_dom_attribute('value') for opt in opts]

    def visible_section_options(self):
        self.when_visible(self.COURSE_SECTION, utils.get_short_timeout())
        return self.els_text_if_exist(self.COURSE_SECTION_OPTS)

    def add_user_by_uid(self, user, section=None):
        app.logger.info(f'Adding UID {user.uid} with role {user.role} to section {section.label if section else None}')
        self.wait_for_page_and_click(self.user_checkbox(user))
        if section:
            opt = section.sis_id if section.sis_id else f'{section.course} {section.label}'
            self.wait_for_select_and_click_option(self.COURSE_SECTION, opt)
        self.wait_for_select_and_click_option(self.USER_ROLE, user.role)
        self.wait_for_element_and_click(self.ADD_USER_BUTTON)
        self.when_visible(self.SUCCESS_MSG, utils.get_medium_timeout())
