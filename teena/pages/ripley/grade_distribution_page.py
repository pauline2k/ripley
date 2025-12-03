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
import math
import time

from flask import current_app as app
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from teena.models.ripley_tool import RipleyTools
from teena.pages.ripley.ripley_pages import RipleyPages
from teena.test_utils import ripley_utils
from teena.test_utils import utils


class GradeDistributionPage(RipleyPages):

    PAGE_HEADING = By.XPATH, '//h1[contains(., "Grade Distribution")]'
    SORRY_NOT_AUTH_MSG = By.XPATH, '//div[text()="Sorry, you are not authorized to use this tool."]'
    NO_GRADES_MSG = By.XPATH, '//*[text()="No data available until final grades are returned."]'
    NO_GRADE_DIST_MSG = By.XPATH, '//div[contains(text()="This course does not meet the requirements")]'
    TOOLTIP_KEY = By.XPATH, '//div[@class="chart-tooltip-key"]'
    TOOLTIP_NAME = By.XPATH, '//div[@class="chart-tooltip-name"]'

    @staticmethod
    def embedded_tool_path(course_site):
        return f'/courses/{course_site.site_id}/external_tools/{RipleyTools.NEWT.value.tool_id}'

    def hit_embedded_tool_url(self, course_site):
        self.navigate_to(f'{utils.canvas_base_url()}{self.embedded_tool_path(course_site)}')

    def load_embedded_tool(self, course_site):
        app.logger.info('Loading embedded version of Grade Distribution tool')
        self.load_tool_in_canvas(self.embedded_tool_path(course_site))

    # Demographics

    DEMOGRAPHICS_HEADING = By.XPATH, '//h2[text()="Grade Distribution by Demographics"]'
    DEMOGRAPHICS_SELECT = By.ID, 'grade-distribution-demographics-select'
    STATISTICS_SELECT = By.ID, 'grade-distribution-statistic-select'
    DEMOGRAPHICS_TABLE_TOGGLE = By.ID, 'grade-distribution-demographics-show-btn'
    DEMOGRAPHICS_TABLE = By.ID, 'grade-distribution-demo-table'
    DEMOGRAPHICS_TABLE_ROW = By.XPATH, '//tr[contains(@id, "grade-distribution-demo-table-row")]'

    def select_demographic(self, demographic):
        app.logger.info(f'Selecting demographic {demographic}')
        self.wait_for_select_and_click_option(self.DEMOGRAPHICS_SELECT, demographic)
        time.sleep(utils.get_click_sleep())

    def is_demographic_option_enabled(self, demographic):
        return self.is_el_enabled((By.XPATH, f'//option[contains(text(), "{demographic}")]'))

    def select_statistic(self, statistic):
        app.logger.info(f'Selecting statistic {statistic}')
        self.wait_for_select_and_click_option(self.STATISTICS_SELECT, statistic)
        time.sleep(utils.get_click_sleep())

    def expand_demographics_table(self):
        if self.is_visible(self.DEMOGRAPHICS_TABLE):
            app.logger.info('Demographics table is already expanded')
        else:
            app.logger.info('Expanding demographics data table')
            self.wait_for_element_and_click(self.DEMOGRAPHICS_TABLE_TOGGLE)
            self.when_visible(self.DEMOGRAPHICS_TABLE, 2)

    def visible_demographic_row_ct(self):
        return len(self.elements(self.DEMOGRAPHICS_TABLE_ROW))

    @staticmethod
    def expected_demographic_count(enrollments):
        if enrollments:
            count = len(enrollments)
            config = ripley_utils.newt_small_cell_suppression()
            return 'No data' if 1 <= count < config else str(count)
        else:
            return 'No data'

    @staticmethod
    def grades_to_grade_points(enrollments):
        valid_grades = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F']
        grades = [e.grade for e in enrollments if e.grade in valid_grades]
        grade_points = []
        for grade in grades:
            if grade in ['A+', 'A']:
                grade_points.append(4.0)
            elif grade == 'A-':
                grade_points.append(3.7)
            elif grade == 'B+':
                grade_points.append(3.3)
            elif grade == 'B':
                grade_points.append(3.0)
            elif grade == 'B-':
                grade_points.append(2.7)
            elif grade == 'C+':
                grade_points.append(2.3)
            elif grade == 'C':
                grade_points.append(2.0)
            elif grade == 'C-':
                grade_points.append(1.7)
            elif grade == 'D+':
                grade_points.append(1.3)
            elif grade == 'D':
                grade_points.append(1.0)
            elif grade == 'D-':
                grade_points.append(0.7)
            else:
                grade_points.append(0)
        return grade_points

    def expected_mean_grade_points(self, enrollments):
        if len(enrollments) >= ripley_utils.newt_small_cell_suppression():
            grades = self.grades_to_grade_points(enrollments)
            if grades:
                avg = round((sum(grades) / len(grades)), 1)
                return str(math.floor(avg) if math.floor(avg) == avg else avg)
            else:
                return 'No data'
        else:
            return 'No data'

    def expected_median_grade_points(self, enrollments):
        grades = self.grades_to_grade_points(enrollments)
        if grades:
            grades.sort()
            count = len(grades)
            if count % 2 == 0:
                bottom = grades[:(int(count / 2))]
                top = grades[int((count / 2)):]
                med = (bottom[-1] + top[0]) / 2
            else:
                med = grades[math.floor(count / 2)]
            return str(math.floor(med) if math.floor(med) == med else med)
        else:
            return 'No data'

    def visible_demographics_term_data(self, term):
        time.sleep(utils.get_click_sleep())
        xpath = f'//tr[contains(@id, "grade-distribution-demo-table-row")][contains(., "{term.name}")]'
        try:
            self.when_visible((By.XPATH, xpath), 10)
        except TimeoutException:
            pass
        data = {
            'term': term.name,
            'ttl_stat': self.el_text_if_exists((By.XPATH, f'{xpath}/td[2]')),
            'ttl_ct': self.el_text_if_exists((By.XPATH, f'{xpath}/td[3]')),
            'sub_stat': self.el_text_if_exists((By.XPATH, f'{xpath}/td[4]')),
            'sub_ct': self.el_text_if_exists((By.XPATH, f'{xpath}/td[5]')),
        }
        app.logger.info(f'Visible data {data}')
        return data

    # Prior enrollments

    PRIOR_ENROLLMENT_HEADING = By.XPATH, '//h2[text()="Grade Distribution by Prior Enrollment"]'
    PRIOR_ENROLLMENT_SELECT = By.XPATH, '//select[contains(@class, "grade-dist-enroll-term-select")]'
    PRIOR_ENROLLMENT_COURSE_INPUT = By.ID, 'grade-distribution-enrollment-course-search'
    PRIOR_ENROLLMENT_COURSE_ADD_BUTTON = By.ID, 'grade-distribution-enroll-add-class-btn'
    PRIOR_ENROLLMENT_TABLE_TOGGLE = By.ID, 'grade-distribution-enrollments-show-btn'
    PRIOR_ENROLLMENT_TABLE = By.ID, 'grade-distribution-enroll-table'

    def select_prior_enrollment_term(self, term):
        app.logger.info(f'Selecting prior enrollment {term.name}')
        self.wait_for_select_and_click_option(self.PRIOR_ENROLLMENT_SELECT, term.name)
        time.sleep(utils.get_click_sleep())

    def expand_prior_enrollment_table(self):
        if self.is_visible(self.PRIOR_ENROLLMENT_TABLE):
            app.logger.info('Prior enrollment table is already visible')
        else:
            app.logger.info('Expanding prior enrollment data table')
            self.wait_for_element_and_click(self.PRIOR_ENROLLMENT_TABLE_TOGGLE)
            self.when_visible(self.PRIOR_ENROLLMENT_TABLE, 1)

    def choose_prior_enrollment_course(self, course_code):
        app.logger.info(f'Entering course name {course_code}')
        self.wait_for_element_clear_and_send_keys(self.PRIOR_ENROLLMENT_COURSE_INPUT, course_code)
        self.hit_tab()
        self.wait_for_element_and_click(self.PRIOR_ENROLLMENT_COURSE_ADD_BUTTON)
        self.when_present(self.prior_enrollments_msg(course_code), utils.get_medium_timeout())

    @staticmethod
    def prior_enrollments_msg(course_code):
        return By.XPATH, f'//span[contains(., "Students Who Have Taken {course_code} to Overall Class")]'

    @staticmethod
    def no_prior_enrollments_msg(course, prior_course_code):
        return (By.XPATH,
                f'//span[contains(., "No {course.code} {course.term.name} students were previously enrolled in {prior_course_code}")]')

    @staticmethod
    def prior_enrollment_data_heading(prior_course_code):
        return By.XPATH, f'//span[contains(., "Students Who Have Taken {prior_course_code} to Overall Class")]'

    @staticmethod
    def expected_grade_pct(self, grade_count, ttl_count):
        app.logger.info(f'Grade count is {grade_count}, Total count is {ttl_count}')
        if ttl_count:
            result = round((grade_count / ttl_count), 3) * 100
            return f'{math.floor(result) if math.floor(result) == result else result}%'
        else:
            return '0%'

    def visible_prior_enroll_grade_data(self, grade):
        time.sleep(utils.get_click_sleep())
        app.logger.info(f'Checking grade {grade}')
        xpath = f'//td[text()="{grade}"]'
        self.when_visible((By.XPATH, xpath), utils.get_short_timeout())
        data = {
            'grade': grade,
            'ttl_pct': self.el_text_if_exists((By.XPATH, f'{xpath}/td[1]')),
            'ttl_ct': self.el_text_if_exists((By.XPATH, f'{xpath}/td[2]')),
            'sub_pct': self.el_text_if_exists((By.XPATH, f'{xpath}/td[3]')),
            'sub_ct': self.el_text_if_exists((By.XPATH, f'{xpath}/td[4]')),
        }
        app.logger.info(f'Visible data {data}')
        return data
