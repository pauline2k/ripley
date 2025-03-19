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


class EGradesPage(RipleyPages):

    BACK_TO_GRADEBOOK_LINK = By.LINK_TEXT, 'Back to Gradebook'
    HOW_TO_POST_GRADES_LINK = By.PARTIAL_LINK_TEXT, 'How do I post grades for an assignment?'
    COURSE_SETTINGS_BUTTON = By.ID, 'canvas-course-settings-href'

    PNP_CUTOFF_RADIO = By.ID, 'input-enable-pnp-conversion-true'
    NO_PNP_CUTOFF_RADIO = By.ID, 'input-enable-pnp-conversion-false'
    CUTOFF_SELECT = By.ID, 'select-pnp-grade-cutoff'
    SECTIONS_SELECT = By.ID, 'course-sections'
    DOWNLOAD_CURRENT_GRADES_BUTTON = By.ID, 'download-current-grades-button'
    DOWNLOAD_FINAL_GRADES_BUTTON = By.ID, 'download-final-grades-button'
    BCOURSES_TO_E_GRADES_LINK = By.PARTIAL_LINK_TEXT, 'From bCourses to E-Grades'

    NON_TEACHER_MSG = By.XPATH, '//div[text()="You must be a teacher in this bCourses course to export to E-Grades CSV."]'

    @staticmethod
    def embedded_tool_path(course_site):
        return f'/courses/#{course_site.site_id}/external_tools/{RipleyTools.E_GRADES.tool_id}'

    def hit_embedded_tool_url(self, course_site):
        self.navigate_to(f'{utils.canvas_base_url()}{self.embedded_tool_path(course_site)}')

    def load_embedded_tool(self, course_site):
        self.load_tool_in_canvas(self.embedded_tool_path(course_site))

    def click_course_settings_button(self, course_site):
        self.wait_for_page_and_click(self.COURSE_SETTINGS_BUTTON)
        self.when_url_contains(f'{utils.canvas_base_url()}/courses/{course_site.site_id}/settings',
                               utils.get_medium_timeout())

    def set_cutoff(self, cutoff):
        if cutoff:
            app.logger.info(f'Setting P/NP cutoff to {cutoff}')
            self.wait_for_select_and_click_option(self.CUTOFF_SELECT, cutoff)
        else:
            app.logger.info('Setting no P/NP cutoff')
            self.wait_for_element_and_click(self.NO_PNP_CUTOFF_RADIO)

    def choose_section(self, section):
        section_name = f'{section.course} {section.label}'
        utils.prepare_download_dir()
        self.wait_for_select_and_click_option(self.SECTIONS_SELECT, section_name)

    def download_current_grades(self, course_site, section, cutoff):
        app.logger.info(f'Downloading current grades for {course_site.course.code} {section.label}')
        file_name = f"egrades-current-{section.section_id}-{course_site.course.term.name.replace(' ', '-')}-*.csv"
        self.download_grades(course_site, section, file_name, opts={'cutoff': cutoff, 'final': False})

    def download_final_grades(self, course_site, section, cutoff):
        app.logger.info(f'Downloading final grades for {course_site.course.code} {section.label}')
        file_name = f"egrades-final-{section.section_id}-{course_site.course.term.name.replace(' ', '-')}-*.csv"
        return self.download_grades(course_site, section, file_name, opts={'cutoff': cutoff, 'final': True})

    def download_grades(self, course_site, section, file_name, opts):
        self.load_embedded_tool(course_site)
        self.click_continue()
        self.set_cutoff(opts['cutoff'])
        if len(course_site.course.sections) > 1:
            self.choose_section(section)
        time.sleep(1)
        el = self.DOWNLOAD_FINAL_GRADES_BUTTON if opts['final'] else self.DOWNLOAD_CURRENT_GRADES_BUTTON
        return self.download_csv(el)
