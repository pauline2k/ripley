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
from flask_login import login_required
from ripley.api.errors import BadRequestError
from ripley.api.util import canvas_role_required
from ripley.externals.data_loch import find_people_by_email, find_people_by_name, find_person_by_uid
from ripley.lib.http import tolerant_jsonify


@app.route('/api/canvas_user/<canvas_site_id>/roles')
def canvas_site_user_roles(canvas_site_id):
    return tolerant_jsonify([])


@app.route('/api/canvas_user/<canvas_site_id>/course_sections')
def canvas_site_add_user(canvas_site_id):
    return tolerant_jsonify([])


@app.route('/api/canvas_user/search')
@login_required
@canvas_role_required('TaEnrollment', 'TeacherEnrollment', 'Lead TA')
def search_users():
    search_text = request.args.get('searchText')
    if not search_text:
        raise BadRequestError('Search text is required.')

    search_type = request.args.get('searchType')
    if search_type not in ['name', 'email', 'uid']:
        raise BadRequestError('Invalid search type.')

    search_results = _search_users(search_text, search_type)
    return tolerant_jsonify([_campus_user_to_api_json(user) for user in search_results])


def _campus_user_to_api_json(user):
    return {
        'uid': user['ldap_uid'],
        'firstName': user['first_name'],
        'lastName': user['last_name'],
        'emailAddress': user['email_address'],
        'affiliations': user['affiliations'],
        'type': user['person_type'],
    }


def _search_users(search_text, search_type):
    if search_type == 'name':
        return find_people_by_name(search_text)
    elif search_type == 'email':
        return find_people_by_email(search_text)
    elif search_type == 'uid':
        return find_person_by_uid(search_text)
