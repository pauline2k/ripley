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
from selenium.webdriver.support.select import Select
from teena.models.ripley_tool import RipleyTools
from teena.pages.ripley.ripley_pages import RipleyPages
from teena.test_utils import utils


class RosterPhotosPage(RipleyPages):

    ROSTER_PHOTOS_LINK = By.LINK_TEXT, RipleyTools.ROSTER_PHOTOS.value.name

    SEARCH_INPUT = By.ID, 'roster-search'
    SECTION_SELECT = By.ID, 'section-select'
    EXPORT_ROSTER_LINK = By.ID, 'download-csv'
    PRINT_ROSTER_LINK = By.ID, 'print-roster'
    WAIT_FOR_LOAD_MSG = By.XPATH, '//*[text()="You can print when student images have loaded."]'

    NO_ACCESS_MSG = By.XPATH, '//div[text()="You must be a teacher in this bCourses course to view official student rosters."]'

    ROSTER_PHOTO = By.XPATH, '//img[contains(@src, "/cal1card-data/photos/")]'
    ROSTER_PHOTO_PLACEHOLDER = By.XPATH, '//img[contains(@src, "photo_unavailable")]'
    ROSTER_SID = By.XPATH, '//div[contains(@id, "student-id-")]'

    @staticmethod
    def embedded_tool_path(course_site):
        return f'/courses/{course_site.site_id}/external_tools/{RipleyTools.ROSTER_PHOTOS.value.tool_id}'

    def hit_embedded_tool_url(self, course_site):
        self.navigate_to(f'{utils.canvas_base_url()}{self.embedded_tool_path(course_site)}')

    def load_embedded_tool(self, course_site):
        app.logger.info('Loading embedded version of Roster Photos tool')
        self.load_tool_in_canvas(self.embedded_tool_path(course_site))

    def click_roster_photos_link(self):
        app.logger.info('Clicking Roster Photos link')
        self.wait_for_page_and_click(self.ROSTER_PHOTOS_LINK)
        self.switch_to_canvas_iframe(utils.ripley_base_url())

    def wait_for_photos_to_load(self):
        self.when_not_visible(self.WAIT_FOR_LOAD_MSG, utils.get_medium_timeout())
        self.when_present(self.ROSTER_PHOTO, utils.get_short_timeout())

    def wait_for_placeholder_count(self, expected_ct):
        tries = utils.get_short_timeout()
        while tries > 0:
            try:
                tries -= 1
                time.sleep(1)
                assert len(self.elements(self.ROSTER_PHOTO_PLACEHOLDER)) >= expected_ct
                break
            except AssertionError:
                if tries == 0:
                    app.logger.info(
                        f'Expected {expected_ct} photos, got {len(self.elements(self.ROSTER_PHOTO_PLACEHOLDER))}')
                    raise

    def section_options(self):
        sel = Select(self.element(self.SECTION_SELECT))
        return [opt.text for opt in sel.options]

    def filter_by_string(self, string):
        app.logger.info(f'Filtering roster by {string}')
        self.wait_for_element_remove_and_type_chars(self.SEARCH_INPUT, string)
        time.sleep(1)

    def filter_by_section(self, section):
        app.logger.info(f'Filtering roster by section {section.course} {section.label}')
        self.wait_for_select_and_click_option(self.SECTION_SELECT, f'{section.course} {section.label}')
        time.sleep(1)

    def click_student_profile_link(self, course_site, student):
        loc = By.XPATH, f'//a[contains(@href, "{course_site.site.id}/profile/{student.canvas_id}")]'
        self.wait_for_element_and_click(loc)
        self.when_present((By.XPATH, f'//h1[contains(text(), "{student.full_name}")]'), utils.get_short_timeout())

    def export_roster(self, course_site):
        app.logger.info(f'Downloading roster CSV for course site {course_site.site_id}')
        parsed = self.download_csv(self.EXPORT_ROSTER_LINK)
        return [r['Student ID'] for r in parsed]

    def all_sids(self):
        return self.els_text_if_exist(self.ROSTER_SID, 'Student ID:')
