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
reader_uid = '60000'
student_uid = '40000'
ta_uid = '50000'
teacher_uid = '30000'


class TestSearchUsers:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_search_users(client, params={'searchText': 'ABC', 'searchType': 'name'}, expected_status_code=401)

    def test_no_canvas_account(self, client, app, fake_auth):
        """Denies user with no Canvas account."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {'course': ['get_by_id_8876542']}, m)
            canvas_site_id = '8876542'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=no_canvas_account_uid)
            _api_search_users(client, params={'searchText': 'ABC', 'searchType': 'name'}, expected_status_code=401)

    def test_student(self, client, app, fake_auth):
        """Denies student."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'account': ['get_admins'],
                'course': ['get_by_id_8876542', 'get_sections_8876542', 'get_enrollments_4567890'],
                'user': ['profile_40000'],
            }, m)
            canvas_site_id = '8876542'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=student_uid)
            _api_search_users(client, params={'searchText': 'ABC', 'searchType': 'name'}, expected_status_code=401)

    def test_reader(self, client, app, fake_auth):
        """Denies reader."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'account': ['get_admins'],
                'course': ['get_by_id_8876542', 'get_sections_8876542', 'get_enrollments_7890123'],
                'user': ['profile_60000'],
            }, m)
            canvas_site_id = '8876542'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=reader_uid)
            _api_search_users(client, params={'searchText': 'ABC', 'searchType': 'name'}, expected_status_code=401)

    def test_ta(self, client, app, fake_auth):
        """Allows TA."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'account': ['get_admins', 'get_terms'],
                'course': ['get_by_id_8876542', 'get_sections_8876542', 'get_enrollments_6789012'],
                'user': ['profile_50000'],
            }, m)
            canvas_site_id = '8876542'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=ta_uid)
            for params in [
                {'searchText': 'BRE', 'searchType': 'name'},
                {'searchText': 'BRE', 'searchType': 'email'},
                {'searchText': '60000', 'searchType': 'uid'},
            ]:
                results = _api_search_users(client, params=params)
                assert len(results) == 1
                assert results[0]['uid'] == '60000'

    def test_teacher(self, client, app, fake_auth):
        """Allows teacher."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'account': ['get_admins', 'get_terms'],
                'course': ['get_by_id_8876542', 'get_sections_8876542', 'get_enrollments_4567890'],
                'user': ['profile_30000'],
            }, m)
            canvas_site_id = '8876542'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=teacher_uid)
            for params in [
                {'searchText': '🤖', 'searchType': 'name'},
                {'searchText': 'Ash', 'searchType': 'email'},
                {'searchText': '30000', 'searchType': 'uid'},
            ]:
                results = _api_search_users(client, params=params)
                assert len(results) == 1
                assert results[0]['uid'] == '30000'

    def test_admin(self, client, app, fake_auth):
        """Allows admin."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'account': ['get_admins'],
                'course': ['get_by_id_8876542', 'get_sections_8876542', 'get_enrollments_4567890'],
                'user': ['profile_10000'],
            }, m)
            canvas_site_id = '8876542'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=admin_uid)
            for params in [
                {'searchText': 'Lambert, Joan', 'searchType': 'name'},
                {'searchText': 'lam', 'searchType': 'email'},
                {'searchText': '20000', 'searchType': 'uid'},
            ]:
                results = _api_search_users(client, params=params)
                assert len(results) == 1
                assert results[0]['uid'] == '20000'

    def test_invalid_params(self, client, app, fake_auth):
        """Returns an error if searchText is blank or searchType is invalid."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {'course': ['get_by_id_8876542']}, m)
            canvas_site_id = '8876542'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=admin_uid)
            _api_search_users(client, expected_status_code=400)
            _api_search_users(client, params={'searchType': 'name'}, expected_status_code=400)
            _api_search_users(client, params={'searchText': '', 'searchType': 'name'}, expected_status_code=400)
            _api_search_users(client, params={'searchText': 'ABC'}, expected_status_code=400)
            _api_search_users(client, params={'searchText': 'ABC', 'searchType': 'pizza'}, expected_status_code=400)


def _api_search_users(client, params=None, expected_status_code=200):
    path = '/api/canvas_user/search'
    if params:
        path += f'?{"&".join([k + "=" + v for k, v in params.items()])}'
    response = client.get(path)
    assert response.status_code == expected_status_code
    return response.json
