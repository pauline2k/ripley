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

from enum import Enum

from teena.test_utils import utils


class RipleyTool(object):

    def __init__(self, name, path, navigation, account=None, dev_key=None, tool_id=None):
        self.name = name
        self.path = path
        self.navigation = navigation
        self.account = account
        self.dev_key = dev_key
        self.tool_id = tool_id

    def set_account(self):
        if self.name in ['Create & Manage Sites', 'Find a Person to Add', 'User Provisioning']:
            self.account = utils.canvas_root_acct()
        elif self.name == 'Mailing Lists':
            self.account = utils.canvas_admin_acct()
        else:
            self.account = utils.canvas_official_courses_acct()


class RipleyTools(Enum):

    ADD_USER = RipleyTool(name='Find a Person to Add',
                          path='add_user',
                          navigation='course_navigation')

    E_GRADES = RipleyTool(name='Download E-Grades',
                          path='export_grade',
                          navigation='course_navigation')

    MAILING_LIST = RipleyTool(name='Mailing List',
                              path='mailing_list',
                              navigation='course_navigation')

    MAILING_LISTS = RipleyTool(name='Mailing Lists',
                               path='mailing_lists',
                               navigation='account_navigation')

    MANAGE_SITES = RipleyTool(name='Create & Manage Sites',
                              path='manage_sites',
                              navigation='user_navigation')

    NEWT = RipleyTool(name='Grade Distribution',
                      path='grade_distribution',
                      navigation='course_navigation')

    ROSTER_PHOTOS = RipleyTool(name='Roster Photos',
                               path='roster_photos',
                               navigation='course_navigation')

    USER_PROVISIONING = RipleyTool(name='User Provisioning',
                                   path='provision_user',
                                   navigation='account_navigation')
