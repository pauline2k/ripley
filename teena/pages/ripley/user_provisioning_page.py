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
from teena.models.ripley_tool import RipleyTools
from teena.pages.ripley.ripley_pages import RipleyPages
from teena.test_utils import utils


class UserProvisioningPage(RipleyPages):

    UID_INPUT = By.ID, 'page-user-provision-uid-list'
    IMPORT_BUTTON = By.ID, 'user-provision-import-btn'
    SUCCESS_MSG = By.XPATH, '//div[contains(., "Success")]'
    NON_NUMERIC_MSG = By.XPATH, '//div[contains(., "The following items in your list are not numeric:")]'
    MAX_INPUT_MSG = By.XPATH, '//div[contains(text(), "Maximum")]'

    def load_embedded_tool(self):
        app.logger.info('Loading embedded version of the User Provisioning tool')
        tool_id = RipleyTools.USER_PROVISIONING.tool_id
        self.load_tool_in_canvas(f'/accounts/{utils.canvas_root_acct()}/external_tools/{tool_id}')

    def enter_uids_and_submit(self, uids_string):
        app.logger.info(f'Entering string to import: {uids_string}')
        self.wait_for_element_and_send_keys(self.UID_INPUT, uids_string)
        self.wait_for_element_and_click(self.IMPORT_BUTTON)
