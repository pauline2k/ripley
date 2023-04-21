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

from datetime import datetime

from flask import current_app as app, redirect, request
from flask_login import current_user, login_required
from ripley.api.errors import ResourceNotFoundError
from ripley.api.util import canvas_role_required, csv_download_response
from ripley.externals import canvas, data_loch
from ripley.externals.canvas import get_course
from ripley.lib.berkeley_term import BerkeleyTerm
from ripley.lib.canvas_utils import canvas_section_to_api_json, canvas_site_to_api_json, instruction_mode_description
from ripley.lib.http import tolerant_jsonify
from ripley.lib.util import to_bool_or_none
from ripley.merged.roster import canvas_site_roster


@app.route('/api/canvas_site/provision')
def canvas_site_provision():
    return tolerant_jsonify([])


@app.route('/api/canvas_site/<canvas_site_id>')
def get_canvas_site(canvas_site_id):
    course = canvas.get_course(canvas_site_id)
    if course:
        api_json = canvas_site_to_api_json(course)
        include_users = to_bool_or_none(request.args.get('includeUsers', False))
        if include_users:
            api_json['users'] = []
            for user in course.get_users(include=('email', 'enrollments')):
                api_json['users'].append({
                    'id': user.id,
                    'enrollments': user.enrollments,
                    'name': user.name,
                    'sortableName': user.sortable_name,
                    'uid': user.login_id,
                    'url': f"{app.config['CANVAS_API_URL']}/courses/{canvas_site_id}/users/{user.id}",
                })
        return tolerant_jsonify(api_json)
    else:
        raise ResourceNotFoundError(f'No Canvas course site found with ID {canvas_site_id}')


@app.route('/api/canvas_site/<canvas_site_id>/provision/sections')
@canvas_role_required('TeacherEnrollment', 'TaEnrollment', 'Lead TA', 'Reader')
def canvas_site_provision_sections(canvas_site_id):
    official_sections, section_ids = _get_official_sections(canvas_site_id)
    term = BerkeleyTerm.from_sis_term_id(official_sections[0]['termId'])
    can_edit = bool(next((role for role in current_user.canvas_site_user_roles if role in ['TeacherEnrollment', 'Lead TA']), None))
    teaching_terms = _get_teaching_terms(section_ids)
    return tolerant_jsonify({
        'canvasSite': {
            'canEdit': can_edit,
            'officialSections': official_sections,
            'term': term.to_api_json(),
        },
        'teachingTerms': teaching_terms,
    })


@app.route('/api/canvas_site/provision/status')
def canvas_site_provision_status():
    # TODO: ?jobId=${jobId}
    return tolerant_jsonify([])


@app.route('/api/canvas_site/<canvas_site_id>/egrade_export/options')
def canvas_egrade_export(canvas_site_id):
    return tolerant_jsonify([])


@app.route('/api/canvas_site/<canvas_site_id>/egrade_export/status')
def canvas_egrade_export_status(canvas_site_id):
    # TODO: ?jobId=${jobId}
    return tolerant_jsonify([])


@app.route('/api/canvas_site/<canvas_site_id>/roster')
@canvas_role_required('TeacherEnrollment', 'TaEnrollment', 'Lead TA', 'Reader')
def get_roster(canvas_site_id):
    return tolerant_jsonify(canvas_site_roster(canvas_site_id))


@app.route('/api/canvas_site/<canvas_site_id>/export_roster')
@canvas_role_required('TeacherEnrollment', 'TaEnrollment', 'Lead TA', 'Reader')
def get_roster_csv(canvas_site_id):
    rows = []
    roster = canvas_site_roster(canvas_site_id)
    for student in roster['students']:
        sections = sorted([section['name'] for section in student['sections']])
        rows.append({
            'Name': f"{student['firstName']} {student['lastName']}",
            'Student ID': student['studentId'],
            'UID': student['uid'],
            'Role': {'E': 'Student', 'W': 'Waitlist Student'}.get(student['enrollStatus'], None),
            'Email address': student['email'],
            'Sections': ', '.join(sections),
        })
    now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    return csv_download_response(
        rows=rows,
        filename=f'{canvas_site_id}-roster-{now}.csv',
        fieldnames=['Name', 'Student ID', 'UID', 'Role', 'Email address', 'Sections'],
    )


@app.route('/redirect/canvas/<canvas_site_id>/user/<uid>')
@login_required
def redirect_to_canvas_profile(canvas_site_id, uid):
    users = get_course(canvas_site_id, api_call=False).get_users(enrollment_type='student')
    user = next((user for user in users if getattr(user, 'login_id', None) == uid), None)
    if user:
        base_url = app.config['CANVAS_API_URL']
        return redirect(f'{base_url}/courses/{canvas_site_id}/users/{user.id}')
    else:
        raise ResourceNotFoundError(f'No bCourses site with ID "{canvas_site_id}" was found.')


def _get_official_sections(canvas_site_id):
    canvas_sections = canvas.get_course_sections(canvas_site_id)
    canvas_sections = [canvas_section_to_api_json(cs) for cs in canvas_sections if cs.sis_section_id]
    section_ids = [section['id'] for section in canvas_sections]
    term_id = canvas_sections[0]['termId']
    sis_sections = data_loch.get_sections(term_id, section_ids)
    sis_sections_by_id = {s['section_id']: s for s in sis_sections}

    def _section(canvas_section):
        sis_section = sis_sections_by_id[canvas_section['id']]
        return {
            **canvas_section,
            'courseCode': sis_section['course_name'],
            'instructionFormat': sis_section['instruction_format'],
            'instructionMode': instruction_mode_description(sis_section['instruction_mode']),
            'isPrimarySection': sis_section['is_primary'],
            'sectionNumber': sis_section['section_number'],
        }
    official_sections = [_section(cs) for cs in canvas_sections]
    return official_sections, section_ids


def _get_teaching_terms(section_ids):
    berkeley_terms = BerkeleyTerm.get_current_terms().values()
    # canvas_terms = canvas.get_terms()
    # TODO: find the intersection of berkeley_terms and canvas_terms
    teaching_sections = data_loch.get_instructing_sections(current_user.uid, [t.to_sis_term_id() for t in berkeley_terms])
    courses_by_term = {}
    for section in teaching_sections:
        course_id = section['course_id']
        term_id = section['term_id']
        if term_id not in courses_by_term:
            courses_by_term[term_id] = {}
        if course_id not in courses_by_term[term_id]:
            term = BerkeleyTerm.from_sis_term_id(term_id)
            courses_by_term[term_id][course_id] = {
                'courseCode': section['course_name'],
                'sections': [],
                'slug': '-'.join([
                    section['course_name'].replace(' ', '-').lower(),
                    term.to_session_slug(session_code=section['session_code']),
                ]),
                'title': section['course_title'],
            }
        # TODO: add schedules
        courses_by_term[term_id][course_id]['sections'].append({
            'courseCode': section['course_name'],
            'id': section['section_id'],
            'instructionFormat': section['instruction_format'],
            'instructionMode': instruction_mode_description(section['instruction_mode']),
            'isCourseSection': section['section_id'] in section_ids,
            'isPrimarySection': section['is_primary'],
            'schedules': {
                'oneTime': [],
                'recurring': [],
            },
            'sectionNumber': section['section_number'],
        })

    def _term_courses(term_id, courses_by_id):
        term = BerkeleyTerm.from_sis_term_id(term_id)
        return {
            'classes': list(courses_by_id.values()),
            'name': term.to_english(),
            'slug': term.to_slug(),
            'termId': term_id,
            'termYear': term.year,
        }
    return [_term_courses(term_id, courses_by_id) for term_id, courses_by_id in courses_by_term.items()]
