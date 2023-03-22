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
                'course': ['get_by_id_8876542', 'get_sections_8876542', 'get_students_8876542', 'get_enrollments_4567890'],
                'user': ['profile_10000'],
            }, m)
            canvas_site_id = '8876542'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=admin_uid)
            response = _api_get_roster(client, canvas_site_id)

            assert response['canvasSite']['canvasSiteId'] == 8876542
            assert response['canvasSite']['name'] == 'Our Dogs, Ourselves: Encounters between the Human and the Non-Human'
            assert len(response['sections']) == 1
            section = response['sections'][0]
            assert section['id'] == 'SEC:2023-B-32936'
            assert section['name'] == 'Section A'
            assert section['sisCourseId'] == 'CRS:ANTHRO-189-2023-B'
            assert len(response['students']) == 1
            student = response['students'][0]
            assert student['email'] == 'xo.kane@berkeley.edu'
            assert student['enrollStatus'] == 'active'
            assert student['firstName'] == 'XO'
            assert student['gradeOption'] == 'TODO'
            assert student['id'] == 5678901
            assert student['lastName'] == 'Kane'
            assert student['loginId'] == '40000'
            assert student['photoUrl'] == 'TODO'
            assert student['sectionIds'] == 'TODO'
            assert student['studentId'] == 'UID:40000'
            assert student['units'] == 'TODO'
            assert len(student['sections'])
            assert student['sections'][0]['id'] == 'SEC:2023-B-32936'
            assert student['sections'][0]['name'] == 'Section A'
            assert student['sections'][0]['sisCourseId'] == 'CRS:ANTHRO-189-2023-B'

    def test_teacher(self, client, app, fake_auth):
        """Allows teacher."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'course': ['get_by_id_8876542', 'get_sections_8876542', 'get_students_8876542', 'get_enrollments_4567890'],
                'user': ['profile_30000'],
            }, m)
            canvas_site_id = '8876542'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=teacher_uid)
            response = _api_get_roster(client, canvas_site_id)

            assert response['canvasSite']['canvasSiteId'] == 8876542
            assert response['canvasSite']['name'] == 'Our Dogs, Ourselves: Encounters between the Human and the Non-Human'
            assert len(response['sections']) == 1
            assert len(response['students']) == 1

    def test_student(self, client, app, fake_auth):
        """Denies student."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'course': ['get_by_id_8876542', 'get_sections_8876542', 'get_students_8876542', 'get_enrollments_4567890'],
                'user': ['profile_40000'],
            }, m)
            canvas_site_id = '8876542'
            fake_auth.login(canvas_site_id=canvas_site_id, uid=student_uid)
            _api_get_roster(client, canvas_site_id, expected_status_code=401)


def _api_get_roster(client, canvas_site_id, expected_status_code=200):
    response = client.get(f'api/canvas_site/{canvas_site_id}/roster')
    assert response.status_code == expected_status_code
    return response.json
