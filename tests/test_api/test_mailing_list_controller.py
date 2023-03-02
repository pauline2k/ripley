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
teacher_uid = '30000'
student_uid = '40000'


class TestFindMailingList:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_find_mailing_list(client, '1234567', expected_status_code=401)

    def test_no_canvas_account(self, client, fake_auth):
        """Denies user with no Canvas account."""
        fake_auth.login(no_canvas_account_uid)
        _api_find_mailing_list(client, '1234567', expected_status_code=401)

    def test_not_enrolled(self, client, app, fake_auth):
        """Denies user with no course enrollment."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {'course': ['get_by_id'], 'user': ['profile_20000']}, m)
            fake_auth.login(not_enrolled_uid)
            _api_find_mailing_list(client, '1234567', expected_status_code=401)

    def test_admin(self, client, app, fake_auth):
        """Allows admin."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {'course': ['get_by_id']}, m)
            fake_auth.login(admin_uid)
            response = _api_find_mailing_list(client, '1234567')

            assert response['canvasSite']['canvasCourseId'] == '1234567'
            assert response['canvasSite']['name'] == 'ASTRON 218: Stellar Dynamics and Galactic Structure'
            assert response['mailingList']['name'] == 'astron-218-stellar-dynamics-and-galactic-stru-sp23'
            assert response['mailingList']['state'] == 'unregistered'

    def test_teacher(self, client, app, fake_auth):
        """Allows teacher."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'course': ['get_by_id', 'get_user_1234567_4567890'],
                'user': ['profile_30000'],
            }, m)
            fake_auth.login(teacher_uid)
            response = _api_find_mailing_list(client, '1234567')

            assert response['mailingList']['name'] == 'astron-218-stellar-dynamics-and-galactic-stru-sp23'
            assert response['mailingList']['state'] == 'unregistered'

    def test_student(self, client, app, fake_auth):
        """Denies student."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'course': ['get_by_id', 'get_user_1234567_5678901'],
                'user': ['profile_40000'],
            }, m)
            fake_auth.login(student_uid)
            _api_find_mailing_list(client, '1234567', expected_status_code=401)


def _api_find_mailing_list(client, course_id, expected_status_code=200):
    response = client.get(f'api/mailing_lists/{course_id}')
    assert response.status_code == expected_status_code
    return response.json


class TestCreateMailingList:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_create_mailing_list(client, '1234567', expected_status_code=401)

    def test_no_canvas_account(self, client, fake_auth):
        """Denies user with no Canvas account."""
        fake_auth.login(no_canvas_account_uid)
        _api_create_mailing_list(client, '1234567', expected_status_code=401)

    def test_not_enrolled(self, client, app, fake_auth):
        """Denies user with no course enrollment."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {'course': ['get_by_id'], 'user': ['profile_20000']}, m)
            fake_auth.login(not_enrolled_uid)
            _api_create_mailing_list(client, '1234567', expected_status_code=401)

    def test_admin(self, client, app, fake_auth):
        """Allows admin."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {'course': ['get_by_id']}, m)
            fake_auth.login(admin_uid)
            response = _api_create_mailing_list(client, '1234567')

            assert response['canvasSite']['canvasCourseId'] == '1234567'
            assert response['canvasSite']['name'] == 'ASTRON 218: Stellar Dynamics and Galactic Structure'
            assert response['mailingList']['name'] == 'astron-218-stellar-dynamics-and-galactic-stru-sp23'
            assert response['mailingList']['state'] == 'created'

            # But you can't step into the same mailing list twice.
            _api_create_mailing_list(client, '1234567', expected_status_code=400)

    def test_teacher(self, client, app, fake_auth):
        """Allows teacher."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'course': ['get_by_id', 'get_user_1234567_4567890'],
                'user': ['profile_30000'],
            }, m)
            fake_auth.login(teacher_uid)
            response = _api_create_mailing_list(client, '1234567')

            assert response['mailingList']['name'] == 'astron-218-stellar-dynamics-and-galactic-stru-sp23'
            assert response['mailingList']['state'] == 'created'

    def test_student(self, client, app, fake_auth):
        """Denies student."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'course': ['get_by_id', 'get_user_1234567_5678901'],
                'user': ['profile_40000'],
            }, m)
            fake_auth.login(student_uid)
            _api_create_mailing_list(client, '1234567', expected_status_code=401)


def _api_create_mailing_list(client, course_id, expected_status_code=200):
    response = client.post(f'api/mailing_lists/{course_id}/create')
    assert response.status_code == expected_status_code
    return response.json
