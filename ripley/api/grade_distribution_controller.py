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
from flask_login import current_user
from ripley.api.errors import ResourceNotFoundError
from ripley.api.util import canvas_role_required
from ripley.externals import canvas
from ripley.externals.data_loch import find_course_by_name
from ripley.lib.berkeley_term import BerkeleyTerm
from ripley.lib.canvas_site_utils import canvas_section_to_api_json, canvas_site_to_api_json, \
    parse_canvas_sis_course_id
from ripley.lib.http import tolerant_jsonify
from ripley.merged.grade_distributions import get_grade_distribution_with_prior_enrollments, get_grade_distributions


@app.route('/api/grade_distribution/<canvas_site_id>')
@canvas_role_required('TeacherEnrollment')
def get_grade_distribution(canvas_site_id):
    course = canvas.get_course(canvas_site_id)
    course_name, term = parse_canvas_sis_course_id(course.sis_course_id)
    canvas_sections = canvas.get_course_sections(canvas_site_id)
    sis_sections = [canvas_section_to_api_json(cs) for cs in canvas_sections if cs.sis_section_id]
    distribution = {
        'canvasSite': canvas_site_to_api_json(course),
        'courseName': course_name,
    }
    if sis_sections:
        term_id = term.to_sis_term_id()
        section_ids = [s['id'] for s in sis_sections]
        instructor_uid = None if current_user.is_admin else current_user.uid
        gpa_term_distribution_by_demographic, grade_distribution_by_term = get_grade_distributions(term_id, section_ids, instructor_uid)
        if gpa_term_distribution_by_demographic is False:
            raise ResourceNotFoundError('This course does not meet the requirements necessary to generate a Grade Distribution.')
        if term_id in grade_distribution_by_term.keys():
            distribution['demographics'] = gpa_term_distribution_by_demographic
            distribution['enrollments'] = grade_distribution_by_term
            distribution['terms'] = [
                {
                    'id': term_id,
                    'name': BerkeleyTerm.from_sis_term_id(term_id).to_english(),
                } for term_id in grade_distribution_by_term.keys()
            ]
        else:
            distribution['demographics'] = []
            distribution['enrollments'] = {}
    else:
        distribution['demographics'] = []
        distribution['enrollments'] = {}
    return tolerant_jsonify(distribution)


@app.route('/api/grade_distribution/<canvas_site_id>/enrollment')
@canvas_role_required('TeacherEnrollment')
def get_prior_enrollment_grade_distribution(canvas_site_id):
    prior_course_name = request.args.get('prior')
    course = canvas.get_course(canvas_site_id)
    course_name, term = parse_canvas_sis_course_id(course.sis_course_id)
    grade_distribution = get_grade_distribution_with_prior_enrollments(
        term_id=term.to_sis_term_id(),
        course_name=course_name,
        instructor_uid=None if current_user.is_admin else current_user.uid,
        prior_course_name=prior_course_name,
    )
    return tolerant_jsonify(grade_distribution)


@app.route('/api/grade_distribution/search_courses')
@canvas_role_required('TeacherEnrollment')
def search_courses():
    search_text = request.args.get('searchText')
    results = find_course_by_name(search_text)
    return tolerant_jsonify({'results': [r['sis_course_name'] for r in results]})
