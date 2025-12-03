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

import itertools

import pytest
from teena.config.teena_test_config import TeenaTestConfig
from teena.models.ripley_tool import RipleyTools
from teena.test_utils import ripley_utils, utils

test = TeenaTestConfig()
test.grade_distribution()
data_ct_threshold = ripley_utils.newt_small_cell_suppression()
valid_letter_grades = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F']


@pytest.mark.usefixtures('page_objects')
class TestSetup:

    def test_setup(self):
        self.canvas_page.log_in(self.cal_net_page, test.admin.username, utils.get_admin_password())
        self.canvas_page.add_ripley_tools([t.value for t in RipleyTools])


@pytest.mark.usefixtures('page_objects')
@pytest.mark.parametrize(argnames='site',
                         argvalues=test.course_sites,
                         ids=[f'{site.site_id} {site.term.sis_id}' for site in test.course_sites],
                         scope='class')
class TestSites:

    def test_load_site(self, site):
        self.newt_page.load_embedded_tool(site)

    # TODO: tests for variable text and UI elements


@pytest.mark.parametrize(argnames='tc',
                         argvalues=test.test_cases,
                         ids=[f'Site {tc.site.site_id}, term {tc.term.name}, UID {tc.instructor.uid}' for tc in test.test_cases],
                         scope='class')
class TestTermData:

    def test_masquerade(self, tc):
        tcs_grouped_by_site = [list(result) for key, result in itertools.groupby(test.test_cases, key=lambda t: t.site.site_id)]
        for tc_group in tcs_grouped_by_site:
            if tc == tc_group[0]:
                self.canvas_page.stop_masquerading()
                self.canvas_page.masquerade_as(tc.instructor, tc.site)
                self.newt_page.load_embedded_tool(tc.site)

    # Demographics

    def test_all_term_course_enrollments_mean_grade_points(self, tc):
        self.newt_page.select_demographic('Select Demographic')
        self.newt_page.select_statistic('Mean Grade Values')
        self.newt_page.expand_demographics_table()
        visible = self.newt_page.visible_demographics_term_data(tc.term)['ttl_stat']
        expected = self.newt_page.expected_mean_grade_points(tc.enrollments)
        utils.assert_equivalence(visible, expected)

    def test_all_term_course_enrollments_count(self, tc):
        visible = self.newt_page.visible_demographics_term_data(tc.term)['ttl_ct']
        expected = self.newt_page.expected_demographic_count(tc.enrollments)
        utils.assert_equivalence(visible, expected)

    def test_athlete_term_course_enrollments_count(self, tc):
        athlete_enrollments = []
        for enroll in tc.enrollments:
            if enroll.student.demographics.is_athlete and enroll.grade in valid_letter_grades:
                athlete_enrollments.append(enroll)
        if not self.newt_page.is_demographic_option_enabled('Student Athletes'):
            assert len(athlete_enrollments) < data_ct_threshold
        else:
            self.newt_page.select_demographic('Student Athletes')
            visible = self.newt_page.visible_demographics_term_data(tc.term)['sub_stat']
            expected = self.newt_page.expected_mean_grade_points(athlete_enrollments)
            utils.assert_equivalence(visible, expected)

    # TODO: Prior enrollment

    # TODO: User role access to tool
