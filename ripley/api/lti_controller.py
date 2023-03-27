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

from flask import current_app as app
from pylti1p3.contrib.flask import (FlaskCacheDataStorage, FlaskMessageLaunch, FlaskOIDCLogin, FlaskRequest)
from pylti1p3.exception import LtiException
from pylti1p3.tool_config import ToolConfJsonFile
from ripley import cache
from ripley.api.errors import BadRequestError, InternalServerError
from ripley.api.util import start_login_session
from ripley.lib.http import tolerant_jsonify
from ripley.models.user import User


class MessageLaunch(FlaskMessageLaunch):

    def validate_deployment(self):
        # pylti1p3 expects a deployment ID, but Canvas makes them optional
        # (https://canvas.instructure.com/doc/api/file.lti_dev_key_config.html#configuring-canvas-in-the-tool).
        try:
            super().validate_deployment()
        except LtiException as e:
            deployment_id = self._get_jwt_body().get('https://purl.imsglobal.org/spec/lti/claim/deployment_id')
            app.logger.warn(f'Deployment ID validation failed; skipping. {e} deployment_id={deployment_id}')
        return self

    def validate_nonce(self):
        # Temporary(?) workaround for "Invalid nonce" error from pylti1p3.
        try:
            super().validate_nonce()
        except LtiException as e:
            nonce = self._get_jwt_body().get('nonce')
            app.logger.warn(f'Nonce validation failed; skipping. {e} nonce={nonce}')
        return self


@app.route('/api/lti/config/add_user.json')
def config_add_user():
    return _tool_config(
        title='Find a Person to Add',
        description='Search and add users to course sections',
        target='launch_add_user',
        placement='course_navigation',
    )


@app.route('/api/lti/config/course_captures.json')
def config_course_captures():
    return _tool_config(
        title='Course Captures',
        description='Recordings of this course',
        target='launch_course_captures',
        placement='course_navigation',
    )


@app.route('/api/lti/config/create_site.json')
def config_create_site():
    return _tool_config(
        title='Create a Site',
        description='Provides access to Course and Project site creation',
        target='launch_create_site',
        placement='user_navigation',
    )


@app.route('/api/lti/config/export_grade.json')
def config_export_grade():
    return _tool_config(
        title='Download E-Grades',
        description='Exports Course Grades to E-Grades CSV file',
        target='launch_export_grade',
        placement='course_navigation',
    )


@app.route('/api/lti/config/mailing_list.json')
def config_mailing_list():
    return _tool_config(
        title='Mailing List',
        description='Create and manage a mailing list for a course site',
        target='launch_mailing_list',
        placement='course_navigation',
    )


@app.route('/api/lti/config/mailing_lists.json')
def config_mailing_lists():
    return _tool_config(
        title='Mailing Lists',
        description='Create and manage mailing lists for all course sites',
        target='launch_mailing_lists',
        placement='account_navigation',
    )


@app.route('/api/lti/config/manage_official_sections.json')
def config_manage_official_sections():
    return _tool_config(
        title='Manage Official Sections',
        description='Provides management options for official course sections',
        target='launch_manage_official_sections',
        placement='course_navigation',
    )


@app.route('/api/lti/config/provision_user.json')
def config_provision_user():
    return _tool_config(
        title='User Provisioning',
        description='Automated user provisioning',
        target='launch_provision_user',
        placement='account_navigation',
    )


@app.route('/api/lti/config/roster_photos.json')
def config_roster_photos():
    return _tool_config(
        title='Roster Photos',
        description='Browse and search official roster photos',
        target='launch_roster_photos',
        placement='course_navigation',
    )


@app.route('/api/lti/jwks')
def get_jwk_set():
    lti_config_path = app.config['LTI_CONFIG_PATH']
    try:
        tool_conf = ToolConfJsonFile(lti_config_path)
        key_set = tool_conf.get_jwks()
        return tolerant_jsonify(key_set)
    except Exception as e:
        app.logger.error(f'Failed to generate LTI keys: {e.__class__.__name__}: {e}')
        raise InternalServerError({'message': str(e)})


@app.route('/api/lti/login', methods=['GET', 'POST'])
def initiate_login():
    lti_config_path = app.config['LTI_CONFIG_PATH']
    flask_request = FlaskRequest()
    target_link_uri = flask_request.get_param('target_link_uri')
    if not target_link_uri:
        raise BadRequestError('Required parameters are missing.')
    try:
        tool_conf = ToolConfJsonFile(lti_config_path)
        launch_data_storage = FlaskCacheDataStorage(cache)
        oidc_login = FlaskOIDCLogin(flask_request, tool_conf, launch_data_storage=launch_data_storage)

        response = oidc_login.enable_check_cookies().redirect(target_link_uri)
        app.logger.info(f'Redirecting to target_link_uri {target_link_uri}')
        return response
    except Exception as e:
        app.logger.error(f'OIDC login failed: {e.__class__.__name__}: {e}')
        raise InternalServerError({'message': str(e)})


@app.route('/api/lti/add_user', methods=['GET', 'POST'])
def launch_add_user():
    return _launch_tool('add_user')


@app.route('/api/lti/course_captures', methods=['GET', 'POST'])
def launch_course_captures():
    return _launch_tool('course_captures')


@app.route('/api/lti/create_site', methods=['GET', 'POST'])
def launch_create_site():
    return _launch_tool('create_site')


@app.route('/api/lti/export_grade', methods=['GET', 'POST'])
def launch_export_grade():
    return _launch_tool('export_grade')


@app.route('/api/lti/mailing_list', methods=['GET', 'POST'])
def launch_mailing_list():
    return _launch_tool('mailing_list/manage')


@app.route('/api/lti/mailing_lists', methods=['GET', 'POST'])
def launch_mailing_lists():
    return _launch_tool('mailing_lists')


@app.route('/api/lti/manage_official_sections', methods=['GET', 'POST'])
def launch_manage_official_sections():
    return _launch_tool('manage_official_sections')


@app.route('/api/lti/provision_user', methods=['GET', 'POST'])
def launch_provision_user():
    return _launch_tool('provision_user')


@app.route('/api/lti/roster_photos', methods=['GET', 'POST'])
def launch_roster_photos():
    return _launch_tool('roster')


def _get_custom_param(lti_data, key):
    value = lti_data.get('https://purl.imsglobal.org/spec/lti/claim/custom', {}).get(key)
    return value if value and str(value).isnumeric() else None


def _launch_tool(target_uri):
    lti_config_path = app.config['LTI_CONFIG_PATH']
    flask_request = FlaskRequest()
    try:
        tool_conf = ToolConfJsonFile(lti_config_path)
        launch_data_storage = FlaskCacheDataStorage(cache)

        message_launch = MessageLaunch(flask_request, tool_conf, launch_data_storage=launch_data_storage)
        launch_data = message_launch.get_launch_data()
        canvas_site_id = _get_custom_param(launch_data, 'canvas_site_id')
        canvas_masquerading_user_id = _get_custom_param(launch_data, 'canvas_masquerading_user_id')
        canvas_user_id = _get_custom_param(launch_data, 'canvas_user_id')
        uid = _get_custom_param(launch_data, 'canvas_user_login_id')
        masquerade = f'Canvas ID {canvas_masquerading_user_id} acting as ' if canvas_masquerading_user_id else ''
        course_context = f', course id {canvas_site_id}' if canvas_site_id else ''

        user_id = User.get_serialized_composite_key(canvas_site_id=canvas_site_id, uid=uid)
        user = User(user_id)
        app.logger.info(f"""Logged in during LTI launch as {masquerade}UID {uid}, Canvas ID {canvas_user_id}{course_context}""")
        return start_login_session(user, redirect_path=f'/{target_uri}')
    except Exception as e:
        app.logger.error(f'Failure to launch: {e.__class__.__name__}: {e}')
        raise InternalServerError({'message': str(e)})


def _tool_config(title, description, target, placement):
    return {
        'title': title,
        'description': description,
        'oidc_initiation_url': app.url_for('initiate_login', _external=True),
        'public_jwk_url': app.url_for('get_jwk_set', _external=True),
        'target_link_uri': app.url_for(target, _external=True),
        'extensions': [
            {
                'platform': 'canvas.instructure.com',
                'privacy_level': 'public',
                'settings': {
                    'platform': 'canvas.instructure.com',
                    'placements': [
                        {
                            'text': title,
                            'placement': placement,
                            'message_type': 'LtiResourceLinkRequest',
                        },
                    ],
                },
            },
        ],
        'custom_fields': {
            'canvas_user_id': '$Canvas.user.id',
            'canvas_site_id': '$Canvas.course.id',
            'canvas_user_login_id': '$Canvas.user.loginId',
            'canvas_masquerading_user_id': '$Canvas.masqueradingUser.id',
        },
    }
