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
from ripley.externals import canvas
from ripley.models.mailing_list import MailingList
from tests.util import execute_loch_fixture_sql, register_canvas_uris

admin_uid = '10000'
no_canvas_account_uid = '10001'
not_enrolled_uid = '20000'
reader_uid = '60000'
ta_uid = '50000'
teacher_uid = '30000'
student_uid = '40000'


class TestGetMailingList:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_mailing_list(client, 1010101, expected_status_code=401)

    def test_no_canvas_account(self, client, fake_auth):
        """Denies user with no Canvas account."""
        canvas_site_id = '1234567'
        fake_auth.login(canvas_site_id=canvas_site_id, uid=no_canvas_account_uid)
        _api_mailing_list(client, canvas_site_id, expected_status_code=401)

    def test_not_enrolled(self, client, app, fake_auth):
        """Denies user with no course enrollment."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {'course': ['get_by_id_1234567'], 'user': ['profile_20000']}, m)
            canvas_site_id = '1234567'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=not_enrolled_uid)
            _api_mailing_list(client, canvas_site_id, expected_status_code=401)

    def test_admin(self, client, app, fake_auth):
        """Allows admin."""
        with requests_mock.Mocker() as m:
            canvas_site_id = 1234567
            register_canvas_uris(app, {'course': [f'get_by_id_{canvas_site_id}', f'search_users_{canvas_site_id}']}, m)
            fake_auth.login(canvas_site_id=canvas_site_id, uid=admin_uid)
            _api_create_mailing_list(
                canvas_site_id=canvas_site_id,
                client=client,
            )
            api_json = _api_mailing_list(client, canvas_site_id)

            assert api_json['canvasSite']['canvasSiteId'] == canvas_site_id
            assert api_json['canvasSite']['name'] == 'ASTRON 218: Stellar Dynamics and Galactic Structure'
            name_ = api_json['name']
            assert name_ == 'astron-218-stellar-dynamics-and-galactic-stru-sp23'

    def test_teacher(self, client, app, fake_auth):
        """Allows teacher."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'account': ['get_admins'],
                'course': ['get_by_id_1234567', 'get_user_1234567_4567890', 'search_users_1234567'],
                'user': ['profile_30000'],
            }, m)
            canvas_site_id = '1234567'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=teacher_uid)
            _api_create_mailing_list(
                canvas_site_id=canvas_site_id,
                client=client,
            )
            # Verify
            api_json = _api_mailing_list(client, canvas_site_id)
            assert api_json['name'] == 'astron-218-stellar-dynamics-and-galactic-stru-sp23'

    def test_student(self, client, app, fake_auth):
        """Denies student."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'course': ['get_by_id_1234567', 'get_user_1234567_5678901'],
                'user': ['profile_40000'],
            }, m)
            canvas_site_id = '1234567'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=student_uid)
            _api_mailing_list(client, canvas_site_id, expected_status_code=401)


class TestGetMyMailingList:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_my_mailing_list(client, expected_status_code=401)

    def test_no_canvas_account(self, client, fake_auth):
        """Denies user with no Canvas account."""
        fake_auth.login(canvas_site_id='1234567', uid=no_canvas_account_uid)
        _api_my_mailing_list(client, expected_status_code=401)

    def test_not_enrolled(self, client, app, fake_auth):
        """Denies user with no course enrollment."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {'course': ['get_by_id_1234567'], 'user': ['profile_20000']}, m)
            fake_auth.login(canvas_site_id='1234567', uid=not_enrolled_uid)
            _api_my_mailing_list(client, expected_status_code=401)

    def test_admin(self, client, app, fake_auth):
        """Allows admin."""
        with requests_mock.Mocker() as m:
            canvas_site_id = 1234567
            register_canvas_uris(app, {'course': [f'get_by_id_{canvas_site_id}', f'search_users_{canvas_site_id}']}, m)
            fake_auth.login(canvas_site_id=canvas_site_id, uid=admin_uid)
            _api_create_mailing_list(
                canvas_site_id=canvas_site_id,
                client=client,
            )
            api_json = _api_my_mailing_list(client)

            assert api_json['canvasSite']['canvasSiteId'] == canvas_site_id
            assert api_json['canvasSite']['name'] == 'ASTRON 218: Stellar Dynamics and Galactic Structure'
            name_ = api_json['name']
            assert name_ == 'astron-218-stellar-dynamics-and-galactic-stru-sp23'

    def test_teacher(self, client, app, fake_auth):
        """Allows teacher."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'account': ['get_admins'],
                'course': ['get_by_id_1234567', 'get_user_1234567_4567890', 'search_users_1234567'],
                'user': ['profile_30000'],
            }, m)
            canvas_site_id = '1234567'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=teacher_uid)
            _api_create_mailing_list(
                canvas_site_id=canvas_site_id,
                client=client,
            )
            # Verify
            api_json = _api_my_mailing_list(client)
            assert api_json['name'] == 'astron-218-stellar-dynamics-and-galactic-stru-sp23'

    def test_student(self, client, app, fake_auth):
        """Denies student."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'course': ['get_by_id_1234567', 'get_user_1234567_5678901'],
                'user': ['profile_40000'],
            }, m)
            canvas_site_id = '1234567'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=student_uid)
            _api_my_mailing_list(client, expected_status_code=401)


class TestSuggestedMailingListName:

    @classmethod
    def _api_suggested_mailing_list_name(cls, client, canvas_site_id, expected_status_code=200):
        response = client.get(f'/api/mailing_list/suggested_name/{canvas_site_id}')
        assert response.status_code == expected_status_code
        return response.json

    def test_suggested_mailing_list_name(self, app, client, fake_auth):
        with requests_mock.Mocker() as m:
            canvas_site_id = '8876542'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=admin_uid)
            register_canvas_uris(app, {'course': [f'get_by_id_{canvas_site_id}']}, m)
            suggested_name = self._api_suggested_mailing_list_name(canvas_site_id=canvas_site_id, client=client)
            assert suggested_name == 'voix-ambigue-d-un-coeur-qui-au-zephyr-prefere-sp23'

    def test_suggested_name_when_default_term(self, app, client, fake_auth):
        with requests_mock.Mocker() as m:
            canvas_site_id = '775390'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=admin_uid)
            register_canvas_uris(app, {'course': [f'get_by_id_{canvas_site_id}']}, m)
            suggested_name = self._api_suggested_mailing_list_name(canvas_site_id=canvas_site_id, client=client)
            assert suggested_name == 'general-chemistry-list'


class TestCreateMailingList:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_create_mailing_list(canvas_site_id=1010101, client=client, expected_status_code=401)

    def test_no_canvas_account(self, client, fake_auth):
        """Denies user with no Canvas account."""
        canvas_site_id = '1234567'
        fake_auth.login(canvas_site_id=canvas_site_id, uid=no_canvas_account_uid)
        _api_create_mailing_list(
            canvas_site_id=canvas_site_id,
            client=client,
            expected_status_code=401,
        )

    def test_not_enrolled(self, client, app, fake_auth):
        """Denies user with no course enrollment."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {'course': ['get_by_id_1234567'], 'user': ['profile_20000']}, m)
            canvas_site_id = '1234567'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=not_enrolled_uid)
            _api_create_mailing_list(
                canvas_site_id=canvas_site_id,
                client=client,
                expected_status_code=401,
            )

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
                    canvas_site_id=canvas_site_id,
                    client=client,
                    name=mailing_list_name,
                )
                mailing_list_id = api_json['id']
                assert api_json['canvasSite']['canvasSiteId'] == 1234567
                assert api_json['canvasSite']['name'] == 'ASTRON 218: Stellar Dynamics and Galactic Structure'
                if mailing_list_name:
                    assert api_json['name'] == mailing_list_name
                else:
                    assert api_json['name'] == 'astron-218-stellar-dynamics-and-galactic-stru-sp23'

                # But you can't step into the same mailing list twice.
                _api_create_mailing_list(
                    canvas_site_id=canvas_site_id,
                    client=client,
                    expected_status_code=400,
                )
                # Name conflicts also disallowed.
                _api_create_mailing_list(
                    canvas_site_id=canvas_site_id,
                    client=client,
                    name='astron-218-stellar-dynamics-and-galactic-stru-sp23',
                    expected_status_code=400,
                )

    def test_teacher(self, client, app, fake_auth):
        """Allows teacher."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'account': ['get_admins'],
                'course': ['get_by_id_1234567', 'get_user_1234567_4567890', 'search_users_1234567'],
                'user': ['profile_30000'],
            }, m)
            canvas_site_id = '1234567'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=teacher_uid)
            api_json = _api_create_mailing_list(
                canvas_site_id=canvas_site_id,
                client=client,
            )
            assert api_json['name'] == 'astron-218-stellar-dynamics-and-galactic-stru-sp23'

    def test_student(self, client, app, fake_auth):
        """Denies student."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'course': ['get_by_id_1234567', 'get_user_1234567_5678901', 'search_users_1234567'],
                'user': ['profile_40000'],
            }, m)
            canvas_site_id = '1234567'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=student_uid)
            _api_create_mailing_list(
                canvas_site_id=canvas_site_id,
                client=client,
                expected_status_code=401,
            )


class TestActivateMailingList:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_activate_mailing_list(
            activate=True,
            client=client,
            expected_status_code=401,
        )

    def test_unauthorized(self, client, fake_auth):
        """Student cannot activate a mailing list."""
        canvas_site_id = '1234567'
        fake_auth.login(canvas_site_id=canvas_site_id, uid=student_uid)
        _api_activate_mailing_list(
            activate=True,
            client=client,
            expected_status_code=401,
        )

    def test_authorized(self, app, client, fake_auth):
        """Teacher can activate a mailing list."""
        with requests_mock.Mocker() as m:
            canvas_site_id = '8876542'
            register_canvas_uris(app, {
                'course': [f'get_by_id_{canvas_site_id}', f'get_sections_{canvas_site_id}', 'get_enrollments_4567890'],
                'user': ['profile_30000'],
            }, m)
            fake_auth.login(canvas_site_id=canvas_site_id, uid=admin_uid)
            canvas_site = canvas.get_course(canvas_site_id)
            mailing_list = MailingList.create(
                canvas_site=canvas_site,
                list_name='Wonder Twin powers activate!',
                welcome_email_body='Body',
                welcome_email_subject='Subject',
            )
            assert mailing_list.welcome_email_active is False
            api_json = _api_activate_mailing_list(
                activate=True,
                client=client,
            )
            assert api_json['welcomeEmailActive'] is True
            api_json = _api_activate_mailing_list(
                activate=False,
                client=client,
            )
            assert api_json['welcomeEmailActive'] is False


class TestPopulateMailingList:

    @classmethod
    def _api_populate_mailing_list(cls, client, mailing_list_id, expected_status_code=200):
        response = client.post(f'/api/mailing_list/{mailing_list_id}/populate')
        api_json = response.json
        assert response.status_code == expected_status_code, f"""
            HTTP status code {response.status_code} != {expected_status_code}
            error: {api_json}
        """
        return api_json

    def test_anonymous(self, client):
        """Denies anonymous user."""
        self._api_populate_mailing_list(client, 1, expected_status_code=401)

    def test_no_canvas_account(self, client, fake_auth):
        """Denies user with no Canvas account."""
        canvas_site_id = '1234567'
        fake_auth.login(canvas_site_id=canvas_site_id, uid=no_canvas_account_uid)
        self._api_populate_mailing_list(client, 1, expected_status_code=401)

    def test_students_cannot_edit_mailing_list(self, client, app, fake_auth):
        """Denies student access to mailing_list."""
        with requests_mock.Mocker() as m:
            canvas_site_id = '1234567'
            uid_of_student = 40000
            register_canvas_uris(
                app,
                {'course': [f'get_by_id_{canvas_site_id}'], 'user': [f'profile_{uid_of_student}']},
                m,
            )
            canvas_site = canvas.get_course(canvas_site_id)
            mailing_list = MailingList.create(canvas_site)
            fake_auth.login(canvas_site_id=canvas_site_id, uid=uid_of_student)
            self._api_populate_mailing_list(client, mailing_list_id=mailing_list.id, expected_status_code=401)

    def test_authorized(self, client, app, fake_auth):
        """Allows admin to manage mailing list."""
        with requests_mock.Mocker() as m:
            canvas_site_id = 1234567
            register_canvas_uris(app, {
                'account': ['get_admins'],
                'course': [f'get_by_id_{canvas_site_id}', f'search_users_{canvas_site_id}'],
                'user': [f'profile_{admin_uid}'],
            }, m)
            fake_auth.login(canvas_site_id=canvas_site_id, uid=admin_uid)
            api_json = _api_create_mailing_list(
                canvas_site_id=canvas_site_id,
                client=client,
            )
            mailing_list_id = api_json['id']
            api_json = self._api_populate_mailing_list(client, mailing_list_id=mailing_list_id)

            # Verify
            expected_email_address = 'synthetic.ash@berkeley.edu'
            assert api_json['mailingList']['canvasSite']['canvasSiteId'] == canvas_site_id
            added = api_json['summary']['add']
            assert added['total'] == 1
            assert added['successes'][0] == expected_email_address
            for key in ['remove', 'restore', 'update', 'welcomeEmails']:
                assert api_json['summary'][key]['total'] == 0

            def _update_email_address_in_loch(email_address):
                execute_loch_fixture_sql(
                    app,
                    sql=f"""
                        UPDATE sis_data.basic_attributes
                        SET email_address = '{email_address}'
                        WHERE ldap_uid = '30000'
                    """,
                )
            # Alter email address
            interim_email_address = 'polystyrene.ash@berkeley.edu'
            _update_email_address_in_loch(interim_email_address)
            # Re-populate mailing list
            api_json = self._api_populate_mailing_list(client, mailing_list_id=mailing_list_id)
            assert api_json
            # TODO: Make it work! We expect an update to existing record.
            the_feature_works_as_expected = False
            if the_feature_works_as_expected:
                updated = api_json['summary']['update']
                assert updated['total'] == 1
                assert updated['successes'][0] == interim_email_address
                for key in ['add', 'remove', 'restore', 'welcomeEmails']:
                    assert api_json['summary'][key]['total'] == 0

            # Reset email address. We are done.
            _update_email_address_in_loch(expected_email_address)

    def test_teacher(self, client, app, fake_auth):
        """Allows teacher."""
        with requests_mock.Mocker() as m:
            canvas_site_id = 1234567
            uid = teacher_uid
            register_canvas_uris(app, {
                'account': ['get_admins'],
                'course': [
                    f'get_by_id_{canvas_site_id}',
                    f'get_user_{canvas_site_id}_4567890',
                    f'search_users_{canvas_site_id}',
                ],
                'user': [f'profile_{uid}'],
            }, m)
            fake_auth.login(canvas_site_id=canvas_site_id, uid=uid)
            api_json = _api_create_mailing_list(
                canvas_site_id=canvas_site_id,
                client=client,
            )
            api_json = self._api_populate_mailing_list(client, mailing_list_id=api_json['id'])
            assert api_json['mailingList']['name'] == 'astron-218-stellar-dynamics-and-galactic-stru-sp23'
            # TODO: verify populated mailing list

    def test_student(self, client, app, fake_auth):
        """Denies student."""
        with requests_mock.Mocker() as m:
            canvas_site_id = '1234567'
            register_canvas_uris(app, {
                'course': [f'get_by_id_{canvas_site_id}', f'get_user_{canvas_site_id}_5678901'],
                'user': [f'profile_{student_uid}'],
            }, m)
            canvas_site = canvas.get_course(canvas_site_id)
            mailing_list = MailingList.create(canvas_site)
            fake_auth.login(canvas_site_id=canvas_site_id, uid=student_uid)
            self._api_populate_mailing_list(client, expected_status_code=401, mailing_list_id=mailing_list.id)


class TestUpdateWelcomeEmail:

    @classmethod
    def _api_welcome_email_update(cls, body, client, subject, active=False, expected_status_code=200):
        response = client.post(
            '/api/mailing_list/welcome_email/update',
            data=json.dumps({
                'active': active,
                'body': body,
                'subject': subject,
            }),
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
            self._api_welcome_email_update(
                subject='Lightning strikes',
                body='...Maybe once, maybe twice',
                client=client,
                expected_status_code=401,
            )

    def test_authorized(self, client, app, fake_auth):
        """Allows authorized user to update mailing list."""
        with requests_mock.Mocker() as m:
            canvas_site_id = '1234567'
            uid = teacher_uid
            register_canvas_uris(app, {
                'account': ['get_admins'],
                'course': [
                    f'get_by_id_{canvas_site_id}',
                    f'get_user_{canvas_site_id}_4567890',
                    f'search_users_{canvas_site_id}'],
                'user': [f'profile_{uid}'],
            }, m)
            fake_auth.login(canvas_site_id=canvas_site_id, uid=uid)
            # Expect 404. The mailing list does not exist.
            self._api_welcome_email_update(
                body="This ain't gonna work",
                client=client,
                expected_status_code=404,
                subject='Doomed to fail',
            )
            # Create the mailing list.
            canvas_site = canvas.get_course(canvas_site_id)
            mailing_list = MailingList.create(
                canvas_site=canvas_site,
                list_name='Gypsy',
                welcome_email_body="So I'm back to the velvet underground",
                welcome_email_subject='Back to that floor I love',
            )
            # Update the welcome email.
            body = 'To a room with some lace and paper flowers'
            subject = 'Back to the gypsy that I was'
            api_json = self._api_welcome_email_update(
                body=body,
                client=client,
                subject=subject,
            )
            assert api_json['id'] == mailing_list.id
            assert api_json['name'] == 'Gypsy'
            assert api_json['welcomeEmailBody'] == body
            assert api_json['welcomeEmailSubject'] == subject


def _api_activate_mailing_list(
        activate,
        client,
        expected_status_code=200,
):
    operation = 'activate' if activate else 'deactivate'
    response = client.get(f'/api/mailing_list/welcome_email/{operation}')
    assert response.status_code == expected_status_code
    return response.json


def _api_create_mailing_list(
        canvas_site_id,
        client,
        expected_status_code=200,
        name=None,
):
    params = {'canvasSiteId': canvas_site_id}
    if name:
        params['name'] = name
    response = client.post(
        '/api/mailing_list/create',
        data=json.dumps(params),
        content_type='application/json',
    )
    assert response.status_code == expected_status_code
    return response.json


def _api_mailing_list(client, canvas_site_id, expected_status_code=200):
    response = client.get(f'/api/mailing_list/{canvas_site_id}')
    assert response.status_code == expected_status_code
    return response.json


def _api_my_mailing_list(client, expected_status_code=200):
    response = client.get('/api/mailing_list/my')
    assert response.status_code == expected_status_code
    return response.json
