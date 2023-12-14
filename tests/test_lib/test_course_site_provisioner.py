"""
Copyright ©2023. The Regents of the University of California (Regents). All Rights Reserved.

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

from unittest import mock
from unittest.mock import mock_open

import bonsai
import pytest
import requests_mock
from ripley.lib.course_site_provisioner import provision_course_site
from tests.util import mock_s3_bucket, register_canvas_uris

admin_uid = '10000'
teacher_uid = '30000'


class TestCourseSiteProvisioner:

    @pytest.mark.skip(reason='TODO: A work in progress.')
    def test_provision_course_site(self, app):
        with requests_mock.Mocker() as m:
            fixtures = {
                'account': [
                    'get_by_id',
                    'create_sis_import',
                    'get_sub_account_anthro',
                ],
                'course': [
                    'get_course_ANTHRO_189',
                    'get_course_ANTHRO_189_not_found',
                    'get_tabs_1523731',
                ],
                'sis_import': [
                    'get_by_id',
                ],
            }
            register_canvas_uris(app, fixtures, m)
            mock_connection = mock.Mock()
            mock_connection.paged_search.return_value = [
                {
                    'berkeleyEduAffiliations': bonsai.LDAPValueList(['GUEST-TYPE-SPONSORED']),
                    'givenName': bonsai.LDAPValueList(['Jonesy']),
                    'mail': bonsai.LDAPValueList(['jonesy@berkeley.edu']),
                    'sn': bonsai.LDAPValueList(['🐈']),
                    'uid': bonsai.LDAPValueList(['9999999']),
                },
            ]
            mock_open.return_value = mock_connection

            with mock_s3_bucket(app) as s3:
                assert s3
                provision_course_site(
                    uid=teacher_uid,
                    site_name='The Acheron moon',
                    site_abbreviation='LV-426',
                    term_slug='spring-2023',
                    section_ids=['32936', '32937'],
                    is_admin_by_ccns=False,
                )
