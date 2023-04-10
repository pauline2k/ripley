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
ta_uid = '50000'
teacher_uid = '30000'
student_uid = '40000'


class TestCanvasSiteProvisionSections:
    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_canvas_course_provision_sections(client, '8876542', expected_status_code=401)

    def test_no_canvas_account(self, client, fake_auth):
        """Denies user with no Canvas account."""
        canvas_site_id = '8876542'
        fake_auth.login(canvas_site_id=canvas_site_id, uid=no_canvas_account_uid)
        _api_canvas_course_provision_sections(client, canvas_site_id, expected_status_code=401)

    def test_not_enrolled(self, client, app, fake_auth):
        """Denies user with no course enrollment."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {'course': ['get_by_id_8876542'], 'user': ['profile_20000']}, m)
            canvas_site_id = '8876542'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=not_enrolled_uid)
            _api_canvas_course_provision_sections(client, canvas_site_id, expected_status_code=401)

    def test_ta(self, client, app, fake_auth):
        """Allows TA, read-only."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'course': ['get_by_id_8876542', 'get_sections_8876542', 'get_enrollments_6789012'],
                'user': ['profile_50000'],
            }, m)
            canvas_site_id = '8876542'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=ta_uid)
            response = _api_canvas_course_provision_sections(client, canvas_site_id)
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
            assert section['id'] == '32936'
            assert section['name'] == 'Section A'
            assert section['sisId'] == 'SEC:2023-B-32936'
            assert section['termId'] == '2232'
            assert len(response['teachingTerms']) == 0

    def test_teacher(self, client, app, fake_auth):
        """Allows teacher."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'course': ['get_by_id_8876542', 'get_sections_8876542', 'get_enrollments_4567890'],
                'user': ['profile_30000'],
            }, m)
            canvas_site_id = '8876542'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=teacher_uid)
            response = _api_canvas_course_provision_sections(client, canvas_site_id)
            assert response['canvasSite']
            assert response['canvasSite']['canEdit'] is True
            assert response['canvasSite']['term'] == {
                'id': '2232',
                'name': 'Spring 2023',
                'season': 'B',
                'year': '2023',
            }
            assert len(response['canvasSite']['officialSections']) == 2
            section = response['canvasSite']['officialSections'][0]
            assert section['id'] == '32936'
            assert section['name'] == 'Section A'
            assert section['sisId'] == 'SEC:2023-B-32936'
            assert section['termId'] == '2232'
            assert len(response['teachingTerms']) == 1
            spring_term = response['teachingTerms'][0]
            assert spring_term['name'] == 'Spring 2023'
            assert spring_term['slug'] == 'spring-2023'
            assert spring_term['termId'] == '2232'
            assert spring_term['termYear'] == '2023'
            assert len(spring_term['classes']) == 1
            course = spring_term['classes'][0]
            assert course['courseCode'] == 'ASTRON 218'
            assert course['title'] == 'Stellar Dynamics and Galactic Structure'
            assert len(course['sections']) == 2
            section = course['sections'][0]
            assert section['id'] == '12345'
            assert section['instructionFormat'] == 'LEC'
            assert section['instructionMode'] == 'In Person'
            assert section['isPrimarySection'] is True
            assert section['sectionNumber'] == '001'
            assert course['slug'] == 'astron-218-B-2023'


def _api_canvas_course_provision_sections(client, canvas_site_id, expected_status_code=200):
    response = client.get(f'/api/canvas_site/{canvas_site_id}/provision/sections')
    assert response.status_code == expected_status_code
    return response.json


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

    def test_admin(self, client, app, fake_auth):
        """Allows admin."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'course': ['get_by_id_8876542', 'get_sections_8876542', 'get_enrollments_4567890'],
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
            assert student['studentId'] is None
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
                'course': ['get_by_id_8876542', 'get_sections_8876542', 'get_enrollments_4567890'],
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
                'course': ['get_by_id_8876542', 'get_sections_8876542', 'get_enrollments_4567890'],
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
