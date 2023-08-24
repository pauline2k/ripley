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
import json

import requests_mock
from tests.util import register_canvas_uris

admin_uid = '10000'
no_canvas_account_uid = '10001'
not_enrolled_uid = '20000'
reader_uid = '60000'
student_uid = '40000'
ta_uid = '50000'
teacher_uid = '30000'


class TestEgradeExportOptions:

    @classmethod
    def _api_egrades_export_options(cls, client, expected_status_code=200, failed_assertion_message=None):
        response = client.get('/api/canvas_site/egrades_export/options')
        assert response.status_code == expected_status_code, failed_assertion_message
        return response.json

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized users."""
        users = {
            'anonymous': None,
            'no_canvas_account': no_canvas_account_uid,
            'not_enrolled': not_enrolled_uid,
            'reader': reader_uid,
            'student': student_uid,
            'teaching_assistant': ta_uid,
        }
        for user_type, uid in users.items():
            if uid:
                fake_auth.login(canvas_site_id='8876542', uid=no_canvas_account_uid)
            self._api_egrades_export_options(
                client,
                expected_status_code=401,
                failed_assertion_message=f'Unexpected response status for {user_type} user',
            )

    def test_teacher(self, client, app, fake_auth):
        """Allows teacher."""
        with requests_mock.Mocker() as m:
            canvas_site_id = '8876542'
            register_canvas_uris(app, {
                'account': ['get_admins', 'get_terms'],
                'course': [
                    f'get_by_id_{canvas_site_id}',
                    f'get_sections_{canvas_site_id}',
                    f'get_settings_{canvas_site_id}',
                    'get_enrollments_4567890',
                ],
                'user': [f'profile_{teacher_uid}'],
            }, m)
            fake_auth.login(canvas_site_id=canvas_site_id, uid=teacher_uid)
            api_json = self._api_egrades_export_options(client)
            # Verify
            assert api_json['gradingStandardEnabled'] is True

    def test_admin(self, client, app, fake_auth):
        """Allows teacher."""
        with requests_mock.Mocker() as m:
            canvas_site_id = '8876542'
            register_canvas_uris(app, {
                'account': ['get_admins', 'get_terms'],
                'course': [
                    f'get_by_id_{canvas_site_id}',
                    f'get_sections_{canvas_site_id}',
                    f'get_settings_{canvas_site_id}',
                ],
                'user': [f'profile_{admin_uid}'],
            }, m)
            fake_auth.login(canvas_site_id=canvas_site_id, uid=admin_uid)
            api_json = self._api_egrades_export_options(client)
            # Verify
            assert api_json['gradingStandardEnabled'] is True


class TestEgradesExportPrepare:

    @classmethod
    def _api_egrades_export_prepare(cls, client, expected_status_code=200, failed_assertion_message=None):
        response = client.post('/api/canvas_site/egrades_export/prepare')
        assert response.status_code == expected_status_code, failed_assertion_message
        return response.json

    @classmethod
    def _api_egrades_export_status(cls, client, job_id, expected_status_code=200):
        response = client.post(
            '/api/canvas_site/egrades_export/status',
            data=json.dumps({'jobId': job_id}),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized users."""
        canvas_site_id = '8876542'
        users = {
            'anonymous': None,
            'no_canvas_account': no_canvas_account_uid,
            'not_enrolled': not_enrolled_uid,
            'reader': reader_uid,
            'student': student_uid,
            'teaching_assistant': ta_uid,
        }
        for user_type, uid in users.items():
            if uid:
                fake_auth.login(canvas_site_id=canvas_site_id, uid=no_canvas_account_uid)
            self._api_egrades_export_prepare(
                client=client,
                expected_status_code=401,
                failed_assertion_message=f'Unexpected response status for {user_type} user',
            )

    def test_teacher(self, client, app, fake_auth):
        """Allows teacher."""
        with requests_mock.Mocker() as m:
            canvas_site_id = '8876542'
            register_canvas_uris(app, {
                'account': ['get_admins', 'get_terms'],
                'course': [
                    f'get_by_id_{canvas_site_id}',
                    f'get_sections_{canvas_site_id}',
                    f'get_settings_{canvas_site_id}',
                    'get_enrollments_4567890',
                ],
                'user': [f'profile_{teacher_uid}'],
            }, m)
            fake_auth.login(canvas_site_id=canvas_site_id, uid=teacher_uid)
            api_json = self._api_egrades_export_prepare(client)
            # Verify
            job_id = api_json['jobId']
            assert job_id
            assert api_json['jobRequestStatus'] == 'Success'
            # Verify that invalid job_id leads to not-found error.
            self._api_egrades_export_status(client, 'this-is-an-invalid-job-id', expected_status_code=400)
            api_json = self._api_egrades_export_status(client, job_id)
            assert 'jobStatus' in api_json


class TestEgradesExportDownload:

    @classmethod
    def _api_egrades_download(
            cls,
            client,
            section_id,
            term_id,
            expected_status_code=200,
            failed_assertion_message=None,
    ):
        path = '/api/canvas_site/egrades_export/download'
        query_string = f'gradeType=final&pnpCutoff=B&sectionId={section_id}&termId={term_id}'
        response = client.get(f'{path}?{query_string}')

        assert response.status_code == expected_status_code, failed_assertion_message
        return response

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized users."""
        users = {
            'anonymous': None,
            'no_canvas_account': no_canvas_account_uid,
            'not_enrolled': not_enrolled_uid,
            'reader': reader_uid,
            'student': student_uid,
            'teaching_assistant': ta_uid,
        }
        for user_type, uid in users.items():
            if uid:
                fake_auth.login(canvas_site_id='8876542', uid=no_canvas_account_uid)
            self._api_egrades_download(
                client,
                expected_status_code=401,
                failed_assertion_message=f'Unexpected response status for {user_type} user',
                section_id=32936,
                term_id=2232,
            )

    def test_teacher(self, client, app, fake_auth):
        """Allows teacher."""
        with requests_mock.Mocker() as m:
            canvas_site_id = 1010101
            section_id = 99999
            term_id = 2228
            register_canvas_uris(app, {
                'account': ['get_admins'],
                'course': [
                    f'get_by_id_{canvas_site_id}',
                    f'get_sections_{canvas_site_id}',
                    f'get_settings_{canvas_site_id}',
                    'get_enrollments_4567890',
                ],
                'section': ['get_enrollments_500'],
                'user': ['profile_10000'],
            }, m)
            fake_auth.login(canvas_site_id=canvas_site_id, uid=admin_uid)
            response = self._api_egrades_download(
                client,
                section_id=section_id,
                term_id=term_id,
            )
            assert 'csv' in response.content_type
            csv = str(response.data)
            # Verify
            assert 'ID,Name,Grade,Grading Basis,Comments' in csv
