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
from teena.models.person import Person
from teena.models.ripley_tool import RipleyTools
from teena.test_utils import utils

test = TeenaTestConfig()
project_site = test.projects()


@pytest.mark.usefixtures('page_objects')
class TestProjectSiteCreation:

    def test_canvas_login(self):
        self.canvas_page.log_in(self.cal_net_page, test.admin.username, utils.get_admin_password())
        self.canvas_page.add_ripley_tools([t.value for t in RipleyTools])
        self.canvas_page.set_canvas_ids(project_site.manual_members)
        self.canvas_page.get_admin_canvas_id(test.canvas_admin, 'Support Admin')
        self.canvas_page.masquerade_as(test.manual_teacher)

    def test_link_to_project_site_help(self):
        self.site_creation_page.load_embedded_tool(test.manual_teacher)
        title = 'bCourses Project Sites | Research, Teaching, & Learning'
        assert self.site_creation_page.is_external_link_valid(self.site_creation_page.PROJECT_HELP_LINK, title)

    def test_link_to_other_collaboration_tools(self):
        self.site_creation_page.switch_to_canvas_iframe()
        title = 'Collaboration Services | bConnected'
        assert self.site_creation_page.is_external_link_valid(self.site_creation_page.PROJECTS_LEARN_MORE_LINK, title)

    def test_cancel_project_site_creation(self):
        self.site_creation_page.load_embedded_tool(test.manual_teacher)
        self.site_creation_page.click_create_project_site()
        self.create_project_site_page.cancel_project_site()
        self.site_creation_page.when_present(self.site_creation_page.CREATE_PROJECT_SITE_LINK, utils.get_short_timeout())

    def test_project_site_name_max_chars(self):
        long_name = 'A loooooong title' * 15
        self.site_creation_page.click_create_project_site()
        self.create_project_site_page.enter_site_name(long_name)
        assert self.create_project_site_page.el_value(self.create_project_site_page.SITE_NAME_INPUT) == long_name[0:255]

    def test_project_site_create(self):
        project_site.title = f'QA Project Site {test.test_id}'
        self.create_project_site_page.create_project_site(project_site.title)
        self.create_project_site_page.wait_for_site_id(project_site)
        self.canvas_page.when_present(self.canvas_page.COURSE_SITE_HEADING, utils.get_short_timeout())
        utils.assert_equivalence(self.canvas_page.element(self.canvas_page.COURSE_SITE_HEADING).text, project_site.title)

    def test_project_homepage_redirect(self):
        self.canvas_page.when_visible(self.canvas_page.PROJECT_SITE_HEADING, utils.get_short_timeout())

    def test_no_roster_photos_tool(self):
        assert not self.roster_photos_page.is_present(self.roster_photos_page.ROSTER_PHOTOS_LINK)

    def test_no_official_sections_tool(self):
        assert not self.official_sections_page.is_present(self.official_sections_page.OFFICIAL_SECTIONS_LINK)

    def test_custom_user_roles(self):
        self.canvas_page.load_users_page(project_site)
        self.canvas_page.click_add_people()
        options = self.canvas_page.user_role_options()
        app.logger.info(f'Available user roles are {options}')
        utils.assert_equivalence(len(list(set(options) & {'Owner', 'Maintainer', 'Member'})), 3)

    def test_add_owner(self):
        user = Person({
            'uid': utils.get_oski_uid(),
            'role': 'Owner',
        })
        self.add_user_page.load_embedded_tool(project_site)
        self.add_user_page.search(user.uid, 'CalNet UID')
        self.add_user_page.add_user_by_uid(user)
        self.add_user_page.when_visible(self.add_user_page.SUCCESS_MSG, utils.get_short_timeout())

    def test_add_maintainer(self):
        user = Person({
            'uid': utils.get_oski_uid(),
            'role': 'Maintainer',
        })
        self.add_user_page.load_embedded_tool(project_site)
        self.add_user_page.search(user.uid, 'CalNet UID')
        self.add_user_page.add_user_by_uid(user)
        self.add_user_page.when_visible(self.add_user_page.SUCCESS_MSG, utils.get_short_timeout())

    def test_add_member(self):
        user = Person({
            'uid': utils.get_oski_uid(),
            'role': 'Member',
        })
        self.add_user_page.load_embedded_tool(project_site)
        self.add_user_page.search(user.uid, 'CalNet UID')
        self.add_user_page.add_user_by_uid(user)
        self.add_user_page.when_visible(self.add_user_page.SUCCESS_MSG, utils.get_short_timeout())

    def test_no_sis_id(self):
        self.canvas_page.stop_masquerading()
        self.canvas_page.load_course_settings(project_site)
        self.canvas_page.when_present(self.canvas_page.COURSE_SIS_ID_INPUT, utils.get_short_timeout())
        assert not self.canvas_page.el_value(self.canvas_page.COURSE_SIS_ID_INPUT)


@pytest.mark.usefixtures('page_objects')
@pytest.mark.parametrize(argnames='tc',
                         argvalues=[test.canvas_admin, test.ta, test.staff, test.student],
                         ids=[user.role for user in [test.canvas_admin, test.ta, test.staff, test.student]],
                         scope='class')
class TestUserRolePermissions:

    def test_create_site_button(self, tc):
        self.canvas_page.masquerade_as(tc)
        self.canvas_page.load_homepage()
        self.canvas_page.wait_for_homepage_content()
        if self.canvas_page.is_present(self.canvas_page.EVENTS_LIST_DIV):
            if tc.role in ['Canvas Admin', 'TA', 'Staff']:
                assert self.canvas_page.is_manage_sites_button_present()
            else:
                assert not self.canvas_page.is_manage_sites_button_present()
        else:
            app.logger.info(f'Unable to test Manage Sites button with UID {tc.uid} because wrong homepage is configured')

    def test_tool_access(self, tc):
        self.site_creation_page.load_embedded_tool(tc)
        if tc.role in ['Canvas Admin', 'Staff', 'TA']:
            app.logger.info(f'Verifying that {tc.role} UID {tc.uid} has access to the project site UI')
            self.site_creation_page.click_create_project_site()
            self.create_project_site_page.when_present(self.create_project_site_page.SITE_NAME_INPUT,
                                                       utils.get_short_timeout())
        else:
            app.logger.info(f'Verifying that {tc.role} UID {tc.uid} has no access to the project site UI')
            self.site_creation_page.when_present(self.site_creation_page.CREATE_PROJECT_SITE_LINK, utils.get_short_timeout())
            assert not self.site_creation_page.element(self.site_creation_page.CREATE_PROJECT_SITE_LINK).is_enabled()
