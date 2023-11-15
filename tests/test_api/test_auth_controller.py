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
from tests.util import override_config, register_canvas_uris

teacher_uid = '30000'


class TestStandaloneViewAccess:
    """Auth API."""

    def test_can_access_standalone_view(self, app, client):
        """Non-admin users can access standalone view per config."""
        with override_config(app, 'ALLOW_STANDALONE_FOR_NON_ADMINS', False):
            with override_config(app, 'DEV_AUTH_ENABLED', True):
                with requests_mock.Mocker() as m:
                    canvas_site_id = 8876542
                    register_canvas_uris(app, {
                        'account': ['get_admins', 'get_by_id'],
                        'course': [
                            f'get_by_id_{canvas_site_id}',
                            f'get_enrollments_{canvas_site_id}_4567890',
                            f'get_sections_{canvas_site_id}',
                        ],
                        'user': [
                            f'profile_{teacher_uid}',
                            f'user_courses_{teacher_uid}',
                        ],
                    }, m)
                    response = client.post(
                        '/api/auth/dev_auth',
                        data=json.dumps({
                            'canvas_site_id': canvas_site_id,
                            'uid': teacher_uid,
                            'password': app.config['DEV_AUTH_PASSWORD'],
                        }),
                        content_type='application/json',
                    )
                    assert response.status_code == 403
                    assert 'not authorized to use Ripley in standalone mode' in response.text
