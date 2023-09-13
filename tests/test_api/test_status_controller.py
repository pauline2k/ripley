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


class TestStatusController:
    """Status API."""

    def test_ping(self, app, client):
        """Answers the phone when pinged."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {'account': ['get_by_id']}, m)

            response = client.get('/api/ping')
            assert response.status_code == 200
            assert response.json['app'] is True
            assert response.json['canvas'] is True
            assert response.json['data_loch'] is True
            assert response.json['db'] is True
            assert response.json['rq']['redis'] is True
            assert response.json['rq']['workers'] is False

    def test_canvas_error(self, app, client):
        """Reports Canvas API error."""
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {'account': ['get_by_id_404']}, m)

            response = client.get('/api/ping')
            assert response.status_code == 200
            assert response.json['app'] is True
            assert response.json['canvas'] is False
            assert response.json['data_loch'] is True


class TestRqStatusController:
    """RQ status API."""

    admin_uid = '10000'
    non_admin_uid = '10001'

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_ping_rq(client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(canvas_site_id=None, uid=self.non_admin_uid)
        _api_ping_rq(client, expected_status_code=401)

    def test_authorized(self, client, fake_auth, mock_job):
        fake_auth.login(canvas_site_id=None, uid=self.admin_uid)
        response = _api_ping_rq(client)
        print(response)
        assert response['redis'] is True
        assert response['workers'] == []
        assert response['queue'] == {'name': 'default', 'jobCount': 0}


def _api_ping_rq(client, expected_status_code=200):
    response = client.get('/api/ping/rq')
    assert response.status_code == expected_status_code
    return response.json
