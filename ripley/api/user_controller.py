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
from flask import current_app as app, request
from flask_login import current_user, login_required
from ripley.api.errors import BadRequestError
from ripley.lib.http import tolerant_jsonify
from ripley.models.user import User


@app.route('/api/user/my_profile')
def my_profile():
    return tolerant_jsonify(current_user.to_api_json(include_canvas_user_data=True))


@app.route('/api/user/profile', methods=['POST'])
@login_required
def get_user_profile():
    params = request.get_json() or {}
    uid = params.get('uid')
    if uid and (uid == current_user.uid or current_user.is_admin):
        user_id = User.get_serialized_composite_key(
            canvas_site_id=current_user.canvas_site_id,
            uid=uid,
        )
        return tolerant_jsonify(User(user_id).to_api_json(include_canvas_user_data=True))
    else:
        raise BadRequestError('Invalid UID')
