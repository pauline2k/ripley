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


class TestSiteCreationAuthorization:

    def test_ripley_creation(self, client, app):
        assert _api_can_create_site(app, client, '2345678') == {'canCreateSite': True}

    def test_joan_creation(self, client, app):
        assert _api_can_create_site(app, client, '3456789') == {'canCreateSite': False}

    def test_unknown(self, client, app):
        assert _api_can_create_site(app, client, '2122') == {'canCreateSite': False}


def _api_can_create_site(app, client, canvas_user_id, expected_status_code=200):
    with requests_mock.Mocker() as m:
        register_canvas_uris(app, {
            'account': ['get_admins', 'get_by_id'],
            'user': ['*'],
        }, m)
        response = client.get(f'api/canvas/can_user_create_site?canvas_user_id={canvas_user_id}')
        assert response.status_code == expected_status_code
        return response.json


class TestMyAuthorizations:

    def test_ripley_auth(self, client, app, fake_auth):
        assert _api_authorizations(app, client, fake_auth, '10000') == {
            'authorizations': {
                'canCreateCourseSite': True,
                'canCreateProjectSite': True,
            },
        }

    def test_joan_auth(self, client, app, fake_auth):
        assert _api_authorizations(app, client, fake_auth, '20000') == {
            'authorizations': {
                'canCreateCourseSite': False,
                'canCreateProjectSite': False,
            },
        }


def _api_authorizations(app, client, fake_auth, uid, expected_status_code=200):
    with requests_mock.Mocker() as m:
        register_canvas_uris(app, {
            'account': ['get_admins', 'get_by_id'],
            'user': ['*'],
        }, m)
        fake_auth.login(uid=uid, canvas_site_id=None)
        response = client.get('api/canvas/authorizations')
        assert response.status_code == expected_status_code
        return response.json
