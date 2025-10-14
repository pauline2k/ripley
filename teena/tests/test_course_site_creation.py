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

import re

import pytest
from teena.config.teena_test_config import TeenaTestConfig
from teena.test_utils import ripley_utils
from teena.test_utils import utils

test = TeenaTestConfig()
test.course_site_creation()


@pytest.mark.usefixtures('page_objects')
class TestSetup:

    def test_setup(self):
        self.canvas_page.log_in(self.cal_net_page, test.admin.username, utils.get_admin_password())
        self.canvas_page.configure_multiple_sites(test)


@pytest.mark.usefixtures('page_objects')
@pytest.mark.parametrize(argnames='site',
                         argvalues=[site for site in test.course_sites],
                         ids=[f'{site.course.term.sis_id}-{site.course.code}' for site in test.course_sites],
                         scope='class')
class TestCourseSiteCreation:

    def test_load_tool(self, site):
        self.canvas_page.stop_masquerading()
        self.canvas_page.set_canvas_ids([site.course.teachers[0]])
        if site.create_site_workflow == 'masq':
            self.canvas_page.masquerade_as(site.course.teachers[0])
        else:
            self.canvas_page.load_homepage()
        self.canvas_page.click_manage_sites()
        self.site_creation_page.click_create_course_site()

    def test_cancel_button(self, site):
        if site.create_site_workflow == 'masq':
            self.create_course_site_page.click_cancel_site_creation()
            self.site_creation_page.click_create_course_site()

    def test_search_for_course(self, site):
        self.create_course_site_page.search_for_course(site)

    def test_multi_section_help_info(self, site):
        if site.create_site_workflow in ['masq', 'uid']:
            assert self.create_course_site_page.is_present(self.create_course_site_page.NEED_HELP)
        else:
            assert not self.create_course_site_page.is_present(self.create_course_site_page.NEED_HELP)

    def test_help_link(self, site):
        if site.create_site_workflow in ['masq', 'uid']:
            assert self.create_course_site_page.is_external_link_valid(
                locator=self.create_course_site_page.INSTR_MODE_LINK,
                expected_page_title='IT - How do I create a Course Site?',
                switch_to_canvas_iframe=True)

    def test_right_sections_are_displayed(self, site):
        if site.create_site_workflow == 'ccn':
            self.create_course_site_page.expand_all_available_sections()
            expected = [section.section_id for section in site.sections]
        else:
            self.create_course_site_page.expand_available_course_sections(site.course, site.course.sections[0])
            expected = [section.section_id for section in site.course.sections]
        expected.sort()
        visible = self.create_course_site_page.visible_section_ids()
        visible.sort()
        utils.assert_equivalence(visible, expected)

    def test_select_sections(self, site):
        self.create_course_site_page.select_sections(site.sections)
        self.create_course_site_page.click_next()

    def test_default_site_name(self, site):
        visible_default_name = self.create_course_site_page.el_value(self.create_course_site_page.SITE_NAME_INPUT)
        expected_name = f'{site.course.title} ({site.course.term.name})'
        utils.assert_equivalence(visible_default_name, expected_name)

    def test_default_site_abbreviation(self, site):
        visible_default_abbrev = self.create_course_site_page.el_value(self.create_course_site_page.SITE_ABBREVIATION)
        expected_abbrev = site.course.code
        utils.assert_actual_includes_expected(visible_default_abbrev, expected_abbrev)

    def test_name_and_abbreviation_required(self, site):
        if site == test.course_sites[0]:
            self.create_course_site_page.enter_site_name('')
            self.create_course_site_page.when_present(self.create_course_site_page.SITE_NAME_ERROR, 1)
            assert not self.create_course_site_page.is_el_enabled(self.create_course_site_page.CREATE_SITE_BUTTON)
            self.create_course_site_page.enter_site_abbreviation('')
            self.create_course_site_page.when_present(self.create_course_site_page.SITE_ABBREVIATION_ERROR, 1)

    def test_go_back(self, site):
        if site == test.course_sites[0]:
            self.create_course_site_page.click_go_back()
            self.create_course_site_page.click_next()

    def test_create_site(self, site):
        site.title = self.create_course_site_page.enter_site_titles(site.course)
        self.create_course_site_page.click_create_site()
        self.create_course_site_page.wait_for_site_id(site)
        assert site.site_id

    # CHECK COURSE SITE CONTENT - MEMBERSHIP, TOOL CONTENT, CUSTOMIZATIONS
    # With the admin create-site-by-ccns workflow, the course instructor is not added to the site right away
    # So the following tests verify site content with the create-site-by-uid or masquerade-as sites

    def test_publish_new_site(self, site):
        if site.site_id and site.create_site_workflow in ['masq', 'uid']:
            self.canvas_page.masquerade_as(site.course.teachers[0])
            self.canvas_page.publish_course_site(site)

    def test_no_overriding_dept_templates(self, site):
        if site.site_id and site.create_site_workflow in ['masq', 'uid']:
            site_has_default_template = self.canvas_page.is_present(self.canvas_page.RECENT_ACTIVITY_HEADING)
            if site.has_template:
                assert not site_has_default_template
            else:
                assert site_has_default_template

    def test_roster_contains_all_expected_members(self, site):
        if site.site_id and site.create_site_workflow in ['masq', 'uid']:
            expected_instructors = ripley_utils.expected_instr_section_data(site)
            expected_students = ripley_utils.expected_student_section_data(site)
            expected_members = expected_instructors + expected_students
            expected_members.sort(key=lambda m: [m['uid'], m['section_id']])

            # The user SIS import could still be churning, so wait for the Student count to meet the expected count
            student_count = {
                'role': 'Student',
                'count': len([s for s in expected_students if s['role'] == 'student']),
            }
            self.canvas_page.load_users_page(site)
            self.canvas_page.wait_for_enrollment_import(site,
                                                        roles=['Student'],
                                                        expected_count_per_role=[student_count])

            # Then verify the user, role, and section data for all members
            visible_members = self.canvas_page.visible_uids_with_role_and_section_id(site)
            utils.assert_equivalence(visible_members, expected_members)

    def test_roster_shows_instruction_mode(self, site):
        if site.site_id and site.create_site_workflow in ['masq', 'uid']:
            visible_modes = set(self.canvas_page.visible_instruction_modes())
            expected_modes = {'In Person', 'Online', 'Hybrid', 'Flexible', 'Remote', 'Web-based'}
            assert visible_modes.issubset(expected_modes)

    def test_roster_photos_link(self, site):
        if site.site_id and site.create_site_workflow in ['masq', 'uid']:
            assert self.canvas_page.is_present(self.roster_photos_page.ROSTER_PHOTOS_LINK)

    def test_roster_photos_sections(self, site):
        if site.site_id and site.create_site_workflow in ['masq', 'uid']:
            self.roster_photos_page.load_embedded_tool(site)
            expected_sections = [f'{section.course} {section.label}' for section in site.sections]
            expected_sections.sort()
            actual_sections = self.roster_photos_page.section_options()
            actual_sections.remove('All Sections')
            utils.assert_equivalence(actual_sections, expected_sections)

    def test_ta_teachers_can_manage_sections(self, site):
        if site.site_id and site.create_site_workflow in ['masq', 'uid']:
            if ripley_utils.get_course_instructor_roles(site.course, site.course.teachers[0]) == ['TNIC']:
                self.site_creation_page.load_embedded_tool(site.course.teachers[0])
                self.site_creation_page.select_site_and_manage(site)
                self.official_sections_page.when_visible(self.official_sections_page.STATIC_VIEW_SECTIONS_TABLE,
                                                         utils.get_medium_timeout())
                self.official_sections_page.when_visible(self.official_sections_page.EDIT_SECTIONS_BUTTON, 1)

    def test_grade_distribution_hidden(self, site):
        if site.site_id and site.create_site_workflow in ['masq', 'uid']:
            assert self.canvas_page.is_grade_distribution_hidden(site)

    def test_conferences_navigation_hidden(self, site):
        if site.site_id and site.create_site_workflow in ['masq', 'uid']:
            assert self.canvas_page.is_conf_link_hidden()

    def test_sub_account(self, site):
        if site.site_id and site.create_site_workflow in ['masq', 'uid'] and not len(
                [sec for sec in site.course.sections if sec.is_primary]) > 1:
            sub_account = self.canvas_page.selected_course_sub_account(site)
            course_code_parts = site.course.code.split()
            for part in course_code_parts:
                if re.search(r'\d', part):
                    course_code_parts.remove(part)
            dept = ' '.join(course_code_parts)
            utils.assert_equivalence(sub_account, dept)

    def test_files_accessibility_teach_learn(self, site):
        if site.site_id and site.create_site_workflow in ['masq', 'uid']:
            self.canvas_page.click_files_tab()
            self.canvas_page.toggle_access_links()
            title = 'Accessibility in Teaching & Learning'
            assert self.canvas_page.is_external_link_valid(self.canvas_page.ACCESS_TEACH_LEARN, title)

    def test_files_accessibility_basics_link(self, site):
        if site.site_id and site.create_site_workflow in ['masq', 'uid']:
            title = 'Accessibility Basics for bCourses'
            assert self.canvas_page.is_external_link_valid(self.canvas_page.ACCESS_BASICS_LINK, title)

    def test_files_accessibility_checker_link(self, site):
        if site.site_id and site.create_site_workflow in ['masq', 'uid']:
            title = 'How do I use the Accessibility Checker in the Rich'
            assert self.canvas_page.is_external_link_valid(self.canvas_page.ACCESS_CHECKER_LINK, title)

    def test_files_accessibility_dsp_link(self, site):
        if site.site_id and site.create_site_workflow in ['masq', 'uid']:
            title = 'Creating Accessible Content'
            assert self.canvas_page.is_external_link_valid(self.canvas_page.ACCESS_DSP_LINK, title)

    def test_files_accessibility_sensus_link(self, site):
        if site.site_id and site.create_site_workflow in ['masq', 'uid']:
            title = 'SensusAccess'
            assert self.canvas_page.is_external_link_valid(self.canvas_page.ACCESS_SENSUS_LINK, title)

    def test_files_accessibility_ally_link(self, site):
        if site.site_id and site.create_site_workflow in ['masq', 'uid']:
            title = 'Ally in bCourses'
            assert self.canvas_page.is_external_link_valid(self.canvas_page.ACCESS_ALLY_LINK, title)

    def test_assignment_religious_holiday_link(self, site):
        if site.site_id and site.create_site_workflow in ['masq', 'uid']:
            self.canvas_page.load_new_assignment_page(site)
            self.canvas_page.expand_religious_holidays()
            title = 'Religious Holidays & Religious Creed Policy'
            assert self.canvas_page.is_external_link_valid(self.canvas_page.RELIGIOUS_HOLIDAY_LINK, title)


@pytest.mark.usefixtures('page_objects')
class TestToolAccess:

    def test_canvas_admin_has_access_to_tool(self):
        self.canvas_page.masquerade_as(test.canvas_admin)
        self.canvas_page.click_manage_sites()
        self.create_course_site_page.when_present(self.create_course_site_page.CREATE_COURSE_SITE_LINK,
                                                  utils.get_short_timeout())
        assert self.create_course_site_page.is_el_enabled(self.create_course_site_page.CREATE_COURSE_SITE_LINK)

    def test_student_has_no_access_to_tool(self):
        self.canvas_page.masquerade_as(test.student)
        self.canvas_page.click_manage_sites_settings_link()
        self.create_course_site_page.when_present(self.create_course_site_page.CREATE_COURSE_SITE_LINK,
                                                  utils.get_short_timeout())
        assert not self.create_course_site_page.is_el_enabled(self.create_course_site_page.CREATE_COURSE_SITE_LINK)
