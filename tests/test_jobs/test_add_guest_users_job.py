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

from unittest import mock

from moto import mock_s3
import requests_mock
from ripley.jobs.add_guest_users_job import AddGuestUsersJob
from tests.util import mock_s3_bucket, read_s3_csv, register_canvas_uris


class TestAddGuestUsersJob:

    @mock_s3
    @mock.patch('ldap3.Connection')
    def test_job_run(self, mock_connection, app):
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'account': [
                    'get_by_id',
                    'create_sis_import',
                ],
                'sis_import': [
                    'get_by_id',
                ],
            }, m)

            mock_response = [{
                'dn': 'ou=people,dc=berkeley,dc=edu',
                'attributes': {
                    'berkeleyEduAffiliations': ['GUEST-TYPE-SPONSORED'],
                    'givenName': ['Jonesy'],
                    'mail': ['jonesy@berkeley.edu'],
                    'sn': ['🐈'],
                    'uid': ['9999999'],
                },
            }]

            mock_connection().__enter__().search.return_value = (None, None, mock_response, None)

            with mock_s3_bucket(app) as s3:
                AddGuestUsersJob(app)._run()
                users_imported = read_s3_csv(app, s3, 'guest-users')
                assert len(users_imported) == 2
                assert users_imported[0] == 'user_id,login_id,first_name,last_name,email,status'
                assert users_imported[1] == 'UID:9999999,9999999,Jonesy,🐈,jonesy@berkeley.edu,active'
