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
from ripley.models.mailing_list import MailingList
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
        fake_auth.login(canvas_site_id=None, uid=no_canvas_account_uid)
        _api_find_mailing_list(client, '1234567', expected_status_code=401)

    def test_not_enrolled(self, client, app, fake_auth):
        """Denies user with no course enrollment."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {'course': ['get_by_id_1234567'], 'user': ['profile_20000']}, m)
            fake_auth.login(canvas_site_id=None, uid=not_enrolled_uid)
            _api_find_mailing_list(client, '1234567', expected_status_code=401)

    def test_admin(self, client, app, fake_auth):
        """Allows admin."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {'course': ['get_by_id_1234567', 'search_users_1234567']}, m)
            canvas_site_id = '1234567'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=admin_uid)
            _api_create_mailing_list(client, canvas_site_id)
            response = _api_find_mailing_list(client, canvas_site_id)

            assert response['canvasSite']['canvasSiteId'] == 1234567
            assert response['canvasSite']['name'] == 'ASTRON 218: Stellar Dynamics and Galactic Structure'
            assert response['name'] == 'astron-218-stellar-dynamics-and-galactic-stru-sp23'

    def test_teacher(self, client, app, fake_auth):
        """Allows teacher."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'course': ['get_by_id_1234567', 'get_user_1234567_4567890', 'search_users_1234567'],
                'user': ['profile_30000'],
            }, m)
            canvas_site_id = '1234567'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=teacher_uid)
            _api_create_mailing_list(client, canvas_site_id)
            response = _api_find_mailing_list(client, canvas_site_id)

            assert response['name'] == 'astron-218-stellar-dynamics-and-galactic-stru-sp23'

    def test_student(self, client, app, fake_auth):
        """Denies student."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'course': ['get_by_id_1234567', 'get_user_1234567_5678901'],
                'user': ['profile_40000'],
            }, m)
            canvas_site_id = '1234567'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=student_uid)
            _api_find_mailing_list(client, canvas_site_id, expected_status_code=401)


class TestCreateMailingList:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_create_mailing_list(client, '1234567', expected_status_code=401)

    def test_no_canvas_account(self, client, fake_auth):
        """Denies user with no Canvas account."""
        canvas_site_id = '1234567'
        fake_auth.login(canvas_site_id=canvas_site_id, uid=no_canvas_account_uid)
        _api_create_mailing_list(client, canvas_site_id, expected_status_code=401)

    def test_not_enrolled(self, client, app, fake_auth):
        """Denies user with no course enrollment."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {'course': ['get_by_id_1234567'], 'user': ['profile_20000']}, m)
            canvas_site_id = '1234567'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=not_enrolled_uid)
            _api_create_mailing_list(client, canvas_site_id, expected_status_code=401)

    def test_authorized(self, client, app, fake_auth):
        """Allows admin."""
        with requests_mock.Mocker() as m:
            mailing_list_id = None
            for mailing_list_name in (None, 'I am a custom name.'):
                if mailing_list_id:
                    # Delete previous mailing_list test data.
                    MailingList.delete(mailing_list_id)
                register_canvas_uris(app, {'course': ['get_by_id_1234567', 'search_users_1234567']}, m)
                canvas_site_id = '1234567'
                fake_auth.login(canvas_site_id=canvas_site_id, uid=admin_uid)
                api_json = _api_create_mailing_list(
                    client=client,
                    canvas_site_id=canvas_site_id,
                    name=mailing_list_name,
                )
                mailing_list_id = api_json['mailingList']['id']
                assert api_json['mailingList']['canvasSite']['canvasSiteId'] == 1234567
                assert api_json['mailingList']['canvasSite']['name'] == 'ASTRON 218: Stellar Dynamics and Galactic Structure'
                if mailing_list_name:
                    assert api_json['mailingList']['name'] == mailing_list_name
                else:
                    assert api_json['mailingList']['name'] == 'astron-218-stellar-dynamics-and-galactic-stru-sp23'

                # But you can't step into the same mailing list twice.
                _api_create_mailing_list(
                    client=client,
                    canvas_site_id=canvas_site_id,
                    expected_status_code=400,
                )

    def test_teacher(self, client, app, fake_auth):
        """Allows teacher."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'course': ['get_by_id_1234567', 'get_user_1234567_4567890', 'search_users_1234567'],
                'user': ['profile_30000'],
            }, m)
            canvas_site_id = '1234567'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=teacher_uid)
            response = _api_create_mailing_list(client, canvas_site_id)

            assert response['mailingList']['name'] == 'astron-218-stellar-dynamics-and-galactic-stru-sp23'

    def test_student(self, client, app, fake_auth):
        """Denies student."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'course': ['get_by_id_1234567', 'get_user_1234567_5678901', 'search_users_1234567'],
                'user': ['profile_40000'],
            }, m)
            canvas_site_id = '1234567'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=student_uid)
            _api_create_mailing_list(client, canvas_site_id, expected_status_code=401)


class TestActivateMailingList:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_activate_mailing_list(
            activate=True,
            canvas_site_id='1234567',
            client=client,
            expected_status_code=401,
        )

    def test_unauthorized(self, client, fake_auth):
        """Student cannot activate a mailing list."""
        canvas_site_id = '1234567'
        fake_auth.login(canvas_site_id=canvas_site_id, uid=student_uid)
        _api_activate_mailing_list(
            activate=True,
            canvas_site_id='1234567',
            client=client,
            expected_status_code=401,
        )

    def test_authorized(self, app, client, fake_auth):
        """Teacher can activate a mailing list."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'course': ['get_by_id_8876542', 'get_sections_8876542', 'get_enrollments_4567890'],
                'user': ['profile_30000'],
            }, m)
            canvas_site_id = '8876542'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=admin_uid)
            mailing_list = MailingList.create(
                canvas_site_id=canvas_site_id,
                list_name='Wonder Twin powers activate!',
                welcome_email_body='Body',
                welcome_email_subject='Subject',
            )
            assert mailing_list.welcome_email_active is False
            api_json = _api_activate_mailing_list(
                activate=True,
                canvas_site_id=canvas_site_id,
                client=client,
            )
            assert api_json['welcomeEmailActive'] is True
            api_json = _api_activate_mailing_list(
                activate=False,
                canvas_site_id=canvas_site_id,
                client=client,
            )
            assert api_json['welcomeEmailActive'] is False


class TestPopulateMailingList:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_populate_mailing_list(client, '1234567', expected_status_code=401)

    def test_no_canvas_account(self, client, fake_auth):
        """Denies user with no Canvas account."""
        canvas_site_id = '1234567'
        fake_auth.login(canvas_site_id=canvas_site_id, uid=no_canvas_account_uid)
        _api_populate_mailing_list(client, canvas_site_id, expected_status_code=401)

    def test_not_enrolled(self, client, app, fake_auth):
        """Denies user with no course enrollment."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {'course': ['get_by_id_1234567'], 'user': ['profile_20000']}, m)
            canvas_site_id = '1234567'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=not_enrolled_uid)
            _api_populate_mailing_list(client, canvas_site_id, expected_status_code=401)

    def test_admin(self, client, app, fake_auth):
        """Allows admin."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'course': ['get_by_id_1234567', 'search_users_1234567'],
                'user': ['profile_10000'],
            }, m)
            canvas_site_id = '1234567'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=admin_uid)
            _api_create_mailing_list(client, canvas_site_id)
            api_json = _api_populate_mailing_list(client, canvas_site_id)
            assert api_json['mailingList']['canvasSite']['canvasSiteId'] == 1234567
            # TODO: verify populated mailing list

    def test_teacher(self, client, app, fake_auth):
        """Allows teacher."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'course': ['get_by_id_1234567', 'get_user_1234567_4567890', 'search_users_1234567'],
                'user': ['profile_30000'],
            }, m)
            canvas_site_id = '1234567'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=teacher_uid)
            _api_create_mailing_list(client, canvas_site_id)
            api_json = _api_populate_mailing_list(client, canvas_site_id)
            assert api_json['mailingList']['name'] == 'astron-218-stellar-dynamics-and-galactic-stru-sp23'
            # TODO: verify populated mailing list

    def test_student(self, client, app, fake_auth):
        """Denies student."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'course': ['get_by_id_1234567', 'get_user_1234567_5678901'],
                'user': ['profile_40000'],
            }, m)
            canvas_site_id = '1234567'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=student_uid)
            _api_populate_mailing_list(client, canvas_site_id, expected_status_code=401)


def _api_activate_mailing_list(
        activate,
        canvas_site_id,
        client,
        expected_status_code=200,
):
    operation = 'activate' if activate else 'deactivate'
    response = client.get(f'/api/mailing_lists/{canvas_site_id}/welcome_email/{operation}')
    assert response.status_code == expected_status_code
    return response.json


def _api_create_mailing_list(
        client,
        canvas_site_id,
        expected_status_code=200,
        name=None,
):
    params = {'name': name} if name else {}
    response = client.post(
        f'/api/mailing_lists/{canvas_site_id}/create',
        data=json.dumps(params),
        content_type='application/json',
    )
    assert response.status_code == expected_status_code
    return response.json


def _api_find_mailing_list(client, canvas_site_id, expected_status_code=200):
    response = client.get(f'api/mailing_lists/{canvas_site_id}')
    assert response.status_code == expected_status_code
    return response.json


def _api_populate_mailing_list(client, canvas_site_id, expected_status_code=200):
    response = client.post(f'/api/mailing_lists/{canvas_site_id}/populate')
    api_json = response.json
    assert response.status_code == expected_status_code, f"""
        HTTP status code {response.status_code} != {expected_status_code}
        error: {api_json}
    """
    return api_json
