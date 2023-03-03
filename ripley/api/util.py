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

from functools import wraps
from urllib.parse import urljoin, urlparse

from flask import abort, current_app as app, redirect, request
from flask_login import current_user, login_user, logout_user
from ripley.externals import canvas
from ripley.lib.http import tolerant_jsonify


def admin_required(func):
    @wraps(func)
    def _admin_required(*args, **kw):
        if current_user and current_user.is_admin:
            return func(*args, **kw)
        else:
            app.logger.warning(f'Unauthorized request to {request.path}')
            return app.login_manager.unauthorized()
    return _admin_required


def canvas_role_required(*roles):
    def _canvas_role_required(func):
        @wraps(func)
        def wrapper(*args, **kw):
            authorized = False
            if current_user.is_authenticated and current_user.is_admin:
                authorized = True
            elif current_user.is_authenticated and current_user.canvas_user_id:
                canvas_course_user = canvas.get_course_user(kw['canvas_course_id'], current_user.canvas_user_id)
                if canvas_course_user and canvas_course_user.enrollments:
                    if next((e for e in canvas_course_user.enrollments if e['role'] in roles), None):
                        authorized = True
            if authorized:
                return func(*args, **kw)
            else:
                app.logger.warning(f'Unauthorized request to {request.path}')
                return app.login_manager.unauthorized()
        return wrapper
    return _canvas_role_required


def _is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def start_login_session(user, redirect_path=None):
    app.logger.info(f"""Starting login session for {user.uid}""")
    if (current_user.is_authenticated and (
            current_user.uid != user.uid or current_user.canvas_course_id != user.canvas_course_id)):
        app.logger.info(f'User (UID {user.uid} canvas_course_id {user.canvas_course_id}) does not match existing session \
            (UID {current_user.uid} canvas_course_id {current_user.canvas_course_id}). Terminating existing session.')
        logout_user()
    authenticated = login_user(user, force=True, remember=True) and current_user.is_authenticated
    if not _is_safe_url(request.args.get('next')):
        return abort(400)
    if authenticated:
        return redirect(redirect_path) if redirect_path else tolerant_jsonify(current_user.to_api_json())
    else:
        return tolerant_jsonify({'message': f'User {user.uid} failed to authenticate.'}, 403)
