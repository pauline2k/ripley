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
from teena.models.ripley_tool import RipleyTools
from teena.test_utils import utils

test = TeenaTestConfig()
test.user_provisioning()
test_users = [
    test.manual_teacher,
    test.ta,
    test.designer,
    test.students[0],
]


@pytest.mark.usefixtures('page_objects')
class TestUserProvisioning:

    def test_setup(self):
        self.canvas_page.log_in(self.cal_net_page, test.admin.username, utils.get_admin_password())
        self.canvas_page.add_ripley_tools([t.value for t in RipleyTools])
        self.canvas_page.set_canvas_ids(test_users)
        self.canvas_page.get_admin_canvas_id(test.canvas_admin, 'Support Admin')

    def test_navigation_link(self):
        self.canvas_page.load_sub_account(utils.canvas_root_acct())
        self.canvas_page.click_user_prov()

    def test_provision_users_line_break_separated_uids(self):
        uids = '\n'.join([u.uid for u in test_users])
        self.user_prov_page.load_embedded_tool()
        self.user_prov_page.enter_uids_and_submit(uids)
        self.user_prov_page.when_visible(self.user_prov_page.SUCCESS_MSG, utils.get_long_timeout())

    def test_provision_users_space_separated_uids(self):
        uids = ' '.join([u.uid for u in test_users])
        self.user_prov_page.load_embedded_tool()
        self.user_prov_page.enter_uids_and_submit(uids)
        self.user_prov_page.when_visible(self.user_prov_page.SUCCESS_MSG, utils.get_long_timeout())

    def test_provision_users_comma_separated_uids(self):
        uids = ','.join([u.uid for u in test_users])
        self.user_prov_page.load_embedded_tool()
        self.user_prov_page.enter_uids_and_submit(uids)
        self.user_prov_page.when_visible(self.user_prov_page.SUCCESS_MSG, utils.get_long_timeout())

    def test_non_numeric_input_rejected(self):
        uids = 'Starchild'
        self.user_prov_page.load_embedded_tool()
        self.user_prov_page.enter_uids_and_submit(uids)
        self.user_prov_page.when_visible(self.user_prov_page.NON_NUMERIC_MSG, utils.get_short_timeout())

    def test_more_than_200_uids_rejected(self):
        uids = ' '.join([u.uid for u in test_users])
        uids = f'{uids} ' * 100
        self.user_prov_page.load_embedded_tool()
        self.user_prov_page.enter_uids_and_submit(uids)
        self.user_prov_page.when_visible(self.user_prov_page.MAX_INPUT_MSG, utils.get_short_timeout())

    def test_canvas_admin_has_tool_access(self):
        self.canvas_page.masquerade_as(test.canvas_admin)
        self.user_prov_page.load_embedded_tool()
        self.user_prov_page.when_present(self.user_prov_page.UID_INPUT, utils.get_short_timeout())

    @pytest.mark.parametrize(argnames='user',
                             argvalues=test_users,
                             ids=[user.role for user in test_users],
                             scope='function')
    def test_non_authorized_user_roles(self, user):
        self.canvas_page.masquerade_as(user)
        self.user_prov_page.load_embedded_tool()
        self.user_prov_page.wait_for_unauthorized_msg()
