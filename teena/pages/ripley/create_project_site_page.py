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
from teena.pages.ripley.course_sections_tables import CourseSectionsTables
from teena.pages.ripley.site_creation_page import SiteCreationPage


class CreateProjectSitePage(CourseSectionsTables, SiteCreationPage):

    SITE_NAME_INPUT = By.ID, 'page-create-project-site-name'
    CREATE_SITE_BUTTON = By.ID, 'create-project-site-button'
    CANCEL_PROJECT_SITE_BUTTON = By.ID, 'cancel-and-return-to-site-creation'

    def cancel_project_site(self):
        app.logger.info('Canceling project site')
        self.wait_for_element_and_click(self.CANCEL_PROJECT_SITE_BUTTON)

    def enter_site_name(self, name):
        app.logger.info(f'Entering project site name {name}')
        self.wait_for_element_clear_and_send_keys(self.SITE_NAME_INPUT, name)

    def create_project_site(self, name):
        app.logger.info('Creating a project site')
        self.enter_site_name(name)
        self.wait_for_element_and_click(self.CREATE_SITE_BUTTON)
