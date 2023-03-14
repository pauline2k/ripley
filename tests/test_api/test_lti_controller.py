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


class TestGetJwks:
    """JSON Web Key Set API."""

    def test_anonymous(self, client):
        """Anonymous user can get the JSON Web Key Set."""
        response = client.get('/api/lti/jwks')
        assert response.status_code == 200
        assert 'keys' in response.json
        keyset = response.json['keys'][0]
        for key in ['alg', 'e', 'kid', 'kty', 'n', 'use']:
            assert key in keyset


class TestGetMailingListConfig:

    def test_anonymous(self, client, app):
        """Anonymous user can get the Mailing List config JSON."""
        response = client.get('api/lti/config/mailing_list.json')
        assert response.status_code == 200
        assert response.content_type == 'application/json'
        config = response.json
        assert config['title'] == 'Mailing List'
        assert config['description'] == 'Create and manage a mailing list for a course site'
        assert config['oidc_initiation_url'] == app.url_for('initiate_login', _external=True)
        assert config['target_link_uri'] == app.url_for('launch_mailing_list', _external=True)
        assert config['public_jwk_url'] == app.url_for('get_jwk_set', _external=True)
        assert config['custom_fields'] == {
            'canvas_user_id': '$Canvas.user.id',
            'canvas_course_id': '$Canvas.course.id',
            'canvas_user_login_id': '$Canvas.user.loginId',
            'canvas_masquerading_user_id': '$Canvas.masqueradingUser.id',
        }
        assert len(config['extensions']) == 1
        tool = config['extensions'][0]
        assert tool['platform'] == 'canvas.instructure.com'
        assert tool['privacy_level'] == 'public'
        assert len(tool['settings']['placements']) == 1
        assert tool['settings']['placements'][0] == {
            'text': 'Mailing List',
            'placement': 'course_navigation',
            'message_type': 'LtiResourceLinkRequest',
        }


class TestGetUserProvisioningConfig:

    def test_anonymous(self, client, app):
        """Anonymous user can get the User Provisioning config JSON."""
        response = client.get('api/lti/config/provision_user.json')
        assert response.status_code == 200
        assert response.content_type == 'application/json'
        config = response.json
        assert config['title'] == 'User Provisioning'
        assert config['description'] == 'Automated user provisioning'
        assert config['oidc_initiation_url'] == app.url_for('initiate_login', _external=True)
        assert config['target_link_uri'] == app.url_for('launch_provision_user', _external=True)
        assert config['public_jwk_url'] == app.url_for('get_jwk_set', _external=True)
        assert config['custom_fields'] == {
            'canvas_user_id': '$Canvas.user.id',
            'canvas_course_id': '$Canvas.course.id',
            'canvas_user_login_id': '$Canvas.user.loginId',
            'canvas_masquerading_user_id': '$Canvas.masqueradingUser.id',
        }
        assert len(config['extensions']) == 1
        tool = config['extensions'][0]
        assert tool['platform'] == 'canvas.instructure.com'
        assert tool['privacy_level'] == 'public'
        assert len(tool['settings']['placements']) == 1
        assert tool['settings']['placements'][0] == {
            'text': 'User Provisioning',
            'placement': 'account_navigation',
            'message_type': 'LtiResourceLinkRequest',
        }
