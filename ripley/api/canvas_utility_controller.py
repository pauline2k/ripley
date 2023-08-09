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
from ripley.lib.http import tolerant_jsonify
from ripley.models.user import User


@app.route('/api/canvas/external_tools')
def get_external_tools():
    return tolerant_jsonify([])


@app.route('/api/canvas/authorizations')
@login_required
def get_authorizations():
    return tolerant_jsonify({
        'authorizations': {
            'canCreateCourseSite': current_user.can_create_canvas_course_site(),
            'canCreateProjectSite': current_user.can_create_canvas_project_site(),
        },
    })


@app.route('/api/canvas/can_user_create_site')
def can_user_create_site():
    # Used by canvas-customization.js
    can_create = False
    canvas_user_id = request.args.get('canvas_user_id')
    if canvas_user_id:
        user = User.from_canvas_user_id(canvas_user_id)
        if user:
            can_create = user.can_create_canvas_project_site() or user.can_create_canvas_course_site()
    return tolerant_jsonify({'canCreateSite': can_create})
