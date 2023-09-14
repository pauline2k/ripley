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
from ripley.api.errors import BadRequestError, InternalServerError, ResourceNotFoundError
from ripley.api.util import canvas_role_required
from ripley.externals import canvas
from ripley.externals.data_loch import find_people_by_email, find_people_by_name, find_person_by_uid
from ripley.lib.canvas_utils import add_user_to_course_section
from ripley.lib.http import tolerant_jsonify


@app.route('/api/canvas_user/<canvas_site_id>/options')
@login_required
@canvas_role_required('TaEnrollment', 'TeacherEnrollment', 'Lead TA')
def get_add_user_options(canvas_site_id):
    course = canvas.get_course(canvas_site_id)
    if not course:
        raise ResourceNotFoundError(f'No Canvas course site found with ID {canvas_site_id}')
    course_sections = canvas.get_course_sections(canvas_site_id)
    return tolerant_jsonify({
        'courseSections': [{'id': section.id, 'name': section.name} for section in course_sections if section.sis_section_id],
        'grantingRoles': _get_grantable_roles(),
    })


@app.route('/api/canvas_user/<canvas_site_id>/users', methods=['POST'])
@login_required
@canvas_role_required('TaEnrollment', 'TeacherEnrollment', 'Lead TA')
def canvas_site_add_user(canvas_site_id):
    course = canvas.get_course(canvas_site_id)
    if not course:
        raise ResourceNotFoundError(f'No Canvas course site found with ID {canvas_site_id}')
    params = request.get_json()
    course_section_id = params.get('sectionId')
    role_label = params.get('role')
    uid = params.get('uid')
    all_roles = canvas.get_roles()
    role = next((r for r in all_roles if r.label == role_label), None)
    if not role:
        raise BadRequestError(f'Unknown role: {role_label}.')
    enrollment = add_user_to_course_section(uid, role, course_section_id)
    if enrollment:
        role_given = next((r for r in all_roles if r.id == enrollment.role_id), None)
        return tolerant_jsonify({
            'role': getattr(role_given, 'label', role_label),
            'sectionId': str(enrollment.course_section_id),
            'uid': uid,
        })
    else:
        raise InternalServerError('Encountered a problem while trying to add a user.')


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
    return tolerant_jsonify(
        {
            'users': [_campus_user_to_api_json(user) for user in search_results],
        },
    )


def _campus_user_to_api_json(user):
    return {
        'affiliations': user['affiliations'],
        'emailAddress': user['email_address'],
        'firstName': user['first_name'],
        'lastName': user['last_name'],
        'resultCount': user['result_count'],
        'rowNumber': user['row_number'],
        'type': user['person_type'],
        'uid': user['ldap_uid'],
    }


def _canvas_role_sort_key(role):
    # The default Canvas UX orders roles by base role type, then built-ins first, then role ID.
    role_type_order = ['StudentEnrollment', 'TeacherEnrollment', 'TaEnrollment', 'DesignerEnrollment', 'ObserverEnrollment']
    type_key = role_type_order.index(role.base_role_type)
    # Custom roles have a "workflow_state" of "active" rather than "built_in".
    workflow_key = 0 if role.workflow_state == 'built_in' else 1
    return f'{type_key}_{workflow_key}_{role.id}'


def _get_grantable_roles():
    permission_to_grantable_role_types = {
        'add_designer_to_course': {'DesignerEnrollment'},
        'add_observer_to_course': {'ObserverEnrollment'},
        'add_student_to_course': {'StudentEnrollment'},
        'add_ta_to_course': {'TaEnrollment'},
        'add_teacher_to_course': {'TeacherEnrollment'},
        'manage_students': {'StudentEnrollment', 'ObserverEnrollment'},
        'manage_admin_users': {'DesignerEnrollment', 'TaEnrollment', 'TeacherEnrollment'},
    }

    def _has_permission(role, permission):
        return role.permissions.get(permission, {}).get('enabled', False)

    all_roles = {r.role: r for r in canvas.get_roles()}
    grantable_roles = []

    if current_user.is_admin:
        grantable_roles = [role for role in all_roles.values() if role.base_role_type.endswith('Enrollment')]
    else:
        grantable_role_types = set()
        for user_role in current_user.canvas_site_user_roles:
            role = all_roles[user_role]
            for permission, role_types in permission_to_grantable_role_types.items():
                if _has_permission(role, permission):
                    grantable_role_types.update(role_types)
        grantable_roles = [role for role in all_roles.values() if role.base_role_type in grantable_role_types]

    roles = [role.label for role in sorted(grantable_roles, key=_canvas_role_sort_key)]
    return [role for i, role in enumerate(roles) if role not in roles[:i]]


def _search_users(search_text, search_type):
    if search_type == 'name':
        return find_people_by_name(search_text)
    elif search_type == 'email':
        return find_people_by_email(search_text)
    elif search_type == 'uid':
        return find_person_by_uid(search_text)
