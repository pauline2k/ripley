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

from datetime import datetime

from flask import current_app as app
import pytest
from teena.config.teena_test_config import TeenaTestConfig
from teena.models.ripley_job import RipleyJobs
from teena.models.ripley_tool import RipleyTools
from teena.test_utils import ripley_utils
from teena.test_utils import utils


test = TeenaTestConfig()
test.mailing_lists()
course_site_1 = test.course_sites[0]
course_site_2 = test.course_sites[1]
course_site_3 = test.course_sites[2]
course_site_4 = test.course_sites[3]
project_site = test.course_sites[4]
roles_with_tool_access = [test.manual_teacher, test.lead_ta, test.ta, test.reader]
roles_sans_tool_access = [test.designer, test.observer, test.student, test.wait_list_student]


@pytest.mark.usefixtures('page_objects')
class TestSetup:

    def test_create_course_sites(self):
        self.canvas_page.log_in(self.cal_net_page, test.admin.username, utils.get_admin_password())
        self.canvas_page.add_ripley_tools([t.value for t in RipleyTools])
        self.canvas_page.get_admin_canvas_id(test.canvas_admin, 'Support Admin')
        self.canvas_page.create_ripley_mailing_list_site(course_site_1)
        self.canvas_page.create_ripley_mailing_list_site(course_site_2)
        self.canvas_page.create_ripley_mailing_list_site(course_site_3)
        self.canvas_page.create_ripley_mailing_list_site(course_site_4)

    def test_create_project_site(self):
        self.site_creation_page.load_embedded_tool(test.admin)
        self.site_creation_page.click_create_project_site()
        self.create_project_site_page.create_project_site(project_site.title)
        self.create_project_site_page.wait_for_site_id(project_site)
        self.canvas_page.add_users(project_site, project_site.manual_members)

    def test_by_default_no_mailing_list_in_site_navigation(self):
        self.canvas_page.load_course_site(course_site_1)
        assert not self.mailing_list_page.is_present(self.mailing_list_page.MAILING_LIST_LINK)


@pytest.mark.usefixtures('page_objects')
class TestCanvasAdminToolAccess:

    def test_support_admin_has_site_tool_access(self):
        self.canvas_page.masquerade_as(test.canvas_admin, course_site_1)
        self.mailing_list_page.load_embedded_tool(course_site_1)
        self.mailing_list_page.when_present(self.mailing_list_page.CREATE_LIST_BUTTON, utils.get_short_timeout())

    def test_support_admin_has_admin_tool_access(self):
        self.mailing_lists_page.load_embedded_tool()
        self.mailing_lists_page.search_for_list(course_site_1.site_id)


@pytest.mark.usefixtures('page_objects')
@pytest.mark.parametrize(argnames='user',
                         argvalues=[user for user in roles_with_tool_access],
                         ids=[user.role for user in roles_with_tool_access],
                         scope='class')
class TestUsersWithSomeAccess:

    def test_role_with_site_tool_access(self, user):
        self.canvas_page.masquerade_as(user, course_site_1)
        self.mailing_list_page.load_embedded_tool(course_site_1)
        self.mailing_list_page.when_present(self.mailing_list_page.CREATE_LIST_BUTTON, utils.get_short_timeout())

    def test_role_sans_admin_tool_access(self, user):
        self.mailing_lists_page.load_embedded_tool()
        self.mailing_lists_page.wait_for_unauthorized_msg()


@pytest.mark.usefixtures('page_objects')
@pytest.mark.parametrize(argnames='user',
                         argvalues=[user for user in roles_sans_tool_access],
                         ids=[user.role for user in roles_sans_tool_access],
                         scope='class')
class TestUsersWithNoAccess:

    def test_role_sans_site_tool_access(self, user):
        self.canvas_page.masquerade_as(user, course_site_1)
        self.mailing_list_page.load_embedded_tool(course_site_1)
        self.mailing_list_page.wait_for_unauthorized_msg()

    def test_role_sans_admin_tool_access(self, user):
        self.mailing_lists_page.load_embedded_tool()
        self.mailing_lists_page.wait_for_unauthorized_msg()


@pytest.mark.usefixtures('page_objects')
class TestAdminToolListCreation:

    def test_requires_valid_site_id(self):
        self.canvas_page.switch_to_default_content()
        self.canvas_page.stop_masquerading()
        self.mailing_lists_page.load_embedded_tool()
        self.mailing_lists_page.search_for_list('99999999')
        self.mailing_lists_page.when_present(self.mailing_lists_page.NOT_FOUND_MSG, utils.get_short_timeout())

    def test_retrieve_site(self):
        self.mailing_lists_page.search_for_list(course_site_1.site_id)
        self.mailing_lists_page.when_present(self.mailing_lists_page.REGISTER_LIST_BUTTON, utils.get_short_timeout())

    def test_course_site_code_displayed(self):
        visible = self.mailing_lists_page.el_text_if_exists(self.mailing_lists_page.SITE_NAME_LINK)
        utils.assert_actual_includes_expected(visible, course_site_1.title)

    def test_course_site_term_displayed(self):
        visible = self.mailing_lists_page.el_text_if_exists(self.mailing_lists_page.SITE_TERM)
        utils.assert_equivalence(visible, course_site_1.term.name)

    def test_course_site_id_displayed(self):
        visible = self.mailing_lists_page.el_text_if_exists(self.mailing_lists_page.SITE_ID)
        utils.assert_equivalence(visible, f'bCourses Site ID {course_site_1.site_id}')

    def test_course_site_link_displayed(self):
        assert self.mailing_lists_page.is_external_link_valid(self.mailing_lists_page.SITE_NAME_LINK,
                                                              course_site_1.title, switch_to_canvas_iframe=True)

    def test_default_mailing_list_name(self):
        utils.assert_equivalence(self.mailing_lists_page.el_value(self.mailing_lists_page.LIST_NAME_INPUT),
                                 self.mailing_lists_page.default_list_name(course_site_1)[:-5])

    def test_no_spaces_in_custom_name(self):
        self.mailing_lists_page.enter_custom_list_name('lousy-list name')
        self.mailing_lists_page.when_present(self.mailing_lists_page.LIST_NAME_ERROR_MSG, utils.get_short_timeout())

    def test_no_invalid_characters_in_custom_name(self):
        self.mailing_lists_page.enter_custom_list_name('lousier_list_name?')
        self.mailing_lists_page.when_present(self.mailing_lists_page.LIST_NAME_ERROR_MSG, utils.get_short_timeout())

    def test_create_mailing_list(self):
        self.mailing_lists_page.enter_custom_list_name(self.mailing_lists_page.default_list_name(course_site_1)[:-5])
        visible = self.mailing_lists_page.wait_for_list_address()
        expected = f'{self.mailing_lists_page.default_list_name(course_site_1)}@bcourses-mail.berkeley.edu'
        utils.assert_equivalence(visible, expected)

    def test_no_dupe_course_code_list(self):
        self.mailing_lists_page.click_cancel_list()
        self.mailing_lists_page.search_for_list(course_site_2.site_id)
        self.mailing_lists_page.enter_custom_list_name(self.mailing_lists_page.default_list_name(course_site_1)[:-5])
        self.mailing_lists_page.when_present(self.mailing_lists_page.LIST_NAME_TAKEN_ERROR_MSG, utils.get_short_timeout())


@pytest.mark.usefixtures('page_objects')
class TestAdminToolExistingList:

    def test_email_address(self):
        self.mailing_lists_page.load_embedded_tool()
        self.mailing_lists_page.search_for_list(course_site_1.site_id)
        visible = self.mailing_lists_page.wait_for_list_address()
        expected = f'{self.mailing_lists_page.default_list_name(course_site_1)}@bcourses-mail.berkeley.edu'
        utils.assert_equivalence(visible, expected)

    def test_membership_count(self):
        visible = self.mailing_lists_page.wait_for_membership_count()
        utils.assert_equivalence(visible, '0')

    def test_most_recent_membership_update(self):
        visible = self.mailing_lists_page.el_text_if_exists(self.mailing_lists_page.LIST_UPDATE_TIME)
        utils.assert_equivalence(visible, 'Never')

    def test_course_site_code_displayed(self):
        visible = self.mailing_lists_page.el_text_if_exists(self.mailing_lists_page.LIST_SITE_LINK)
        utils.assert_actual_includes_expected(visible, course_site_1.title)

    def test_course_site_title_and_term_displayed(self):
        visible = self.mailing_lists_page.el_text_if_exists(self.mailing_lists_page.LIST_SITE_DESC)
        expected = f'{course_site_1.abbreviation}, {course_site_1.term.name}'
        utils.assert_equivalence(visible, expected)

    def test_course_site_id_displayed(self):
        visible = self.mailing_lists_page.el_text_if_exists(self.mailing_lists_page.LIST_SITE_ID)
        utils.assert_equivalence(visible, course_site_1.site_id)

    def test_course_site_link_displayed(self):
        assert self.mailing_lists_page.is_external_link_valid(self.mailing_lists_page.LIST_SITE_LINK,
                                                              course_site_1.title, switch_to_canvas_iframe=True)

    def test_create_list_memberships(self):
        self.mailing_lists_page.update_memberships()
        visible_count = self.mailing_lists_page.el_text_if_exists(self.mailing_lists_page.LIST_MEMBERSHIP_COUNT)
        visible_date = self.mailing_lists_page.el_text_if_exists(self.mailing_lists_page.LIST_UPDATE_TIME)
        utils.assert_equivalence(visible_count, str(len(course_site_1.manual_members)))
        utils.assert_actual_includes_expected(visible_date, datetime.now().strftime('%b %-d, %Y'))

    def test_list_of_members_added(self):
        self.mailing_lists_page.expand_added_users()
        for member in course_site_1.manual_members:
            app.logger.info(f'Checking if {member.email} has been added')
            assert self.mailing_lists_page.is_user_added(member)

    def test_delete_list_memberships(self):
        member = course_site_1.manual_members[-1]
        self.canvas_page.remove_users_from_course(course_site_1, [member])
        self.mailing_lists_page.load_embedded_tool()
        self.mailing_lists_page.search_for_list(course_site_1.site_id)
        self.mailing_lists_page.update_memberships()
        visible_count = self.mailing_lists_page.wait_for_membership_count()
        utils.assert_equivalence(visible_count, str(len(course_site_1.manual_members) - 1))

    def test_list_of_members_deleted(self):
        member = course_site_1.manual_members[-1]
        self.mailing_lists_page.expand_removed_users()
        app.logger.info(f'Checking if {member.email} has been removed')
        assert self.mailing_lists_page.is_user_removed(member)

    def test_restore_list_memberships(self):
        member = course_site_1.manual_members[-1]
        self.canvas_page.add_users(course_site_1, [member])
        self.canvas_page.masquerade_as(member, course_site_1)
        self.canvas_page.stop_masquerading()
        self.mailing_lists_page.load_embedded_tool()
        self.mailing_lists_page.search_for_list(course_site_1.site_id)
        self.mailing_lists_page.update_memberships()
        visible_count = self.mailing_lists_page.wait_for_membership_count()
        utils.assert_equivalence(visible_count, str(len(course_site_1.manual_members)))

    def test_list_of_members_restored(self):
        member = course_site_1.manual_members[-1]
        self.mailing_lists_page.expand_restored_users()
        app.logger.info(f'Checking if {member.email} has been restored')
        assert self.mailing_lists_page.is_user_restored(member)

    def test_update_member_email_address(self):
        member = course_site_1.manual_members[-1]
        ripley_utils.set_mailing_list_member_email(member,
                                                   f'foo{test.test_id}@bar.com')
        self.mailing_lists_page.load_embedded_tool()
        self.mailing_lists_page.search_for_list(course_site_1.site_id)
        self.mailing_lists_page.update_memberships()
        self.mailing_lists_page.expand_added_users()
        assert self.mailing_lists_page.is_user_added(member)


@pytest.mark.usefixtures('page_objects')
class TestRipleyJobMembershipUpdates:

    def test_delete_list_memberships(self):
        member = course_site_1.manual_members[-1]
        self.canvas_page.remove_users_from_course(course_site_1, [member])
        self.splash_page.load_page()
        self.admin_page.run_job(RipleyJobs.REFRESH_MAILING_LIST.value)
        self.mailing_lists_page.load_embedded_tool()
        self.mailing_lists_page.search_for_list(course_site_1.site_id)
        visible_count = self.mailing_lists_page.wait_for_membership_count()
        utils.assert_equivalence(visible_count, str(len(course_site_1.manual_members) - 1))

    def test_restore_list_memberships(self):
        member = course_site_1.manual_members[-1]
        self.canvas_page.add_users(course_site_1, [member])
        self.canvas_page.masquerade_as(member, course_site_1)
        self.canvas_page.stop_masquerading()
        self.splash_page.load_page()
        self.admin_page.run_job(RipleyJobs.REFRESH_MAILING_LIST.value)
        self.mailing_lists_page.load_embedded_tool()
        self.mailing_lists_page.search_for_list(course_site_1.site_id)
        visible_count = self.mailing_lists_page.wait_for_membership_count()
        utils.assert_equivalence(visible_count, str(len(course_site_1.manual_members)))

    def test_update_member_email_address(self):
        member = course_site_1.manual_members[-1]
        new_email = f'bar{test.test_id}@foo.com'
        ripley_utils.set_mailing_list_member_email(member, new_email)
        self.splash_page.load_page()
        self.admin_page.run_job(RipleyJobs.REFRESH_MAILING_LIST.value)
        updated = ripley_utils.get_mailing_list_member_email(member)
        utils.assert_equivalence(updated, member.email)

    def test_no_membership_update_more_than_one_term_past(self):
        self.mailing_lists_page.load_embedded_tool()
        self.mailing_lists_page.search_for_list(course_site_4.site_id)
        self.mailing_lists_page.enter_custom_list_name(self.mailing_lists_page.default_list_name(course_site_4)[:-5])
        visible = self.mailing_lists_page.wait_for_list_address()
        expected = f'{self.mailing_lists_page.default_list_name(course_site_4)}@bcourses-mail.berkeley.edu'
        utils.assert_equivalence(visible, expected)

        self.canvas_page.masquerade_as(course_site_4.manual_members[0], course_site_4)
        self.canvas_page.stop_masquerading()
        self.splash_page.load_page()
        self.admin_page.run_job(RipleyJobs.REFRESH_MAILING_LIST.value)
        self.mailing_lists_page.load_embedded_tool()
        self.mailing_lists_page.search_for_list(course_site_4.site_id)
        visible_count = self.mailing_lists_page.wait_for_membership_count()
        utils.assert_equivalence(visible_count, '0')


@pytest.mark.usefixtures('page_objects')
class TestInstructorFacingTool:

    def test_no_existing_mailing_list(self):
        self.canvas_page.masquerade_as(course_site_3.manual_members[0], course_site_3)
        self.mailing_list_page.load_embedded_tool(course_site_3)
        self.mailing_list_page.when_present(self.mailing_list_page.NO_LIST_MSG, utils.get_short_timeout())

    def test_create_list_default_name(self):
        self.mailing_list_page.create_list()
        visible = self.mailing_list_page.el_text_if_exists(self.mailing_list_page.LIST_ADDRESS)
        expected = f'{self.mailing_list_page.default_list_name(course_site_3)}@bcourses-mail.berkeley.edu'
        utils.assert_equivalence(visible, expected)

    def test_no_list_for_dupe_course_code_and_term(self):
        course_site_2.title = course_site_1.title
        self.canvas_page.stop_masquerading()
        self.canvas_page.edit_course_name(course_site_2)
        self.canvas_page.masquerade_as(course_site_2.manual_members[0], course_site_2)
        self.mailing_list_page.load_embedded_tool(course_site_2)
        self.mailing_list_page.click_create_list()
        self.mailing_list_page.when_present(self.mailing_list_page.LIST_DUPE_EMAIL_MSG, utils.get_short_timeout())

    def test_existing_mailing_list(self):
        self.mailing_list_page.load_embedded_tool(course_site_3)
        visible = self.mailing_list_page.wait_for_list_address()
        expected = f'{self.mailing_list_page.default_list_name(course_site_3)}@bcourses-mail.berkeley.edu'
        utils.assert_equivalence(visible, expected)


@pytest.mark.usefixtures('page_objects')
class TestProjectSiteLists:

    def test_admin_tool_allows_list_creation(self):
        self.canvas_page.stop_masquerading()
        self.mailing_lists_page.load_embedded_tool()
        self.mailing_lists_page.search_for_list(project_site.site_id)
        self.mailing_lists_page.enter_custom_list_name(
            f'{self.mailing_lists_page.default_list_name(project_site)}'.replace('-list', ''))
        visible = self.mailing_lists_page.wait_for_list_address()
        expected = f'{self.mailing_lists_page.default_list_name(project_site)}@bcourses-mail.berkeley.edu'
        utils.assert_equivalence(visible, expected)

    def test_admin_tool_updates_membership(self):
        self.mailing_lists_page.update_memberships()
