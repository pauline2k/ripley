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

from flask import current_app as app, redirect, request
from flask_login import current_user, login_required
from ripley.api.errors import BadRequestError, InternalServerError, ResourceNotFoundError
from ripley.api.util import canvas_role_required, csv_download_response
from ripley.externals import canvas, data_loch
from ripley.externals.canvas import get_course
from ripley.lib.berkeley_course import course_to_api_json, section_to_api_json, sort_course_sections
from ripley.lib.berkeley_term import BerkeleyTerm
from ripley.lib.canvas_utils import canvas_section_to_api_json, canvas_site_to_api_json
from ripley.lib.http import tolerant_jsonify
from ripley.lib.sis_import_csv import SisImportCsv
from ripley.lib.util import to_bool_or_none
from ripley.merged.roster import canvas_site_roster, canvas_site_roster_csv


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


@app.route('/api/canvas_site/<canvas_site_id>/provision/sections', methods=['POST'])
@canvas_role_required('TeacherEnrollment', 'Lead TA')
def canvas_site_edit_sections(canvas_site_id):
    course = canvas.get_course(canvas_site_id)
    if not course:
        raise ResourceNotFoundError(f'No Canvas course site found with ID {canvas_site_id}')
    params = request.get_json()
    sections_to_add = params.get('sectionIdsToAdd', [])
    sections_to_remove = params.get('sectionIdsToRemove', [])
    sections_to_update = params.get('sectionIdsToUpdate', [])
    section_ids = sections_to_add + sections_to_remove + sections_to_update
    if not len(section_ids):
        raise BadRequestError('Required parameters are missing.')

    canvas_sis_term_id = course.term['sis_term_id']
    term = BerkeleyTerm.from_canvas_sis_term_id(canvas_sis_term_id)
    sis_sections = data_loch.get_sections(term_id=term.to_sis_term_id(), section_ids=section_ids)
    if not (sis_sections and len(sis_sections)):
        raise ResourceNotFoundError(f'No sections found with IDs {section_ids}')

    def _section(section):
        section_name = ' '.join([section['course_name'], section['instruction_format'], section['section_number']])
        section_name += f" ({section['instruction_mode']})"
        return {
            'section_id': section['section_id'],
            'course_id': section['course_id'],
            'name': section_name,
            'status': 'deleted' if section['section_id'] in sections_to_remove else 'active',
            'start_date': None,
            'end_date': None,
        }
    sections = [_section(s) for s in sis_sections]
    with SisImportCsv.create(fieldnames=['section_id', 'course_id', 'name', 'status', 'start_date', 'end_date']) as sis_import:
        sis_import.writerows(sections)
        sis_import.filehandle.close()
        if not canvas.post_sis_import(attachment=sis_import.tempfile.name):
            raise InternalServerError('Course sections SIS import failed.')
    return tolerant_jsonify({'jobStatus': 'Completed'})


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
    return csv_download_response(**canvas_site_roster_csv(canvas_site_id))


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
    section_ids = [section['id'] for section in canvas_sections if section['id']]
    term_id = canvas_sections[0]['termId']
    sis_sections = sort_course_sections(
        data_loch.get_sections(term_id, section_ids),
    )
    sis_sections_by_id = {s['section_id']: s for s in sis_sections}

    def _section(canvas_section):
        sis_section = sis_sections_by_id[canvas_section['id']]
        return {
            **canvas_section,
            **section_to_api_json(sis_section),
        }
    official_sections = [_section(cs) for cs in canvas_sections if cs['id']]
    return official_sections, section_ids


def _get_teaching_terms(section_ids):
    berkeley_terms = BerkeleyTerm.get_current_terms().values()
    # canvas_terms = canvas.get_terms()
    # TODO: find the intersection of berkeley_terms and canvas_terms
    teaching_sections = sort_course_sections(
        data_loch.get_instructing_sections(current_user.uid, [t.to_sis_term_id() for t in berkeley_terms]),
    )
    courses_by_term = {}
    for section in teaching_sections:
        course_id = section['course_id']
        term_id = section['term_id']
        if term_id not in courses_by_term:
            courses_by_term[term_id] = {}
        if course_id not in courses_by_term[term_id]:
            term = BerkeleyTerm.from_sis_term_id(term_id)
            courses_by_term[term_id][course_id] = course_to_api_json(term, section)
        courses_by_term[term_id][course_id]['sections'].append({
            **section_to_api_json(section),
            'isCourseSection': section['section_id'] in section_ids,
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
