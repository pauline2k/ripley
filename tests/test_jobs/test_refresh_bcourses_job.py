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

from contextlib import contextmanager
from unittest import mock

from moto import mock_s3
import pytest
import requests_mock
from ripley.jobs.refresh_bcourses_job import RefreshBcoursesJob
from tests.util import assert_s3_key_not_found, mock_s3_bucket, read_s3_csv, register_canvas_uris


class TestRefreshBcoursesJob:

    @mock_s3
    def test_no_changes(self, app):
        with _setup(app) as s3:
            RefreshBcoursesJob(app)._run(params={'mode': 'all'})
            assert_s3_key_not_found(app, s3, 'sis-id-sis-import')
            assert_s3_key_not_found(app, s3, 'user-sis-import')

    @mock_s3
    @mock.patch('ripley.jobs.refresh_bcourses_job.get_all_active_users')
    def test_name_change(self, mock_all_users, app, campus_users):
        with _setup(app) as s3:
            for u in campus_users:
                if u['first_name'] == 'Ash':
                    u['first_name'] = 'Definitely-not-a-synthetic-Ash'
                    break
            mock_all_users.return_value = campus_users

            RefreshBcoursesJob(app)._run(params={'mode': 'all'})

            assert_s3_key_not_found(app, s3, 'sis-id-sis-import')

            users_imported = read_s3_csv(app, s3, 'user-sis-import')
            assert len(users_imported) == 2
            assert users_imported[0] == 'user_id,login_id,first_name,last_name,email,status'
            assert users_imported[1] == 'UID:30000,30000,Definitely-not-a-synthetic-Ash,🤖,synthetic.ash@berkeley.edu,active'

    @mock_s3
    @mock.patch('ripley.jobs.refresh_bcourses_job.get_all_active_users')
    def test_email_change(self, mock_all_users, app, campus_users):
        with _setup(app) as s3:
            for u in campus_users:
                if u['email_address'] == 'synthetic.ash@berkeley.edu':
                    u['email_address'] = 'definitely.no.robots.here@berkeley.edu'
                    break
            mock_all_users.return_value = campus_users

            RefreshBcoursesJob(app)._run(params={'mode': 'all'})

            assert_s3_key_not_found(app, s3, 'sis-id-sis-import')

            users_imported = read_s3_csv(app, s3, 'user-sis-import')
            assert len(users_imported) == 2
            assert users_imported[0] == 'user_id,login_id,first_name,last_name,email,status'
            assert users_imported[1] == 'UID:30000,30000,Ash,🤖,definitely.no.robots.here@berkeley.edu,active'

    @mock_s3
    @mock.patch('ripley.jobs.refresh_bcourses_job.get_all_active_users')
    def test_sis_id_change(self, mock_all_users, app, campus_users):
        with _setup(app) as s3:
            for u in campus_users:
                if u['ldap_uid'] == '30000':
                    u['sid'] = '1337'
                    break
            mock_all_users.return_value = campus_users

            RefreshBcoursesJob(app)._run(params={'mode': 'all'})

            sis_id_changes_imported = read_s3_csv(app, s3, 'sis-id-sis-import')
            assert len(sis_id_changes_imported) == 2
            assert sis_id_changes_imported[0] == 'old_id,new_id,old_integration_id,new_integration_id,type'
            assert sis_id_changes_imported[1] == 'UID:30000,1337,,,user'

            assert_s3_key_not_found(app, s3, 'user-sis-import')

    @pytest.fixture(scope='function')
    def campus_users(self, app):
        from ripley.externals.data_loch import get_all_active_users
        return get_all_active_users()


@contextmanager
def _setup(app):
    with requests_mock.Mocker() as m:
        register_canvas_uris(app, {
            'account': [
                'create_report_provisioning_csv_sections',
                'create_report_provisioning_csv_users',
                'get_by_id',
                'get_report_provisioning_csv_sections',
                'get_report_provisioning_csv_users',
                'create_sis_import',
            ],
            'file': [
                'download_provisioning_csv_sections',
                'get_provisioning_csv_sections',
                'download_provisioning_csv_users',
                'get_provisioning_csv_users',
            ],
            'sis_import': [
                'get_by_id',
            ],
        }, m)

        with mock_s3_bucket(app) as s3:
            yield s3
