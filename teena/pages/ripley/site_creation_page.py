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
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from teena.models.ripley_tool import RipleyTools
from teena.pages.ripley.ripley_pages import RipleyPages
from teena.test_utils import utils


class SiteCreationPage(RipleyPages):

    PAGE_HEADING = By.XPATH, '//h1[text()="Create a Site"]'
    GO_NEXT_BUTTON = By.ID, 'go-next-btn'

    def load_embedded_tool(self, user):
        app.logger.info('Loading embedded version of Create Course Site tool')
        self.load_tool_in_canvas(f'/users/{user.canvas_id}/external_tools/{RipleyTools.MANAGE_SITES.value.tool_id}')

    def wait_for_site_id(self, course_site):
        tries = utils.get_long_timeout()
        while tries > 0:
            try:
                tries -= 1
                self.when_url_contains(f'{utils.canvas_base_url()}/courses', 1)
                self.switch_to_default_content()
                break
            except TimeoutException:
                if self.is_present(self.SIS_IMPORT_ERROR):
                    app.logger.info('Site provisioning failed')
                    raise
                elif tries == 0:
                    app.logger.info('Timed out waiting for site provisioning')
                    raise
        course_site.site_id = self.current_url().replace(f'{utils.canvas_base_url()}/courses', '')
        app.logger.info(f'Site id is {course_site.site_id}')

    # Course site

    CREATE_COURSE_SITE_LINK = By.ID, 'create-course-site'
    COURSE_SITES_MSG = By.XPATH, '//div[contains(text(), "Set up course sites to communicate with and manage the work")]'
    NO_COURSE_SITES_MSG = By.XPATH, '//div[contains(text(), "you will need to be the official instructor of record")]'

    def click_create_course_site(self):
        app.logger.info('Selecting create course site and continue')
        self.wait_for_page_and_click(self.CREATE_COURSE_SITE_LINK)
        self.wait_for_element_and_click(self.GO_NEXT_BUTTON)

    # Project site

    CREATE_PROJECT_SITE_LINK = By.ID, 'create-project-site'
    PROJECT_HELP_LINK = By.ID, 'bcourses-project-sites-service-page'
    PROJECTS_LEARN_MORE_LINK = By.ID, 'berkeley-collaboration-services-information'

    def click_create_project_site(self):
        app.logger.info('Selecting create project site and continue')
        self.wait_for_page_and_click(self.CREATE_PROJECT_SITE_LINK)
        self.wait_for_element_and_click(self.GO_NEXT_BUTTON)

    # Manage official sections

    MANAGE_SECTIONS_LINK = By.ID, 'manage-official-sections'
    NO_MANAGING_SECTIONS_MSG = By.XPATH, '//span[contains(text(), "Sorry, we found neither")]'
    MANAGE_SECTIONS_SITE_INPUT = By.ID, 'canvas-site-id-input'
    MANAGE_SECTIONS_SITE_SELECT = By.ID, 'course-sections'

    def select_site_and_manage(self, course_site):
        app.logger.info(f'Selecting site {course_site.site_id} in {course_site.course.term.name} and continuing')
        self.wait_for_element_and_click(self.MANAGE_SECTIONS_LINK)
        self.wait_for_select_and_click_option(self.MANAGE_SECTIONS_SITE_SELECT, course_site.site_id)
        self.wait_for_element_and_click(self.GO_NEXT_BUTTON)

    def enter_site_and_manage(self, course_site):
        app.logger.info(f'Entering site {course_site.site_id} and continuing')
        self.wait_for_element_and_click(self.MANAGE_SECTIONS_LINK)
        self.wait_for_element_clear_and_send_keys(self.MANAGE_SECTIONS_SITE_INPUT, course_site.site_id)
        self.wait_for_element_and_click(self.GO_NEXT_BUTTON)
