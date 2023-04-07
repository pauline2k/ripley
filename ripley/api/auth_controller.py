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

from urllib.parse import urlencode

import cas
from flask import current_app as app, flash, redirect, request, url_for
from flask_login import current_user, login_required, logout_user
from ripley.api.errors import ResourceNotFoundError
from ripley.api.util import start_login_session
from ripley.lib.http import add_param_to_url, tolerant_jsonify
from ripley.models.user import User


@app.route('/api/auth/become_user', methods=['POST'])
@login_required
def become():
    logout_user()
    params = request.get_json() or {}
    return _dev_auth_login(
        canvas_site_id=params.get('canvasSiteId'),
        password=app.config['DEV_AUTH_PASSWORD'],
        uid=params.get('uid'),
    )


@app.route('/api/auth/cas_login_url')
def cas_login_url():
    target_url = request.referrer or None
    return tolerant_jsonify({
        'casLoginUrl': _cas_client(target_url).get_login_url(),
    })


@app.route('/api/auth/dev_auth', methods=['POST'])
def dev_auth_login():
    if app.config['DEV_AUTH_ENABLED']:
        params = request.get_json() or {}
        canvas_site_id = params.get('canvasSiteId')
        uid = params.get('uid')
        app.logger.debug(f'Dev-auth login attempt by UID {uid}')
        password = params.get('password')
        return _dev_auth_login(canvas_site_id, password, uid)
    else:
        app.logger.debug('Dev-auth attempt when DEV_AUTH_ENABLED == False.')
        raise ResourceNotFoundError('Unknown path')


@app.route('/api/auth/update_user_session', methods=['POST'])
def update_user_session():
    if app.config['DEV_AUTH_ENABLED'] and current_user.is_authenticated:
        params = request.get_json() or {}
        canvas_site_id = params.get('canvasSiteId')
        uid = current_user.uid
        logout_user()
        # Re-authenticate
        user_id = User.get_serialized_composite_key(canvas_site_id=canvas_site_id, uid=uid)
        user = User(user_id)
        if user.is_active and (user.is_admin or len(user.canvas_site_user_roles)):
            # User must be either an admin or a member of the course site.
            start_login_session(user)
            return tolerant_jsonify(user.to_api_json(include_canvas_user_data=True))
        else:
            logout_user()
            return tolerant_jsonify(f'Sorry, {uid} is not authorized to use this tool.', 403)
    else:
        raise ResourceNotFoundError('Unknown path')


@app.route('/api/auth/logout')
@login_required
def logout():
    logout_user()
    redirect_url = app.config['VUE_LOCALHOST_BASE_URL'] or request.url_root
    cas_logout_url = _cas_client().get_logout_url(redirect_url=redirect_url)
    return tolerant_jsonify({
        'casLogoutUrl': cas_logout_url,
        **current_user.to_api_json(),
    })


@app.route('/cas/callback', methods=['GET', 'POST'])
def cas_login():
    ticket = request.args['ticket']
    target_url = request.args.get('url')
    uid, attributes, proxy_granting_ticket = _cas_client(target_url).verify_ticket(ticket)
    app.logger.info(f'Logged into CAS as user {uid}')
    user_id = User.get_serialized_composite_key(canvas_site_id=None, uid=uid)
    user = User(user_id)
    if user.is_active:
        flash('Logged in successfully.')
        redirect_path = target_url or '/'
        return start_login_session(user, redirect_path=redirect_path)
    else:
        redirect_path = add_param_to_url('/', ('error', f'Sorry, {user.name} is not authorized to use this tool.'))
        return redirect(redirect_path)


def _cas_client(target_url=None):
    cas_server = app.config['CAS_SERVER']
    # One (possible) advantage this has over "request.base_url" is that it embeds the configured SERVER_NAME.
    service_url = url_for('.cas_login', _external=True)
    if target_url:
        service_url = service_url + '?' + urlencode({'url': target_url})
    return cas.CASClientV3(server_url=cas_server, service_url=service_url)


def _dev_auth_login(canvas_site_id, password, uid):
    if password != app.config['DEV_AUTH_PASSWORD']:
        app.logger.debug(f'UID {uid} failed dev-auth login: bad password.')
        return tolerant_jsonify({'message': 'Invalid credentials'}, 401)
    user_id = User.get_serialized_composite_key(canvas_site_id=canvas_site_id, uid=uid)
    user = User(user_id)
    if not user.is_active:
        msg = f'Sorry, {uid} is not authorized to use this tool.'
        return tolerant_jsonify({'message': msg}, 403)
    response = start_login_session(user)
    app.logger.debug(f'Successful dev-auth login for UID {user.uid}.')
    return response


def _get_custom_param(lti_data, key):
    value = lti_data.get('https://purl.imsglobal.org/spec/lti/claim/custom', {}).get(key)
    return value if value and value.isnumeric() else None
