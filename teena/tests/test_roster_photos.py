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
from teena.test_utils import utils

test = TeenaTestConfig()
test.rosters()


@pytest.mark.usefixtures('page_objects')
class TestRosterPhotos:

    def test_setup(self):
        self.canvas_page.log_in(self.cal_net_page, test.admin.username, utils.get_admin_password())
        self.canvas_page.configure_single_site(test)
        self.create_course_site_page.provision_course_site(test.course_site)
        self.canvas_page.publish_course_site(test.course_site)
        self.canvas_page.load_users_page(test.course_site)
        self.canvas_page.click_find_person_to_add()
        for user in test.course_site.manual_members:
            self.add_user_page.search(user.uid, 'CalNet UID')
            self.add_user_page.add_user_by_uid(user, test.course_site.sections[0])

    def test_all_sis_enrollments_visible(self):
        self.canvas_page.masquerade_as(test.course_site.course.teachers[0], test.course_site)
        self.roster_photos_page.click_roster_photos_link()
        self.roster_photos_page.wait_for_photos_to_load()
        visible_sids = self.roster_photos_page.all_sids()
        visible_sids.sort()
        expected_sids = test.course_site.expected_student_sids()
        expected_sids.sort()
        utils.assert_equivalence(visible_sids, expected_sids)

    def test_waitlisted_students_have_placeholders(self):
        self.roster_photos_page.wait_for_placeholder_count(test.course_site.expected_wait_list_count())

    def test_all_sections_visible_by_default(self):
        expected_section_codes = [f'{s.course} {s.label}' for s in test.course_site.sections]
        expected_section_codes.sort()
        expected_section_codes.insert(0, 'All Sections')
        utils.assert_equivalence(self.roster_photos_page.section_options(), expected_section_codes)

    def test_filter_photos_by_search_string(self):
        if test.course_site.expected_student_sids():
            sid = self.roster_photos_page.all_sids()[-1]
            self.roster_photos_page.filter_by_string(sid)
            filtered_sids = self.roster_photos_page.all_sids()
            assert len(filtered_sids) == 1
            assert filtered_sids[0] == sid

    def test_download_csv(self):
        primary = next(filter(lambda s: s.is_primary, test.course_site.sections))
        expected_sids = test.course_site.expected_student_sids()
        expected_sids.sort()
        self.roster_photos_page.filter_by_section(primary)
        exported_sids = self.roster_photos_page.export_roster(test.course_site)
        exported_sids.sort()
        utils.assert_equivalence(exported_sids, expected_sids)

    def test_print_photos_button_present(self):
        self.roster_photos_page.load_embedded_tool(test.course_site)
        self.roster_photos_page.when_visible(self.roster_photos_page.PRINT_ROSTER_LINK, utils.get_medium_timeout())


@pytest.mark.usefixtures('page_objects')
@pytest.mark.parametrize(argnames='section',
                         argvalues=test.course_site.sections,
                         ids=[section.section_id for section in test.course_site.sections],
                         scope='class')
class TestFilterBySection:

    def test_filter_photos_by_section(self, section):
        self.roster_photos_page.filter_by_string('')
        section_sids = [e.student.sid for e in section.enrollments]
        section_sids.sort()
        self.roster_photos_page.filter_by_section(section)
        visible = self.roster_photos_page.all_sids()
        visible.sort()
        utils.assert_equivalence(visible, section_sids)


@pytest.mark.usefixtures('page_objects')
@pytest.mark.parametrize(argnames='user',
                         argvalues=[test.canvas_admin, test.lead_ta, test.ta],
                         ids=[user.role for user in [test.canvas_admin, test.lead_ta, test.ta]],
                         scope='class')
class TestUserRoleAdminOrTA:

    def test_access_to_tool(self, user):
        self.canvas_page.masquerade_as(user, test.course_site)
        self.roster_photos_page.load_embedded_tool(test.course_site)
        self.roster_photos_page.wait_for_photos_to_load()

    def test_navigation_link(self, user):
        self.canvas_page.switch_to_default_content()
        assert self.roster_photos_page.is_present(self.roster_photos_page.ROSTER_PHOTOS_LINK)


@pytest.mark.usefixtures('page_objects')
class TestUserRoleObserver:

    def test_access_to_tool(self):
        self.canvas_page.masquerade_as(test.observer, test.course_site)
        self.roster_photos_page.load_embedded_tool(test.course_site)
        self.roster_photos_page.wait_for_unauthorized_msg()

    def test_navigation_link(self):
        self.canvas_page.switch_to_default_content()
        assert not self.roster_photos_page.is_present(self.roster_photos_page.ROSTER_PHOTOS_LINK)


@pytest.mark.usefixtures('page_objects')
@pytest.mark.parametrize(argnames='user',
                         argvalues=[test.designer, test.reader],
                         ids=[user.role for user in [test.designer, test.reader]],
                         scope='class')
class TestUserRoleDesignerOrReader:

    def test_access_to_tool(self, user):
        self.canvas_page.masquerade_as(user, test.course_site)
        self.roster_photos_page.load_embedded_tool(test.course_site)
        self.roster_photos_page.wait_for_unauthorized_msg()

    def test_navigation_link(self, user):
        self.canvas_page.switch_to_default_content()
        assert self.roster_photos_page.is_present(self.roster_photos_page.ROSTER_PHOTOS_LINK)


@pytest.mark.usefixtures('page_objects')
@pytest.mark.parametrize(argnames='user',
                         argvalues=[test.students[0], test.wait_list_student],
                         ids=[user.role for user in [test.students[0], test.wait_list_student]],
                         scope='class')
class TestUserRoleStudents:

    def test_access_to_tool(self, user):
        self.canvas_page.masquerade_as(user, test.course_site)
        self.roster_photos_page.load_embedded_tool(test.course_site)
        self.roster_photos_page.wait_for_either_element(
            [self.canvas_page.ACCESS_DENIED_MSG, self.roster_photos_page.UNAUTH_MSG], utils.get_medium_timeout())

    def test_navigation_link(self, user):
        self.canvas_page.switch_to_default_content()
        assert not self.roster_photos_page.is_present(self.roster_photos_page.ROSTER_PHOTOS_LINK)
