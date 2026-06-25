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

import json

from flask import current_app as app
from selenium.webdriver.common.by import By
from teena.pages.ripley.ripley_pages import RipleyPages
from teena.test_utils import utils


class ArchivalStatusPage(RipleyPages):

    PAGE_HEADING = By.XPATH, '//h1[.="View Course Retention Status"]'
    NO_COURSES_MSG = By.ID, 'archival-status-no-courses'
    SITE_ID_LINKS = By.XPATH, '//*[starts-with(@id, "archival-status-site-id-")]'

    def get_archival_status_api_feed(self):
        app.logger.info('Fetching archival status API feed')
        self.switch_to_default_content()
        self.navigate_to(f'{utils.ripley_base_url()}/api/canvas_site/archival_status')
        return json.loads(self.element((By.XPATH, '//body')).text)

    def wait_for_page_to_load(self):
        app.logger.info('Waiting for archival status page to load')
        self.when_present(self.PAGE_HEADING, utils.get_medium_timeout())

    def has_no_courses_message(self):
        return self.is_present(self.NO_COURSES_MSG)

    def visible_site_ids(self):
        return [el.text for el in self.elements(self.SITE_ID_LINKS)]

    def role_for_site(self, site_id):
        return self.element((By.ID, f'archival-status-role-{site_id}')).text

    def removal_date_for_site(self, site_id):
        return self.element((By.ID, f'archival-status-removal-date-{site_id}')).text
