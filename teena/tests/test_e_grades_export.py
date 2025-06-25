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
import pytest
from teena.config.teena_test_config import TeenaTestConfig
from teena.models.canvas_assignment import CanvasAssignment
from teena.models.ripley_tool import RipleyTools
from teena.models.section import Section, SectionEnrollment
from teena.test_utils import utils

test = TeenaTestConfig()
test.e_grades()
test_enrollment = SectionEnrollment({})
primary_section = Section({})


@pytest.mark.usefixtures('page_objects')
class TestSetup:

    def test_get_site_data(self):
        self.canvas_page.log_in(self.cal_net_page, test.admin.username, utils.get_admin_password())
        self.canvas_page.configure_single_site(test)
        prim = next(filter(lambda s: s.is_primary, test.course_site.sections))
        primary_section.course = prim.course
        primary_section.enrollments = prim.enrollments
        primary_section.label = prim.label
        primary_section.section_id = prim.section_id

    def test_e_grades_export_button_on_gradebook(self):
        self.canvas_page.load_gradebook(test.course_site)
        self.canvas_page.click_e_grades_export_button()
        self.e_grades_page.wait_for_title_contains(RipleyTools.E_GRADES.value.name)
        self.e_grades_page.when_present(self.e_grades_page.CANVAS_IFRAME, utils.get_medium_timeout())

    def test_create_un_graded_test_assignment(self):
        self.canvas_page.masquerade_as(test.course_site.course.teachers[0])
        ungraded = CanvasAssignment(title=test.test_id)
        self.canvas_page.set_grade_policy_manual(test.course_site)
        self.canvas_page.create_assignment(test.course_site, ungraded)


@pytest.mark.usefixtures('page_objects')
class TestNoGradingSchemeAndAssignmentUnPosted:

    def test_disable_grading_scheme(self):
        self.canvas_page.disable_grading_scheme(test.course_site)

    def test_course_settings_link(self):
        self.e_grades_page.load_embedded_tool(test.course_site)
        self.e_grades_page.click_course_settings_button(test.course_site)

    def test_how_post_grades_for_assignment_link(self):
        self.e_grades_page.load_embedded_tool(test.course_site)
        title = 'How do I post grades for an assignment'
        assert self.e_grades_page.is_external_link_valid(self.e_grades_page.HOW_TO_POST_GRADES_LINK, title)

    def test_no_continuing(self):
        self.e_grades_page.load_embedded_tool(test.course_site)
        self.e_grades_page.when_present(self.e_grades_page.CONTINUE_BUTTON, utils.get_medium_timeout())
        assert not self.e_grades_page.is_el_enabled(self.e_grades_page.CONTINUE_BUTTON)

    def test_cancel_e_grades(self):
        self.e_grades_page.click_cancel(test.course_site)


@pytest.mark.usefixtures('page_objects')
class TestGradingSchemeEnabledAndAssignmentUnPosted:

    def test_enable_grading_scheme(self):
        self.canvas_page.enable_grading_scheme(test.course_site)

    def test_course_settings_link(self):
        self.e_grades_page.load_embedded_tool(test.course_site)
        self.e_grades_page.click_course_settings_button(test.course_site)

    def test_how_post_grades_for_assignment_link(self):
        self.e_grades_page.load_embedded_tool(test.course_site)
        title = 'How do I post grades for an assignment'
        assert self.e_grades_page.is_external_link_valid(self.e_grades_page.HOW_TO_POST_GRADES_LINK, title)

    def test_allowed_to_continue(self):
        self.e_grades_page.load_embedded_tool(test.course_site)
        self.e_grades_page.click_continue()
        self.e_grades_page.when_present(self.e_grades_page.DOWNLOAD_FINAL_GRADES_BUTTON, utils.get_medium_timeout())

    def test_cancel_e_grades(self):
        self.e_grades_page.load_embedded_tool(test.course_site)
        self.e_grades_page.click_cancel(test.course_site)


@pytest.mark.usefixtures('page_objects')
class TestGradingSchemeEnabledAndNoMutedAssignment:

    def test_all_sections_available_for_selection(self):
        self.e_grades_page.load_embedded_tool(test.course_site)
        self.e_grades_page.click_continue()
        if len(test.course_site.sections) > 1:
            expected = [f'{s.course} {s.label}' for s in test.course_site.sections]
            expected.append('Choose...')
            expected.sort()
            visible = self.e_grades_page.section_select_options()
            visible.sort()
            utils.assert_equivalence(visible, expected)

    def test_pnp_selection_required(self):
        assert not self.e_grades_page.is_el_enabled(self.e_grades_page.DOWNLOAD_CURRENT_GRADES_BUTTON)
        assert not self.e_grades_page.is_el_enabled(self.e_grades_page.DOWNLOAD_FINAL_GRADES_BUTTON)


@pytest.mark.usefixtures('page_objects')
class TestCsvExport:

    def test_csv_content(self):
        expected_grades = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F', 'P', 'NP', 'S', 'U']
        expected_grading_bases = ['CPN', 'DPN', 'EPN', 'ESU', 'FRZ', 'GRD']
        e_grades = self.e_grades_page.download_final_grades(test.course_site, primary_section, cutoff='C-')
        utils.assert_equivalence(self.e_grades_page.csv_sids(e_grades), primary_section.enrolled_sids())
        utils.assert_equivalence(self.e_grades_page.csv_names(e_grades), primary_section.enrolled_last_names())
        assert not list(set(self.e_grades_page.csv_grades(e_grades)) - set(expected_grades))
        assert not list(set(self.e_grades_page.csv_grading_bases(e_grades)) - set(expected_grading_bases))


@pytest.mark.usefixtures('page_objects')
class TestDownloadCSVPerSection:

    def test_download_current_grades_primary_section(self):
        assert self.e_grades_page.download_current_grades(test.course_site, primary_section, cutoff='C-')

    def test_download_current_grades_secondary_section(self):
        seconds = [s for s in test.course_site.sections if not s.is_primary]
        if seconds:
            assert self.e_grades_page.download_current_grades(test.course_site, seconds[0], cutoff='C-')

    def test_download_final_grades_primary_section(self):
        assert self.e_grades_page.download_final_grades(test.course_site, primary_section, cutoff='C-')

    def test_download_final_grades_secondary_section(self):
        seconds = [s for s in test.course_site.sections if not s.is_primary]
        if seconds:
            assert self.e_grades_page.download_final_grades(test.course_site, seconds[0], cutoff='C-')


@pytest.mark.usefixtures('page_objects')
class TestFinalGradeOverride:

    def test_setup(self):
        # Find a site student enrollment with SID and usable grade for testing grade override
        self.canvas_page.stop_masquerading()
        self.canvas_page.load_users_page(test.course_site)
        site_enrollments = self.canvas_page.visible_student_enrollments(test.course_site, [primary_section])
        self.canvas_page.load_gradebook(test.course_site)
        for site_enrollment in site_enrollments:
            score = self.canvas_page.student_score(site_enrollment.student)
            if score and not score['un_posted']:
                test_enrollment.student = site_enrollment.student
                test_enrollment.grade = score['grade']
                break

    def test_grade_override_enabled(self):
        valid_grades = ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F']
        override_grade = next(filter(lambda g: g != test_enrollment.grade, valid_grades))
        self.canvas_page.load_gradebook(test.course_site)
        self.canvas_page.allow_grade_override()
        self.canvas_page.enter_override_grade(test.course_site, test_enrollment.student, override_grade)
        self.e_grades_page.load_embedded_tool(test.course_site)
        e_grades = self.e_grades_page.download_final_grades(test.course_site, primary_section)
        e_grades_row = next(filter(lambda r: r['sid'] == test_enrollment.student.sid, e_grades))
        utils.assert_equivalence(e_grades_row['grade'], override_grade)

    def test_grade_override_disabled(self):
        self.canvas_page.load_gradebook(test.course_site)
        self.canvas_page.disallow_grade_override()
        grades_are_final = self.canvas_page.are_grades_final(test.course_site)
        app.logger.info(f'Grades are final is {grades_are_final}')
        self.canvas_page.hit_escape()
        if grades_are_final:
            e_grades = self.e_grades_page.download_final_grades(test.course_site, primary_section)
        else:
            e_grades = self.e_grades_page.download_current_grades(test.course_site, primary_section)
        e_grades_row = next(filter(lambda r: r['sid'] == test_enrollment.student.sid, e_grades))
        utils.assert_equivalence(e_grades_row['grade'], test_enrollment.grade)


@pytest.mark.usefixtures('page_objects')
class TestUserToolAccess:

    def test_add_users(self):
        users_to_add = [test.lead_ta, test.ta, test.designer, test.reader, test.observer, test.student,
                        test.wait_list_student]
        self.canvas_page.load_users_page(test.course_site)
        self.canvas_page.click_find_person_to_add()
        for user in users_to_add:
            self.add_user_page.search(user.uid, 'CalNet UID')
            self.add_user_page.add_user_by_uid(user, primary_section)

    @pytest.mark.parametrize(argnames='user',
                             argvalues=[user for user in [test.canvas_admin, test.lead_ta]],
                             ids=[user.role for user in [test.canvas_admin, test.lead_ta]],
                             scope='function')
    def test_support_admin_has_access(self, user):
        self.canvas_page.masquerade_as(user, test.course_site)
        self.e_grades_page.load_embedded_tool(test.course_site)
        self.e_grades_page.click_continue()

    @pytest.mark.parametrize(argnames='user',
                             argvalues=[user for user in [test.ta, test.reader]],
                             ids=[user.role for user in [test.ta, test.reader]],
                             scope='function')
    def test_user_with_button_but_no_tool_access(self, user):
        self.canvas_page.masquerade_as(user, test.course_site)
        self.canvas_page.load_gradebook(test.course_site)
        self.canvas_page.click_e_grades_export_button()
        self.e_grades_page.switch_to_canvas_iframe()
        self.e_grades_page.wait_for_unauthorized_msg()

    @pytest.mark.parametrize(argnames='user',
                             argvalues=[user for user in [test.designer, test.observer, test.student,
                                                          test.wait_list_student]],
                             ids=[user.role for user in [test.designer, test.observer, test.student,
                                                         test.wait_list_student]],
                             scope='function')
    def test_user_with_no_tool_access(self, user):
        self.canvas_page.masquerade_as(user, test.course_site)
        self.e_grades_page.load_embedded_tool(test.course_site)
        self.e_grades_page.wait_for_unauthorized_msg()
