"""
Copyright ©2026. The Regents of the University of California (Regents). All Rights Reserved.

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

from selenium.webdriver.common.by import By
from teena.pages.canvas.canvas_api_page import CanvasApiPage
from teena.test_utils import utils

class CanvasProfilePage(CanvasApiPage):
    PRONOUNS_DISPLAY = By.ID, 'pronouns'
    PRONOUNS_CUSTOM_DESCRIPTION = By.XPATH, '//*[@id="pronouns"]/following-sibling::span[contains(@class, "data_description")]'
    PRONOUNS_HELP_LINK = By.XPATH, '//*[@id="pronouns"]/following-sibling::span//a'

    def load_user_profile(self):
        """Navigate to the fixed profile settings URL."""
        self.navigate_to(f'{utils.canvas_base_url()}/profile/settings')
        self.when_present(self.PRONOUNS_DISPLAY, utils.get_short_timeout())
        time.sleep(2)

    def is_pronouns_section_present(self):
        """Return True if the pronouns ID exists on the page."""
        return self.is_present(self.PRONOUNS_DISPLAY)

    def get_description_text(self):
        """Return the text of the custom instructional span."""
        return self.element(self.PRONOUNS_CUSTOM_DESCRIPTION).text.replace('\n', ' ').strip()
