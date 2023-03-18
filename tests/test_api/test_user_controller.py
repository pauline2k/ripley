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

from werkzeug.http import parse_cookie

admin_uid = '10000'
student_uid = '40000'
teacher_uid = '30000'


class TestUserProfile:
    """User profile API."""

    @classmethod
    def _api_user_profile(cls, client, uid, expected_status_code=200):
        response = client.post(
            '/api/user/profile',
            data=json.dumps({'uid': uid}),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_anonymous(self, client):
        """Denies anonymous user."""
        self._api_user_profile(client, expected_status_code=401, uid=student_uid)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(teacher_uid)
        self._api_user_profile(client, expected_status_code=400, uid=student_uid)

    def test_user_can_view_own_profile(self, client, fake_auth):
        """User can view own profile."""
        fake_auth.login(student_uid)
        self._api_user_profile(client, uid=student_uid)

    def test_authorized_admin(self, client, fake_auth):
        fake_auth.login(admin_uid)
        api_json = self._api_user_profile(client, uid=student_uid)
        assert api_json['uid'] == student_uid

    def test_masquerading_cookies(self, client, fake_auth):
        """Masquerading user gets profile of masqueradee."""
        from flask_login import current_user

        fake_auth.login(teacher_uid)
        assert current_user.uid == teacher_uid
        response = client.get('/api/user/my_profile')
        assert response.json['uid'] == teacher_uid
        cookies = response.headers.getlist('Set-Cookie')
        user_sessions = [c for c in cookies if 'remember_ripley_token' in c]
        assert len(user_sessions) == 1
        user_session = parse_cookie(user_sessions[0])
        assert '{"canvas_site_id": null, "uid": "30000"}' in user_session['remember_ripley_token']
        assert 'Secure' in user_session
        assert user_session['SameSite'] == 'None'

        fake_auth.login(student_uid)
        assert current_user.uid == student_uid
        response = client.get('/api/user/my_profile')
        assert response.json['uid'] == student_uid
        cookies = response.headers.getlist('Set-Cookie')
        user_sessions = [c for c in cookies if 'remember_ripley_token' in c]
        assert len(user_sessions) == 1
        user_session = parse_cookie(user_sessions[0])
        assert '{"canvas_site_id": null, "uid": "40000"}' in user_session['remember_ripley_token']
        assert 'Secure' in user_session
        assert user_session['SameSite'] == 'None'
