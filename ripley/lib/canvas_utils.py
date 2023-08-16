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

from itertools import groupby
import re

from flask import current_app as app
from ripley.api.errors import InternalServerError, ResourceNotFoundError
from ripley.externals import canvas, data_loch
from ripley.externals.s3 import upload_dated_csv
from ripley.lib.berkeley_course import course_section_name, course_to_api_json, section_to_api_json, \
    sort_course_sections
from ripley.lib.berkeley_term import BerkeleyTerm
from ripley.lib.sis_import_csv import SisImportCsv
from ripley.lib.util import utc_now
from ripley.models.job_history import JobHistory
from rq.job import get_current_job


def get_canvas_sis_section_id(sis_section):
    berkeley_term = BerkeleyTerm.from_sis_term_id(sis_section['term_id'])
    return f"SEC:{berkeley_term.year}-{berkeley_term.season}-{sis_section['section_id']}"


def parse_canvas_sis_section_id(sis_section_id):
    section_id, berkeley_term = None, None
    if sis_section_id:
        m = re.fullmatch(r'^(SEC:)?(?P<term_year>\d{4})-(?P<term_code>[A-D])-(?P<section_id>\d+).*?$', sis_section_id)
        section_id = m['section_id'] if m else None
        berkeley_term = BerkeleyTerm(m['term_year'], m['term_code']) if m else None
    return section_id, berkeley_term


def api_formatted_course_role(role):
    return {
        'student': 'StudentEnrollment',
        'ta': 'TaEnrollment',
        'teacher': 'TeacherEnrollment',
    }.get(role, role)


def canvas_section_to_api_json(canvas_section):
    section_id, berkeley_term = parse_canvas_sis_section_id(canvas_section.sis_section_id)
    return {
        'id': section_id,
        'canvasName': canvas_section.name,
        'sisId': canvas_section.sis_section_id,
        'termId': berkeley_term.to_sis_term_id() if berkeley_term else None,
    }


def canvas_site_to_api_json(canvas_site):
    canvas_site_id = canvas_site.id
    return {
        'canvasSiteId': canvas_site_id,
        'courseCode': canvas_site.course_code if canvas_site else None,
        'name': canvas_site.name.strip() if canvas_site else None,
        'sisCourseId': canvas_site.sis_course_id if canvas_site else None,
        'term': _canvas_site_term_json(canvas_site),
        'url': f"{app.config['CANVAS_API_URL']}/courses/{canvas_site_id}",
    }


def csv_formatted_course_role(role):
    return {
        'StudentEnrollment': 'student',
        'TaEnrollment': 'ta',
        'TeacherEnrollment': 'teacher',
    }.get(role, role)


def csv_row_for_campus_user(user):
    return {
        'user_id': user_id_from_attributes(user),
        'login_id': str(user['ldap_uid']),
        'first_name': user['first_name'],
        'last_name': user['last_name'],
        'email': user['email_address'],
        'status': 'active',
    }


def format_term_enrollments_export(term_id):
    return f"{term_id.replace(':', '-')}-term-enrollments-export"


def get_official_sections(canvas_site_id):
    canvas_sections = canvas.get_course_sections(canvas_site_id)
    canvas_sections = [canvas_section_to_api_json(cs) for cs in canvas_sections if cs.sis_section_id]
    canvas_sections_by_id = {cs['id']: cs for cs in canvas_sections if cs['id']}
    section_ids = list(canvas_sections_by_id.keys())
    term_id = canvas_sections[0]['termId']
    sis_sections = sort_course_sections(
        data_loch.get_sections(term_id, section_ids) or [],
    )
    if len(sis_sections) != len(section_ids):
        app.logger.warn(f'Canvas site ID {canvas_site_id} has {len(section_ids)} sections, but SIS has {len(sis_sections)} sections.')

    def _section(section_id, rows):
        canvas_section = canvas_sections_by_id[section_id]
        return {
            **canvas_section,
            **section_to_api_json(rows[0], rows[1:]),
        }
    official_sections = []
    for section_id, rows in groupby(sis_sections, lambda s: s['section_id']):
        official_sections.append(_section(section_id, list(rows)))
    return official_sections, section_ids, sis_sections


def get_teaching_terms(current_user, section_ids, sections):
    berkeley_terms = BerkeleyTerm.get_current_terms()
    canvas_terms = [term.sis_term_id for term in canvas.get_terms() if term.sis_term_id]
    terms = []
    for key, term in berkeley_terms.items():
        if term.to_canvas_sis_term_id() not in canvas_terms:
            continue
        if key != 'future' or term.season == 'D':
            terms.append(term)

    teaching_sections = []
    if (current_user.is_teaching or current_user.canvas_masquerading_user_id):
        instructor_uid = current_user.uid
        teaching_sections = sort_course_sections(
            data_loch.get_instructing_sections(instructor_uid, [t.to_sis_term_id() for t in terms]) or [],
        )
    if not len(teaching_sections):
        teaching_sections = sections
    courses_by_term = {}
    for section_id, sections in groupby(teaching_sections, lambda s: s['section_id']):
        sections = list(sections)
        section = next((s for s in sections if s.get('is_co_instructor', False) is False), None)
        co_instructor_sections = [s for s in sections if s.get('is_co_instructor', True) is True]
        course_id = section['course_id']
        term_id = section['term_id']
        if term_id not in courses_by_term:
            courses_by_term[term_id] = {}
        if course_id not in courses_by_term[term_id]:
            term = BerkeleyTerm.from_sis_term_id(term_id)
            courses_by_term[term_id][course_id] = course_to_api_json(term, section)
        courses_by_term[term_id][course_id]['sections'].append({
            **section_to_api_json(section, co_instructor_sections),
            'isCourseSection': section_id in section_ids,
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


def prepare_egrade_export(course):
    app.logger.warning(f'E-Grades job started for course {course.id}')
    official_grades = []
    for user in course.get_users(enrollment_type='student', include='enrollments'):
        grades = _extract_grades(user['enrollments'])
        official_grades.append({
            'current_grade': grades['current_grade'],
            'final_grade': grades['final_grade'],
            'name': user.sortable_name,
            'override_grade': grades['override_grade'],
            'uid': user.login_id if hasattr(user, 'login_id') else None,
        })
    return official_grades


def sis_enrollment_status_to_canvas_course_role(sis_enrollment_status):
    return {
        'E': 'StudentEnrollment',
        'W': 'Waitlist Student',
        'C': 'StudentEnrollment',
    }.get(sis_enrollment_status, None)


def uid_from_canvas_login_id(login_id):
    result = {'uid': None, 'inactivePrefix': None}
    match = re.match('^(inactive-)?([0-9]+)$', login_id)
    if match:
        try:
            result = {'uid': str(match.group(2)), 'inactivePrefix': bool(match.group(1))}
        except Exception:
            pass
    return result


def update_canvas_sections(course, all_section_ids, section_ids_to_remove):
    canvas_sis_term_id = course.term['sis_term_id']
    term = BerkeleyTerm.from_canvas_sis_term_id(canvas_sis_term_id)
    sis_sections = data_loch.get_sections(term_id=term.to_sis_term_id(), section_ids=all_section_ids)
    if not (sis_sections and len(sis_sections)):
        raise ResourceNotFoundError(f'No sections found with IDs {", ".join(all_section_ids)}')

    def _section(section):
        return {
            'section_id': get_canvas_sis_section_id(section),
            'course_id': course.sis_course_id,
            'name': f"{section['course_name']} {course_section_name(section)}",
            'status': 'deleted' if section['section_id'] in section_ids_to_remove else 'active',
            'start_date': None,
            'end_date': None,
        }
    sections = [_section(s) for s in sis_sections]
    with SisImportCsv.create(fieldnames=['section_id', 'course_id', 'name', 'status', 'start_date', 'end_date']) as sections_csv:
        sections_csv.writerows(sections)
        sections_csv.filehandle.close()

        upload_dated_csv(
            sections_csv.tempfile.name,
            f"course-provision-{canvas_sis_term_id.replace(':', '-')}-{course.sis_course_id.replace(':', '-')}-sections-sis-import",
            'canvas_sis_imports',
            utc_now().strftime('%F_%H-%M-%S'),
        )

        app.logger.debug(f'Posting course sections SIS import (canvas_site_id={course.id}).')
        sis_import = canvas.post_sis_import(attachment=sections_csv.tempfile.name)
        if not sis_import:
            raise InternalServerError(f'Course sections SIS import failed (canvas_site_id={course.id}).')
        job = get_current_job()
        if job:
            job.meta['sis_import_id'] = sis_import.id
        bg_job = _update_enrollments_in_background(canvas_sis_term_id, course, sections, section_ids_to_remove, sis_import)
        if bg_job:
            job.meta['enrollment_update_job_id'] = bg_job.id
        job.save_meta()


def user_id_from_attributes(attributes):
    if (
        attributes['sid']
        and attributes['affiliations']
        and ('STUDENT-TYPE-REGISTERED' in attributes['affiliations'] or 'STUDENT-TYPE-NOT REGISTERED' in attributes['affiliations'])
    ):
        return attributes['sid']
    else:
        return f"UID:{attributes['ldap_uid']}"


def _canvas_site_term_json(canvas_site):
    api_json = None
    if canvas_site:
        canvas_sis_term_id = canvas_site.term['sis_term_id']
        term = BerkeleyTerm.from_canvas_sis_term_id(canvas_sis_term_id) if canvas_sis_term_id else None
        if term:
            api_json = {
                'term_yr': term.year,
                'term_cd': term.season,
                'name': term.to_english(),
            }
    return api_json


def _extract_grades(enrollments):
    keys = ['current_score', 'current_grade', 'final_score', 'final_grade override_score', 'override_grade']
    grade_hash = dict.fromkeys(keys, None)
    enrollments = filter(lambda e: e.type == 'StudentEnrollment' and hasattr(e, 'grades'), enrollments)
    if enrollments:
        api_grades = enrollments[0].grades
        for key in keys:
            if key in api_grades:
                grade_hash[key] = api_grades[key]
    return grade_hash


def _update_enrollments_in_background(sis_term_id, course, all_sections, deleted_section_ids, sis_import):
    from ripley.jobs.bcourses_provision_site_job import BcoursesProvisionSiteJob

    params = {
        'canvas_site_id': course.id,
        'deleted_section_ids': deleted_section_ids,
        'sis_course_id': course.sis_course_id,
        'sis_term_id': sis_term_id,
        'updated_sis_section_ids': [s['section_id'] for s in all_sections if s['status'] == 'active'],
    }
    app.logger.info(f'SIS import (id={sis_import.id}) {sis_import.workflow_state}; starting job BcoursesProvisionSiteJob \
                    (sis_course_id={course.sis_course_id}).')
    BcoursesProvisionSiteJob(app.app_context).run_async(force_run=True, params=params)
    return JobHistory.get_running_job(job_key=BcoursesProvisionSiteJob.key())
