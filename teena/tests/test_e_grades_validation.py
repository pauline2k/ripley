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

import pytest
from teena.config.teena_test_config import TeenaTestConfig
from teena.models.section import Section, SectionEnrollment
from teena.test_utils import utils

test = TeenaTestConfig()
test.e_grades()
test_enrollments = [SectionEnrollment({})] * utils.e_grades_student_count()
primary_section = Section({})
letter_grades = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F']
grading_schemes = ['Letter Grade Scale', 'Letter Grades with +/-', 'Pass/No Pass', 'Satisfactory/Unsatisfactory']


@pytest.mark.usefixtures('page_objects')
class TestSetup:

    def test_get_site_data(self):
        self.canvas_page.log_in(self.cal_net_page, test.admin.username, utils.get_admin_password())
        self.canvas_page.configure_single_site(test)
        test.course_site.are_grades_final = self.canvas_page.are_grades_final(test.course_site)
        prim = next(filter(lambda s: s.is_primary, test.course_site.sections))
        primary_section.course = prim.course
        primary_section.enrollments = prim.enrollments
        primary_section.label = prim.label
        primary_section.section_id = prim.section_id

    def test_get_test_students(self):
        self.canvas_page.load_users_page(test.course_site)
        site_enrollments = self.canvas_page.visible_student_enrollments(test.course_site, [primary_section])
        self.canvas_page.load_gradebook(test.course_site)
        count = 0
        for site_enrollment in site_enrollments:
            score = self.canvas_page.student_score(site_enrollment.student)
            if score and not score['un_posted']:
                test_enrollments[count] = site_enrollment
                count += 1
                if count == utils.e_grades_student_count():
                    break


@pytest.mark.usefixtures('page_objects')
@pytest.mark.parametrize(argnames='scheme',
                         argvalues=grading_schemes,
                         ids=grading_schemes,
                         scope='class')
class TestGradingScheme:

    def test_set_scheme(self, scheme):
        self.canvas_page.enable_grading_scheme(test.course_site)
        self.canvas_page.set_grading_scheme(scheme)

    def test_get_gradebook_scores(self, scheme):
        self.canvas_page.load_gradebook(test.course_site)
        for enrollment in [e for e in test_enrollments if e.student]:
            enrollment.grade = self.canvas_page.student_score(enrollment.student)['grade']

    def test_e_grades_export_with_cutoff(self, scheme):
        cutoff = 'C'
        if test.course_site.are_grades_final:
            e_grades = self.e_grades_page.download_final_grades(test.course_site, primary_section, cutoff)
        else:
            e_grades = self.e_grades_page.download_current_grades(test.course_site, primary_section, cutoff)
        enrollments = [e for e in test_enrollments if e.student]
        utils.assert_equivalence(self.e_grades_page.actual_e_grades(e_grades, enrollments),
                                 self.e_grades_page.expected_e_grades(letter_grades, scheme, enrollments, cutoff))

    def test_e_grades_export_sans_cutoff(self, scheme):
        cutoff = None
        if test.course_site.are_grades_final:
            e_grades = self.e_grades_page.download_final_grades(test.course_site, primary_section, cutoff)
        else:
            e_grades = self.e_grades_page.download_current_grades(test.course_site, primary_section, cutoff)
        enrollments = [e for e in test_enrollments if e.student]
        utils.assert_equivalence(self.e_grades_page.actual_e_grades(e_grades, enrollments),
                                 self.e_grades_page.expected_e_grades(letter_grades, scheme, enrollments, cutoff))
