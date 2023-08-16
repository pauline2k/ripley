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
    def _api_egrade_export_options(cls, client, expected_status_code=200, failed_assertion_message=None):
        response = client.get('/api/canvas_site/egrade_export/options')
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
            self._api_egrade_export_options(
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
            api_json = self._api_egrade_export_options(client)
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
            api_json = self._api_egrade_export_options(client)
            # Verify
            assert api_json['gradingStandardEnabled'] is True
