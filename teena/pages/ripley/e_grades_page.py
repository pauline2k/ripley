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

import csv
import time

from flask import current_app as app
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from teena.models.ripley_tool import RipleyTools
from teena.pages.ripley.ripley_pages import RipleyPages
from teena.test_utils import utils


class EGradesPage(RipleyPages):

    BACK_TO_GRADEBOOK_LINK = By.LINK_TEXT, 'Back to Gradebook'
    HOW_TO_ENABLE_GRADING_SCHEME_LINK = By.PARTIAL_LINK_TEXT, 'How do I enable a grading scheme for a course?'
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
        return f'/courses/{course_site.site_id}/external_tools/{RipleyTools.E_GRADES.value.tool_id}'

    def hit_embedded_tool_url(self, course_site):
        self.navigate_to(f'{utils.canvas_base_url()}{self.embedded_tool_path(course_site)}')

    def load_embedded_tool(self, course_site):
        self.load_tool_in_canvas(self.embedded_tool_path(course_site))

    def is_continue_aria_disabled(self):
        return self.element(self.CONTINUE_BUTTON).get_dom_attribute('aria-disabled') == 'true'

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

    def section_select_options(self):
        sel = Select(self.element(self.SECTIONS_SELECT))
        return [opt.text.strip() for opt in sel.options]

    def choose_section(self, section):
        section_name = f'{section.course} {section.label}'
        utils.prepare_download_dir()
        self.wait_for_select_and_click_option(self.SECTIONS_SELECT, section_name)

    def download_current_grades(self, course_site, section, cutoff=None):
        app.logger.info(f'Downloading current grades for {course_site.course.code} {section.label}')
        return self.download_grades(course_site, section, opts={'cutoff': cutoff, 'final': False})

    def download_final_grades(self, course_site, section, cutoff=None):
        app.logger.info(f'Downloading final grades for {course_site.course.code} {section.label}')
        return self.download_grades(course_site, section, opts={'cutoff': cutoff, 'final': True})

    def download_grades(self, course_site, section, opts):
        self.load_embedded_tool(course_site)
        self.click_continue()
        self.set_cutoff(opts['cutoff'])
        if len(course_site.course.sections) > 1:
            self.choose_section(section)
        time.sleep(1)
        el = self.DOWNLOAD_FINAL_GRADES_BUTTON if opts['final'] else self.DOWNLOAD_CURRENT_GRADES_BUTTON
        file_path = self.download_file(el, 'csv')
        time.sleep(1)
        e_grades = []
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            for r in reader:
                e_grades.append({
                    'sid': r['ID'],
                    'last_name': r['Name'].split(',')[0].strip().lower(),
                    'grade': r['Grade'],
                    'grading_basis': r['Grading Basis'],
                    'comment': r['Comments'],
                })
        return e_grades

    @staticmethod
    def csv_sids(e_grades):
        sids = [r['sid'] for r in e_grades]
        sids.sort()
        return sids

    @staticmethod
    def csv_names(e_grades):
        names = [r['last_name'] for r in e_grades]
        names.sort()
        return names

    @staticmethod
    def csv_grades(e_grades):
        grades = [r['grade'] for r in e_grades]
        grades.sort()
        return grades

    @staticmethod
    def csv_grading_bases(e_grades):
        grading_bases = [r['grading_basis'] for r in e_grades]
        grading_bases.sort()
        return grading_bases

    @staticmethod
    def expected_e_grade(letter_grades, grading_scheme, enrollment, cutoff):
        if grading_scheme in ['Letter Grade Scale', 'Letter Grades with +/-']:
            if enrollment.grading_basis == 'GRD':
                return enrollment.grade
            else:
                if cutoff:
                    passing = letter_grades.index(enrollment.grade) <= letter_grades.index(cutoff)
                    if enrollment.grading_basis in ['ESU', 'SUS']:
                        return 'S' if passing else 'U'
                    else:
                        return 'P' if passing else 'NP'
                else:
                    return enrollment.grade
        else:
            return enrollment.grade

    @staticmethod
    def expected_comment(enrollment):
        if enrollment.grading_basis in ['CPN', 'DPN', 'EPN', 'PNP']:
            return 'P/NP grade'
        elif enrollment.grading_basis in ['ESU', 'SUS']:
            return 'S/U grade'
        elif enrollment.grading_basis == 'CNC':
            return 'C/NC grade'
        else:
            return ''

    def expected_e_grades_row(self, letter_grades, grading_scheme, enrollment, cutoff):
        return {
            'sid': enrollment.student.sid,
            'last_name': enrollment.student.last_name.lower(),
            'grade': self.expected_e_grade(letter_grades, grading_scheme, enrollment, cutoff),
            'grading_basis': enrollment.grading_basis,
            'comment': self.expected_comment(enrollment),
        }

    def expected_e_grades(self, letter_grades, grading_scheme, enrollments, cutoff):
        e_grades = []
        for enrollment in enrollments:
            e_grades.append(self.expected_e_grades_row(letter_grades, grading_scheme, enrollment, cutoff))
        e_grades.sort(key=lambda e: e['sid'])
        return e_grades

    @staticmethod
    def actual_e_grades(e_grades, enrollments):
        grades = []
        enrollment_sids = [enrollment.student.sid for enrollment in enrollments]
        for e_grade in e_grades:
            if e_grade['sid'] in enrollment_sids:
                grades.append(e_grade)
        grades.sort(key=lambda e: e['sid'])
        return grades
