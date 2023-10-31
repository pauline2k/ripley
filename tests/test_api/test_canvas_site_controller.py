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

TERM_ID_CURRENT = '2232'
TERM_ID_NEXT = '2235'

admin_uid = '10000'
faculty_uid = '90000'
no_canvas_account_uid = '10001'
not_enrolled_uid = '20000'
reader_uid = '60000'
student_uid = '40000'
ta_uid = '50000'
teacher_uid = '30000'


class TestViewOfficialSections:

    EMPTY_OFFICIAL_SECTIONS_FEED = {TERM_ID_CURRENT: [], TERM_ID_NEXT: []}

    @classmethod
    def _api_canvas_site_official_sections(cls, client, expected_status_code=200):
        response = client.get('/api/canvas_site/manage_official_sections')
        assert response.status_code == expected_status_code
        return response.json

    def test_anonymous(self, client):
        """Denies anonymous user."""
        self._api_canvas_site_official_sections(client, expected_status_code=401)

    def test_no_canvas_account(self, client, app, fake_auth):
        """Denies user with no Canvas account."""
        with requests_mock.Mocker() as m:
            canvas_site_id = '8876542'
            register_canvas_uris(app, {'course': [f'get_by_id_{canvas_site_id}']}, m)
            fake_auth.login(canvas_site_id=canvas_site_id, uid=no_canvas_account_uid)
            self._api_canvas_site_official_sections(client, expected_status_code=401)

    def test_reader(self, client, app, fake_auth):
        """Official sections view is not available to Reader role."""
        with requests_mock.Mocker() as m:
            canvas_site_id = '8876542'
            uid = reader_uid
            register_canvas_uris(app, {
                'account': ['get_admins', 'get_by_id'],
                'course': [
                    f'get_by_id_{canvas_site_id}',
                    f'get_enrollments_{canvas_site_id}_7890123',
                    f'get_sections_{canvas_site_id}',
                ],
                'user': [f'profile_{uid}'],
            }, m)
            fake_auth.login(canvas_site_id=canvas_site_id, uid=uid)
            assert self._api_canvas_site_official_sections(client) == self.EMPTY_OFFICIAL_SECTIONS_FEED

    def test_teaching_roles(self, client, app, fake_auth):
        """Official sections view is available teaching roles."""
        with requests_mock.Mocker() as m:
            canvas_user_ids = {
                ta_uid: 6789012,
                teacher_uid: 4567890,
            }
            for uid in [ta_uid, teacher_uid]:
                canvas_site_id = 8876542
                register_canvas_uris(app, {
                    'account': ['get_admins', 'get_by_id'],
                    'course': [
                        f'get_by_id_{canvas_site_id}',
                        f'get_enrollments_{canvas_site_id}_{canvas_user_ids[uid]}',
                        f'get_sections_{canvas_site_id}',
                    ],
                    'user': [
                        f'profile_{uid}',
                        f'user_courses_{uid}',
                    ],
                }, m)
                fake_auth.login(canvas_site_id=canvas_site_id, uid=uid)
                api_json = self._api_canvas_site_official_sections(client)
                assert TERM_ID_CURRENT in api_json
                current_term_courses = api_json[TERM_ID_CURRENT]
                assert len(current_term_courses) == 1
                assert current_term_courses[0]['canvasSiteId'] == canvas_site_id

    def test_teacher_no_section_ids(self, client, app, fake_auth):
        """Teacher without sections gets empty feed."""
        with requests_mock.Mocker() as m:
            uid = teacher_uid
            canvas_site_id = '8876542'
            register_canvas_uris(app, {
                'account': ['get_admins'],
                'course': [
                    f'get_by_id_{canvas_site_id}',
                    f'get_sections_{canvas_site_id}',
                    f'get_enrollments_{canvas_site_id}_4567890',
                ],
                'user': [f'profile_{uid}'],
            }, m)
            fake_auth.login(canvas_site_id=canvas_site_id, uid=uid)
            sections = self._api_canvas_site_official_sections(client)
            assert sections == self.EMPTY_OFFICIAL_SECTIONS_FEED


class TestEditOfficialSections:

    @classmethod
    def _api_edit_official_sections(cls, client, canvas_site_id, params=None, expected_status_code=200):
        data = {
            'sectionIdsToAdd': [],
            'sectionIdsToRemove': [],
            'sectionIdsToUpdate': [],
        }
        data.update(params or {})
        response = client.post(
            f'/api/canvas_site/{canvas_site_id}/provision/sections',
            data=json.dumps(data),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_anonymous(self, client):
        """Denies anonymous user."""
        self._api_edit_official_sections(client, '8876542', expected_status_code=401)

    def test_no_canvas_account(self, client, app, fake_auth):
        """Denies user with no Canvas account."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {'course': ['get_by_id_8876542']}, m)
            canvas_site_id = '8876542'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=no_canvas_account_uid)
            self._api_edit_official_sections(client, canvas_site_id, expected_status_code=401)

    def test_reader(self, client, app, fake_auth):
        """Denies Reader."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'account': ['get_admins', 'get_by_id'],
                'course': ['get_by_id_8876542', 'get_sections_8876542', 'get_enrollments_8876542_7890123'],
                'user': ['profile_60000'],
            }, m)
            canvas_site_id = '8876542'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=reader_uid)
            self._api_edit_official_sections(client, canvas_site_id, expected_status_code=401)

    def test_ta(self, client, app, fake_auth):
        """Denies TA."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'account': ['get_admins', 'get_by_id'],
                'course': ['get_by_id_8876542', 'get_sections_8876542', 'get_enrollments_8876542_6789012'],
                'user': ['profile_50000'],
            }, m)
            canvas_site_id = '8876542'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=ta_uid)
            self._api_edit_official_sections(client, canvas_site_id, expected_status_code=401)

    def test_teacher(self, client, app, fake_auth):
        """Allows teacher."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'account': ['create_sis_import', 'get_admins', 'get_by_id', 'get_sis_import'],
                'course': ['get_by_id_8876542', 'get_sections_8876542', 'get_enrollments_8876542_4567890'],
                'user': ['profile_30000'],
            }, m)
            canvas_site_id = '8876542'
            params = {
                'sectionIdsToAdd': ['12345'],
            }
            fake_auth.login(canvas_site_id=canvas_site_id, uid=teacher_uid)
            self._api_edit_official_sections(client, canvas_site_id, params=params)

    def test_teacher_no_section_ids(self, client, app, fake_auth):
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'account': ['get_admins'],
                'course': ['get_by_id_8876542', 'get_sections_8876542', 'get_enrollments_8876542_4567890'],
                'user': ['profile_30000'],
            }, m)
            canvas_site_id = '8876542'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=teacher_uid)
            self._api_edit_official_sections(client, canvas_site_id, expected_status_code=400)


class TestCanvasSiteProvision:

    @classmethod
    def _api_canvas_course_provision(cls, client, params=None, expected_status_code=200):
        path = '/api/canvas_site/provision'
        if params:
            path += f'?{"&".join([k + "=" + v for k, v in params.items()])}'
        response = client.get(path)
        assert response.status_code == expected_status_code
        return response.json

    def test_anonymous(self, client):
        """Denies anonymous user."""
        self._api_canvas_course_provision(client, expected_status_code=401)

    def test_teacher(self, client, app, fake_auth):
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'account': ['get_admins', 'get_terms'],
                'course': ['get_by_id_8876542', 'get_sections_8876542', 'get_enrollments_8876542_4567890'],
                'user': ['profile_30000'],
            }, m)
            fake_auth.login(canvas_site_id=None, uid=teacher_uid)
            feed = self._api_canvas_course_provision(client)
            assert feed['teachingTerms'][0]['name'] == 'Spring 2023'
            assert feed['teachingTerms'][0]['classes'][0]['courseCode'] == 'ANTHRO 189'

    def test_admin_acting_as_teacher(self, client, app, fake_auth):
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'account': ['get_admins', 'get_terms'],
                'course': ['get_by_id_8876542', 'get_sections_8876542', 'get_enrollments_8876542_4567890'],
                'user': ['profile_30000', f'profile_{admin_uid}'],
            }, m)
            fake_auth.login(canvas_site_id=None, uid=admin_uid)
            feed = self._api_canvas_course_provision(client, params={'adminActingAs': teacher_uid, 'adminTermSlug': 'spring-2023'})
            assert feed['teachingTerms'][0]['name'] == 'Spring 2023'
            assert feed['teachingTerms'][0]['classes'][0]['courseCode'] == 'ANTHRO 189'

    def test_admin_requesting_ccns(self, client, app, fake_auth):
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'account': ['get_admins', 'get_terms'],
                'course': ['get_by_id_8876542', 'get_sections_8876542', 'get_enrollments_8876542_4567890'],
                'user': ['profile_30000', f'profile_{admin_uid}'],
            }, m)
            fake_auth.login(canvas_site_id=None, uid=admin_uid)
            feed = self._api_canvas_course_provision(client, params={'adminBySectionIds[]': '32936', 'adminTermSlug': 'spring-2023'})
            assert feed['teachingTerms'][0]['name'] == 'Spring 2023'
            assert feed['teachingTerms'][0]['classes'][0]['courseCode'] == 'ANTHRO 189'


class TestCanvasSiteProvisionSections:

    @classmethod
    def _api_canvas_course_provision_sections(cls, client, canvas_site_id, expected_status_code=200):
        response = client.get(f'/api/canvas_site/{canvas_site_id}/official_sections')
        assert response.status_code == expected_status_code
        return response.json

    def test_anonymous(self, client):
        """Denies anonymous user."""
        self._api_canvas_course_provision_sections(client, '8876542', expected_status_code=401)

    def test_no_canvas_account(self, client, app, fake_auth):
        """Denies user with no Canvas account."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {'course': ['get_by_id_8876542']}, m)
            canvas_site_id = '8876542'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=no_canvas_account_uid)
            self._api_canvas_course_provision_sections(client, canvas_site_id, expected_status_code=401)

    def test_not_enrolled(self, client, app, fake_auth):
        """Denies user with no course enrollment."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {'course': ['get_by_id_8876542'], 'user': ['profile_20000']}, m)
            canvas_site_id = '8876542'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=not_enrolled_uid)
            self._api_canvas_course_provision_sections(client, canvas_site_id, expected_status_code=401)

    def test_student(self, client, app, fake_auth):
        """Denies user with no course enrollment."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {'course': ['get_by_id_8876542'], 'user': [f'profile_{student_uid}']}, m)
            canvas_site_id = '8876542'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=student_uid)
            self._api_canvas_course_provision_sections(client, canvas_site_id, expected_status_code=401)

    def test_reader(self, client, app, fake_auth):
        """Denies Reader."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'account': ['get_admins', 'get_terms'],
                'course': ['get_by_id_8876542', 'get_sections_8876542', 'get_enrollments_8876542_7890123'],
                'user': ['profile_60000'],
            }, m)
            canvas_site_id = '8876542'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=reader_uid)
            self._api_canvas_course_provision_sections(client, canvas_site_id, expected_status_code=401)

    def test_ta(self, client, app, fake_auth):
        """Allows TA, read-only."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'account': ['get_admins', 'get_terms'],
                'course': ['get_by_id_8876542', 'get_sections_8876542', 'get_enrollments_8876542_6789012'],
                'user': ['profile_50000'],
            }, m)
            canvas_site_id = '8876542'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=ta_uid)
            response = self._api_canvas_course_provision_sections(client, canvas_site_id)
            assert response['canvasSite']
            assert response['canvasSite']['canEdit'] is False
            assert response['canvasSite']['term'] == {
                'id': '2232',
                'name': 'Spring 2023',
                'season': 'B',
                'year': '2023',
            }
            assert len(response['canvasSite']['officialSections']) == 2
            section = response['canvasSite']['officialSections'][0]
            assert section['canvasName'] == 'Section A'
            assert section['id'] == '32936'
            assert section['name'] == 'LEC 001 (In Person)'
            assert section['sisId'] == 'SEC:2023-B-32936'
            assert section['termId'] == '2232'
            assert len(response['teachingTerms']) == 1

    def test_teacher(self, client, app, fake_auth):
        """Allows teacher."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'account': ['get_admins', 'get_terms'],
                'course': ['get_by_id_8876542', 'get_sections_8876542', 'get_enrollments_8876542_4567890'],
                'user': ['profile_30000'],
            }, m)
            canvas_site_id = '8876542'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=teacher_uid)
            response = self._api_canvas_course_provision_sections(client, canvas_site_id)
            assert response['canvasSite']
            assert response['canvasSite']['canEdit'] is True
            assert response['canvasSite']['term'] == {
                'id': '2232',
                'name': 'Spring 2023',
                'season': 'B',
                'year': '2023',
            }
            # Official sections
            assert len(response['canvasSite']['officialSections']) == 2
            section = response['canvasSite']['officialSections'][0]
            assert section['canvasName'] == 'Section A'
            assert section['courseCode'] == 'ANTHRO 189'
            assert section['id'] == '32936'
            assert section['instructionFormat'] == 'LEC'
            assert section['instructionMode'] == 'In Person'
            assert section['isPrimarySection'] is True
            assert section['name'] == 'LEC 001 (In Person)'
            assert section['schedules']
            assert section['sectionNumber'] == '001'
            assert section['sisId'] == 'SEC:2023-B-32936'
            assert section['termId'] == '2232'

            # All available sections
            assert len(response['teachingTerms']) == 1
            spring_term = response['teachingTerms'][0]
            assert spring_term['name'] == 'Spring 2023'
            assert spring_term['slug'] == 'spring-2023'
            assert spring_term['termId'] == '2232'
            assert spring_term['termYear'] == '2023'
            assert len(spring_term['classes']) == 2
            course = next(c for c in spring_term['classes'] if c['courseCode'] == 'ASTRON 218')
            assert course['title'] == 'Stellar Dynamics and Galactic Structure'
            assert len(course['sections']) == 3
            sections = course['sections']
            assert sections[0]['courseCode'] == 'ASTRON 218'
            assert sections[0]['id'] == '12345'
            assert sections[0]['instructionFormat'] == 'LEC'
            assert sections[0]['instructionMode'] == 'In Person'
            assert sections[0]['instructors'] == [
                {
                    'name': 'Ash',
                    'role': 'PI',
                    'uid': '30000',
                },
            ]
            assert sections[0]['isPrimarySection'] is True
            assert sections[0]['schedules']['oneTime'] == [
                {
                    'buildingName': 'Sevastopol Station',
                    'date': 'SaMW 2023-02-17',
                },
            ]
            assert sections[0]['schedules']['recurring'] == []
            assert sections[0]['sectionNumber'] == '001'

            assert sections[1]['courseCode'] == 'ASTRON 218'
            assert sections[1]['id'] == '12346'
            assert sections[1]['instructionFormat'] == 'LEC'
            assert sections[1]['instructionMode'] == 'In Person'
            assert sections[1]['instructors'] == [
                {
                    'name': 'Ash',
                    'role': 'PI',
                    'uid': '30000',
                },
                {
                    'name': 'Fitzi Ritz',
                    'role': 'PI',
                    'uid': '13579',
                },
            ]
            assert sections[1]['isPrimarySection'] is True
            assert sections[1]['schedules']['oneTime'] == []
            assert sections[1]['schedules']['recurring'] == [
                {
                    'buildingName': 'Acheron LV',
                    'meetingDays': 'TUTH',
                    'meetingEndTime': '13:30',
                    'meetingStartTime': '09:00',
                    'roomNumber': '426',
                    'schedule': 'TuTh 9:00A-1:30P',
                },
                {
                    'buildingName': None,
                    'meetingDays': 'TUTH',
                    'meetingEndTime': '13:30',
                    'meetingStartTime': '09:00',
                    'roomNumber': None,
                    'schedule': 'TuTh 9:00A-1:30P',
                },
            ]
            assert sections[1]['sectionNumber'] == '002'
            assert sections[2]['id'] == '12347'
            assert sections[2]['instructionFormat'] == 'DIS'
            assert sections[2]['isPrimarySection'] is False
            assert sections[2]['instructors'] == [
                {
                    'name': 'Mufty Blauswater',
                    'role': 'PI',
                    'uid': '200122',
                },
            ]
            assert sections[2]['schedules']['oneTime'] == []
            assert sections[2]['schedules']['recurring'] == [
                {
                    'buildingName': 'Sevastopol Station',
                    'meetingDays': 'TU',
                    'meetingEndTime': '15:00',
                    'meetingStartTime': '14:00',
                    'roomNumber': None,
                    'schedule': 'Tu 2:00P-3:00P',
                },
            ]
            assert sections[2]['sectionNumber'] == '101'
            assert course['slug'] == 'astron-218-2023-B'

    def test_admin(self, client, app, fake_auth):
        """Allows admin."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'account': ['get_admins', 'get_terms'],
                'course': ['get_by_id_8876542', 'get_sections_8876542', 'get_enrollments_8876542_4567890'],
                'user': [f'profile_{admin_uid}'],
            }, m)
            canvas_site_id = '8876542'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=admin_uid)
            response = self._api_canvas_course_provision_sections(client, canvas_site_id)
            assert response['canvasSite']
            assert response['canvasSite']['canEdit'] is False
            # Official sections
            assert len(response['canvasSite']['officialSections']) == 2
            # All available sections
            assert len(response['teachingTerms']) == 1
            spring_term = response['teachingTerms'][0]
            assert spring_term['name'] == 'Spring 2023'
            assert len(spring_term['classes']) == 1
            assert spring_term['classes'][0]
            assert spring_term['classes'][0]['slug'] == 'anthro-189-2023-B'


class TestCreateCourseSite:

    @classmethod
    def _api_create_course_site(cls, client, params=None, expected_status_code=200):
        response = client.post(
            '/api/canvas_site/provision/create',
            data=json.dumps(params or {}),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    @classmethod
    def _api_get_creation_job_status(cls, client, job_id, expected_status_code=200):
        response = client.get(f'/api/canvas_site/provision/status?jobId={job_id}')
        print(response.json)
        assert response.status_code == expected_status_code
        return response.json

    def test_anonymous(self, client):
        """Denies anonymous user."""
        self._api_create_course_site(client, expected_status_code=401)
        self._api_get_creation_job_status(client, '1234', expected_status_code=401)

    def test_unauthorized_users(self, client, app, fake_auth):
        """Denies Reader."""
        with requests_mock.Mocker() as m:
            account_id = '129407'
            canvas_site_id = '8876542'
            for unauthorized_uid, user_description in {
                not_enrolled_uid: 'Non-enrolled user',
                reader_uid: 'Reader',
                student_uid: 'Student',
                ta_uid: 'TA',
            }.items():
                has_canvas_account = unauthorized_uid != no_canvas_account_uid
                register_canvas_uris(app, {
                    'account': ['get_admins', f'get_courses_{account_id}'],
                    'course': [f'get_by_id_{canvas_site_id}', f'get_sections_{canvas_site_id}', 'get_enrollments_8876542_4567890'],
                    'user': [f'profile_{unauthorized_uid}'] if has_canvas_account else [],
                }, m)
                fake_auth.login(canvas_site_id=canvas_site_id, uid=unauthorized_uid)
                self._api_create_course_site(client, expected_status_code=401)
                self._api_get_creation_job_status(client, '1234', expected_status_code=401)

    def test_create_course_site_teacher(self, client, app, fake_auth):
        """Allows teacher."""
        with requests_mock.Mocker() as m:
            canvas_site_id = '8876542'
            register_canvas_uris(app, {
                'account': ['get_admins'],
                'course': [f'get_by_id_{canvas_site_id}'],
                'user': [f'profile_{teacher_uid}'],
            }, m)
            fake_auth.login(canvas_site_id=canvas_site_id, uid=teacher_uid)
            api_json = self._api_create_course_site(
                client,
                params={'sectionIds': [10000]},
            )
            assert api_json['jobId']
            assert api_json['jobStatus'] == 'sendingRequest'

            api_json = self._api_get_creation_job_status(client, api_json['jobId'])
            assert api_json['jobStatus']


class TestCreateProjectSite:

    @classmethod
    def _api_create_project_site(cls, client, name, expected_status_code=200, failed_assertion_message=None):
        response = client.post(
            '/api/canvas_site/project_site/create',
            data=json.dumps({'name': name}),
            content_type='application/json',
        )
        assert response.status_code == expected_status_code
        return response.json

    def test_anonymous(self, client):
        """Denies anonymous user."""
        self._api_create_project_site(client, 'Sorry Charlie', expected_status_code=401)

    def test_unauthorized_users(self, client, app, fake_auth):
        """Denies Reader."""
        with requests_mock.Mocker() as m:
            account_id = '129407'
            canvas_site_id = '8876542'
            for unauthorized_uid, user_description in {
                no_canvas_account_uid: 'User with no Canvas account',
                not_enrolled_uid: 'Non-enrolled user',
                reader_uid: 'Reader',
                student_uid: 'Student',
                ta_uid: 'TA',
                teacher_uid: 'Teacher',
            }.items():
                has_canvas_account = unauthorized_uid != no_canvas_account_uid
                register_canvas_uris(app, {
                    'account': ['get_admins', f'get_courses_{account_id}'],
                    'course': [f'get_by_id_{canvas_site_id}', f'get_sections_{canvas_site_id}', 'get_enrollments_8876542_4567890'],
                    'user': [f'profile_{unauthorized_uid}'] if has_canvas_account else [],
                }, m)
                fake_auth.login(canvas_site_id=canvas_site_id, uid=unauthorized_uid)
                self._api_create_project_site(
                    client,
                    'Sorry Charlie',
                    expected_status_code=401,
                    failed_assertion_message=f'Do not allow {user_description} (UID: {unauthorized_uid}) to create project site.',
                )

    def test_authorized_users(self, client, app, fake_auth):
        """Allows faculty."""
        with requests_mock.Mocker() as m:
            account_id = '129407'
            canvas_site_id = '8876542'
            project_site_id = '3030303'
            for unauthorized_uid, user_description in {
                faculty_uid: 'Faculty',
                admin_uid: 'Admin user',
            }.items():
                register_canvas_uris(app, {
                    'account': [
                        'get_admins',
                        f'get_by_id_{account_id}',
                        f'get_roles_{account_id}',
                        f'get_courses_{account_id}',
                    ],
                    'course': [
                        f'get_by_id_{canvas_site_id}',
                        f'get_by_id_{project_site_id}',
                        f'get_content_migrations_{project_site_id}',
                        'get_enrollments_8876542_4567890',
                        f'get_sections_{canvas_site_id}',
                        f'get_tabs_{project_site_id}',
                        'post_course_enrollments_3030303',
                    ],
                    'user': [f'profile_{unauthorized_uid}'],
                }, m)
                fake_auth.login(canvas_site_id=canvas_site_id, uid=unauthorized_uid)
                api_json = self._api_create_project_site(
                    client,
                    'My project site',
                    failed_assertion_message=f'{user_description} (UID: {unauthorized_uid}) should have power to create a project site.',
                )
                assert api_json


class TestGetRoster:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_get_roster(client, '8876542', expected_status_code=401)

    def test_no_canvas_account(self, client, fake_auth):
        """Denies user with no Canvas account."""
        canvas_site_id = '8876542'
        fake_auth.login(canvas_site_id=canvas_site_id, uid=no_canvas_account_uid)
        _api_get_roster(client, canvas_site_id, expected_status_code=401)

    def test_not_enrolled(self, client, app, fake_auth):
        """Denies user with no course enrollment."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {'course': ['get_by_id_8876542'], 'user': ['profile_20000']}, m)
            canvas_site_id = '8876542'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=not_enrolled_uid)
            _api_get_roster(client, canvas_site_id, expected_status_code=401)

    def test_reader(self, client, app, fake_auth):
        """Denies Reader."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'account': ['get_admins'],
                'course': ['get_by_id_8876542', 'get_sections_8876542', 'get_enrollments_8876542_7890123'],
                'user': ['profile_60000'],
            }, m)
            canvas_site_id = '8876542'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=reader_uid)
            _api_get_roster(client, canvas_site_id, expected_status_code=401)

    def test_ta(self, client, app, fake_auth):
        """Allows TA."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'account': ['get_admins'],
                'course': ['get_by_id_8876542', 'get_sections_8876542', 'get_enrollments_8876542_6789012'],
                'user': ['profile_50000'],
            }, m)
            canvas_site_id = '8876542'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=ta_uid)
            response = _api_get_roster(client, canvas_site_id)

            assert len(response['sections']) == 2
            assert len(response['students']) == 4

    def test_admin(self, client, app, fake_auth):
        """Allows admin."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'account': ['get_admins'],
                'course': ['get_by_id_8876542', 'get_sections_8876542', 'get_enrollments_8876542_4567890'],
                'user': ['profile_10000'],
            }, m)
            canvas_site_id = '8876542'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=admin_uid)
            response = _api_get_roster(client, canvas_site_id)

            assert len(response['sections']) == 2
            section = response['sections'][0]
            assert section['id'] == '32936'
            assert section['name'] == 'Section A'
            assert section['sisId'] == 'SEC:2023-B-32936'
            students = response['students']
            assert len(students) == 4

            # Verify sort order
            previous_last_name = ''
            for student in students:
                assert previous_last_name < student['lastName']
            # Verify contents of sample student
            student = next((s for s in students if s['id'] == '20000'), None)
            assert student
            assert student['email'] == 'joan.lambert@berkeley.edu'
            assert student['enrollStatus'] == 'E'
            assert student['firstName'] == 'Joan'
            assert student['id'] == '20000'
            assert student['lastName'] == 'Lambert'
            assert student['uid'] == '20000'
            assert student['photoUrl'].startswith('https://photo-bucket.s3.amazonaws.com/photos/20000.jpg?AWSAccessKeyId=')
            assert student['studentId'] == '30020000'
            assert len(student['sections']) == 2
            assert student['sections'][0]['id'] == '32936'
            assert student['sections'][0]['name'] == 'Section A'
            assert student['sections'][0]['sisId'] == 'SEC:2023-B-32936'
            assert student['sections'][1]['id'] == '32937'
            assert student['sections'][1]['name'] == 'Section B'
            assert student['sections'][1]['sisId'] == '2023-B-32937'

    def test_teacher(self, client, app, fake_auth):
        """Allows teacher."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'account': ['get_admins'],
                'course': ['get_by_id_8876542', 'get_sections_8876542', 'get_enrollments_8876542_4567890'],
                'user': ['profile_30000'],
            }, m)
            canvas_site_id = '8876542'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=teacher_uid)
            response = _api_get_roster(client, canvas_site_id)

            assert len(response['sections']) == 2
            assert len(response['students']) == 4

    def test_student(self, client, app, fake_auth):
        """Denies student."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'account': ['get_admins'],
                'course': ['get_by_id_8876542', 'get_sections_8876542', 'get_enrollments_8876542_4567890'],
                'user': ['profile_40000'],
            }, m)
            canvas_site_id = '8876542'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=student_uid)
            _api_get_roster(client, canvas_site_id, expected_status_code=401)


def _api_export_roster(client, canvas_site_id, expected_status_code=200):
    response = client.get(f'/api/canvas_site/{canvas_site_id}/export_roster')
    assert response.status_code == expected_status_code
    return response.json


def _api_get_roster(client, canvas_site_id, expected_status_code=200):
    response = client.get(f'/api/canvas_site/{canvas_site_id}/roster')
    assert response.status_code == expected_status_code
    return response.json


class TestGradeDistributions:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_get_grade_distributions(client, '1010101', expected_status_code=401)

    def test_no_canvas_account(self, client, fake_auth):
        """Denies user with no Canvas account."""
        canvas_site_id = '1010101'
        fake_auth.login(canvas_site_id=canvas_site_id, uid=no_canvas_account_uid)
        _api_get_grade_distributions(client, canvas_site_id, expected_status_code=401)

    def test_not_enrolled(self, client, app, fake_auth):
        """Denies user with no course enrollment."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {'course': ['get_by_id_1010101'], 'user': ['profile_20000']}, m)
            canvas_site_id = '1010101'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=not_enrolled_uid)
            _api_get_grade_distributions(client, canvas_site_id, expected_status_code=401)

    def test_student(self, client, app, fake_auth):
        """Denies student."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'course': ['get_by_id_1010101', 'get_sections_1010101'],
                'user': ['profile_40000'],
            }, m)
            canvas_site_id = '8876542'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=student_uid)
            _api_get_grade_distributions(client, canvas_site_id, expected_status_code=401)

    def test_admin_no_grades(self, client, app, fake_auth):
        """Allows admin, throws 404 if grades if not present."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'account': ['get_admins'],
                'course': ['get_by_id_8876542', 'get_sections_8876542'],
                'user': ['profile_10000'],
            }, m)
            canvas_site_id = '8876542'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=admin_uid)
            _api_get_grade_distributions(client, canvas_site_id, expected_status_code=404)

    def test_admin_grades(self, client, app, fake_auth):
        """Allows admin, returns grades if present."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'account': ['get_admins'],
                'course': ['get_by_id_1010101', 'get_sections_1010101'],
                'user': ['profile_10000'],
            }, m)
            canvas_site_id = '1010101'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=admin_uid)
            response = _api_get_grade_distributions(client, canvas_site_id)
            assert response['canvasSite']['courseCode'] == 'ASTRON 218'
            assert response['officialSections'][0]['sisId'] == 'SEC:2022-D-99999'
            assert response['demographics'][0]['genders'] == {'male': {'count': 5, 'percentage': 22.7}, 'female': {'count': 11, 'percentage': 16.2}}
            assert response['enrollments']['ANTHRO 197'][0] == {
                'grade': 'A+',
                'noPriorEnrollCount': 14,
                'noPriorEnrollPercentage': 17.1,
                'priorEnrollCount': 2,
                'priorEnrollPercentage': 22.2,
                'totalCount': 16,
                'totalPercentage': 17.6,
            }

    def test_ta(self, client, app, fake_auth):
        """Denies TA."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'account': ['get_admins'],
                'course': ['get_by_id_8876542', 'get_sections_8876542'],
                'user': ['profile_50000'],
            }, m)
            canvas_site_id = '8876542'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=ta_uid)
            _api_get_grade_distributions(client, canvas_site_id, expected_status_code=401)

    def test_teacher(self, client, app, fake_auth):
        """Allows teacher."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'account': ['get_admins'],
                'course': ['get_by_id_1010101', 'get_sections_1010101', 'get_enrollments_8876542_4567890_past'],
                'user': ['profile_30000'],
            }, m)
            canvas_site_id = '1010101'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=teacher_uid)
            response = _api_get_grade_distributions(client, canvas_site_id)
            assert response['canvasSite']['courseCode'] == 'ASTRON 218'
            assert response['officialSections'][0]['sisId'] == 'SEC:2022-D-99999'
            assert response['demographics'][0]['genders'] == {'male': {'count': 5, 'percentage': 22.7}, 'female': {'count': 11, 'percentage': 16.2}}
            assert response['enrollments']['ANTHRO 197'][0] == {
                'grade': 'A+',
                'noPriorEnrollCount': 14,
                'noPriorEnrollPercentage': 17.1,
                'priorEnrollCount': 2,
                'priorEnrollPercentage': 22.2,
                'totalCount': 16,
                'totalPercentage': 17.6,
            }


def _api_get_grade_distributions(client, canvas_site_id, expected_status_code=200):
    response = client.get(f'/api/canvas_site/{canvas_site_id}/grade_distribution')
    assert response.status_code == expected_status_code
    return response.json
