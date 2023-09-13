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
import secrets
from time import sleep

from flask import current_app as app
from flask_login import current_user
from ripley.api.errors import BadRequestError, InternalServerError, ResourceNotFoundError
from ripley.externals import canvas, data_loch
from ripley.externals.canvas import get_course_sections, get_roles, set_tab_hidden
from ripley.externals.s3 import upload_dated_csv
from ripley.lib.berkeley_course import course_section_name, course_to_api_json, section_to_api_json, \
    sort_course_sections
from ripley.lib.berkeley_term import BerkeleyTerm
from ripley.lib.calnet_utils import get_basic_attributes, roles_from_affiliations
from ripley.lib.egrade_utils import convert_per_grading_basis, get_canvas_course_student_grades
from ripley.lib.sis_import_csv import SisImportCsv
from ripley.lib.util import utc_now
from rq.job import get_current_job


def add_user_to_course_section(uid, role, course_section_id):
    canvas_user = canvas.get_sis_user_profile(uid)
    if not canvas_user:
        import_users([uid])
        canvas_user = canvas.get_sis_user_profile(uid)
    if not canvas_user:
        app.logger.warning(f'Unable to find or create Canvas user for UID={uid}')
        return None
    canvas_section = canvas.get_section(section_id=course_section_id, api_call=False, use_sis_id=True)
    if not canvas_section:
        app.logger.warning(f'No Canvas section found with course_section_id={course_section_id})')
        return None
    return canvas_section.enroll_user(
        canvas_user['id'],
        **{
            'enrollment[type]': role.base_role_type,
            'enrollment[role_id]': role.id,
            'enrollment[enrollment_state]': 'active',
            'enrollment[course_section_id]': course_section_id,
            'enrollment[notify]': False,
        },
    )


def create_canvas_project_site(name, owner_uid):
    account_id = app.config['CANVAS_BERKELEY_ACCOUNT_ID']
    project_site = canvas.get_account(account_id, api_call=False).create_course(
        course_code=name,
        name=name,
        sis_course_id=f'PROJ:{secrets.token_hex(8).upper()}',
        term_id=app.config['CANVAS_PROJECTS_TERM_ID'],
    )
    canvas_site_id = project_site['id']
    course = canvas.get_course(course_id=canvas_site_id, api_call=False)
    content_migration = course.create_content_migration(
        migration_type=app.config['CANVAS_PROJECTS_TEMPLATE_ID'],
    )
    migration_progress_id = None
    migration_start_time = None
    if content_migration['workflow_state'] != 'completed':
        migration_progress_id = content_migration['progress_url'].rsplit('/', 1)[-1]
        migration_start_time = utc_now()

    # Hide BigBlueButton, if present.
    for tab in canvas.get_tabs(course_id=canvas_site_id):
        tab_label = tab['label'].lower()
        if all(b in tab_label for b in ['big', 'blue', 'button']):
            set_tab_hidden(hidden=True, tab_id=tab['id'])
            break
    # Make the current_user the site owner.
    sis_user_profile = canvas.get_sis_user_profile(uid=owner_uid)
    owner_role = next((role for role in get_roles() if 'owner' in role.label.lower()), None)
    course.enroll_user(
        sis_user_profile['id'],
        role_id=owner_role.id,
        enrollment_state='active',
        notify=False,
    )
    if migration_progress_id:
        import_state = 'new'
        # TODO: Improve on this hard-coded wait.
        for index in range(0, 10):
            progress = canvas.get_progres(migration_progress_id)
            import_state = progress['body']['workflow_state']
            if import_state and import_state != 'completed':
                sleep(1)
            else:
                break
        elapsed_time = utc_now().timestamp() - migration_start_time.timestamp()
        status_description = 'completed' if import_state == 'completed' else 'not completed'
        app.logger.warning(f'Template-import of Canvas project site {canvas_site_id} {status_description} after {elapsed_time} seconds')
    return project_site


def get_canvas_course_id(course_slug):
    base_course_id = f'CRS:{course_slug.upper()}'
    course_id = base_course_id
    attempts = 0
    existing_site = None
    while attempts < 10:
        existing_site = canvas.get_course(course_id, use_sis_id=True)
        if not existing_site:
            break
        attempts += 1
        course_id = base_course_id + '-' + secrets.token_hex(4).upper()
    if existing_site:
        raise InternalServerError(f'Could not generate unique ID for Canvas site {course_slug}')
    return course_id


def get_canvas_sis_section_id(term_id, sis_section_id, ensure_unique=False):
    berkeley_term = BerkeleyTerm.from_sis_term_id(term_id)
    base_section_id = f'SEC:{berkeley_term.year}-{berkeley_term.season}-{sis_section_id}'
    section_id = base_section_id
    if ensure_unique:
        attempts = 0
        existing_section = None
        while attempts < 10:
            existing_section = canvas.get_section(section_id, use_sis_id=True)
            if not existing_section:
                break
            attempts += 1
            section_id = base_section_id + '-' + secrets.token_hex(4).upper()
        if existing_section:
            raise InternalServerError(f'Could not generate unique ID for Canvas section {term_id}-{sis_section_id}')
    return section_id


def get_grantable_roles():
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


def extract_berkeley_term_id(canvas_site):
    sis_term_id = canvas_site.term['sis_term_id']
    term = BerkeleyTerm.from_canvas_sis_term_id(sis_term_id) if sis_term_id else None
    return term.to_sis_term_id() if term else None


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
        app.logger.warning(f'Canvas site ID {canvas_site_id} has {len(section_ids)} sections, but SIS has {len(sis_sections)} sections.')

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


def get_teaching_terms(current_user=None, section_ids=None, sections=None, term_id=None, uid=None):
    berkeley_terms = BerkeleyTerm.get_current_terms()
    if term_id:
        canvas_terms = [term_id]
    else:
        canvas_terms = [term.sis_term_id for term in canvas.get_terms() if term.sis_term_id]
    terms = []
    for key, term in berkeley_terms.items():
        if term.to_canvas_sis_term_id() not in canvas_terms:
            continue
        if key != 'future' or term.season == 'D':
            terms.append(term)

    instructor_uid = None
    if uid:
        instructor_uid = uid
    elif current_user and (current_user.is_teaching or current_user.canvas_masquerading_user_id):
        instructor_uid = current_user.uid

    teaching_sections = []
    if instructor_uid:
        teaching_sections = data_loch.get_instructing_sections(instructor_uid, [t.to_sis_term_id() for t in terms]) or []
        teaching_sections = sort_course_sections(teaching_sections)

    if not len(teaching_sections) and sections:
        teaching_sections = sections

    courses_by_term = _build_courses_by_term(teaching_sections, term_id, section_ids)

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


def import_users(uids):
    users = []
    batch_size = 1000
    for batch in [uids[i:i + batch_size] for i in range(0, len(uids), batch_size)]:
        rows = get_basic_attributes(batch)
        for uid, row in rows.items():
            person_type = getattr(row, 'person_type', None)
            if person_type == 'Z':
                continue
            user = {
                'affiliations': row['affiliations'],
                'email_address': row['email_address'],
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'ldap_uid': uid,
                'roles': roles_from_affiliations(row['affiliations']),
                'sid': row['sid'],
            }
            if person_type != 'A' or any(item for item in ['student', 'staff', 'faculty', 'guest'] if user['roles'][item]):
                users.append(csv_row_for_campus_user(user))
    with SisImportCsv.create(['user_id', 'login_id', 'first_name', 'last_name', 'email', 'status']) as users_csv:
        users_csv.writerows(users)
        users_csv.filehandle.close()

        upload_dated_csv(
            users_csv.tempfile.name,
            'user-provision-sis-import',
            'canvas_sis_imports',
            utc_now().strftime('%F_%H-%M-%S'),
        )

        app.logger.debug('Posting user provisioning SIS import.')
        sis_import = canvas.post_sis_import(attachment=users_csv.tempfile.name)
        if not sis_import:
            raise InternalServerError('User provisioning SIS import failed.')
        return sis_import


def _build_courses_by_term(teaching_sections, term_id, section_ids):
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
        section_feed = section_to_api_json(section, co_instructor_sections)
        if section_ids:
            section_feed['isCourseSection'] = section_id in section_ids
        courses_by_term[term_id][course_id]['sections'].append(section_feed)
    return courses_by_term


def prepare_egrades_export(canvas_site_id, grade_type, pnp_cutoff, section_id, term_id):
    app.logger.warning(f'E-Grades job started for course {canvas_site_id}')
    official_grades = []
    canvas_section_id = None
    for canvas_course_section in get_course_sections(canvas_site_id):
        berkeley_section_id, berkeley_term = parse_canvas_sis_section_id(canvas_course_section.sis_section_id)
        if berkeley_section_id == section_id:
            canvas_section_id = canvas_course_section.id
            break
    if canvas_section_id:
        enrollments = canvas.get_section(canvas_section_id, api_call=False).get_enrollments()
        for enrollment in enrollments:
            grades = _extract_grades([enrollment])
            student = enrollment.user
            uid = student['login_id'] if 'login_id' in student else None
            official_grade = {
                'current_grade': grades['current_grade'],
                'final_grade': grades['final_grade'],
                'name': student['sortable_name'],
                'override_grade': grades['override_grade'],
                'uid': uid,
            }
            official_grades.append(official_grade)
    else:
        raise BadRequestError(f'Section {section_id} not found in context of Canvas course site {canvas_site_id}.')

    rows = []
    for row in get_canvas_course_student_grades(canvas_site_id=canvas_site_id, section_id=section_id, term_id=term_id):
        grading_basis = (row['grading_basis'] or '').upper()
        comment = None
        if grading_basis in ['CPN', 'DPN', 'EPN', 'PNP']:
            comment = 'P/NP grade'
        elif grading_basis in ['ESU', 'SUS']:
            comment = 'S/U grade'
        elif grading_basis == 'CNC':
            comment = 'C/NC grade'
        override_grade = row.get('grades', {}).get('override_grade')
        grade = convert_per_grading_basis(
            row['grades'][f'{grade_type}_grade'],
            override_grade,
            grading_basis,
            pnp_cutoff,
        )
        rows.append({
            'ID': row['sid'],
            'Name': row['name'],
            'Grade': grade,
            'Grading Basis': grading_basis,
            'Comments': comment or None,
        })
    return {
        'grade_type': grade_type,
        'rows': rows,
        'section_id': section_id,
        'term_id': term_id,
    }


def provision_course_site(uid, site_name, site_abbreviation, term_slug, section_ids, is_admin_by_ccns):
    term = BerkeleyTerm.from_slug(term_slug)

    terms_feed = []
    # Admins can specify semester and CCNs directly, without access checks.
    if is_admin_by_ccns:
        sections = sort_course_sections(
            data_loch.get_sections(term.to_sis_term_id(), section_ids) or [],
        )
        terms_feed = get_teaching_terms(sections=sections)
    # Otherwise, the user must have instructor access (direct or inherited via section nesting) to all sections.
    else:
        terms_feed = get_teaching_terms(section_ids=section_ids, term_id=term.to_canvas_sis_term_id(), uid=uid)

    courses_list = terms_feed[0]['classes'] if terms_feed else []
    if not courses_list:
        raise BadRequestError('No candidate courses found.')

    course_slug = courses_list[0]['slug']

    # Identify department subaccount
    dept_name = courses_list[0]['deptName']
    account = _subaccount_for_department(dept_name)
    defined_roles = list(account.get_roles())
    teacher_role = next((r for r in defined_roles if r.label == 'Teacher'), None)
    lead_ta_role = next((r for r in defined_roles if r.label == 'Lead TA'), None)

    sis_term_id = term.to_canvas_sis_term_id()
    sis_course_id = get_canvas_course_id(course_slug)

    with SisImportCsv.create(fieldnames=['course_id', 'short_name', 'long_name', 'account_id', 'term_id', 'status']) as course_csv:
        course_csv.writerow({
            'course_id': sis_course_id,
            'short_name': site_abbreviation,
            'long_name': site_name,
            'account_id': account.sis_account_id,
            'term_id': sis_term_id,
            'status': 'active',
        })
        course_csv.filehandle.close()

        upload_dated_csv(
            course_csv.tempfile.name,
            f"course-provision-{sis_course_id.replace(':', '-')}-course-sis-import",
            'canvas_sis_imports',
            utc_now().strftime('%F_%H-%M-%S'),
        )

        app.logger.debug(f'Posting course SIS import (sis_course_id={sis_course_id}).')
        sis_import = canvas.post_sis_import(attachment=course_csv.tempfile.name)
        if not sis_import:
            raise InternalServerError(f'Course sections SIS import failed (sis_course_id={sis_course_id}).')

    course = canvas.get_course(sis_course_id, use_sis_id=True)
    if not course:
        raise InternalServerError(f'Canvas course lookup failed (sis_course_id={sis_course_id}).')

    # TODO Adjust settings (hide conferences and grade distributions, set default view)

    # Section definitions
    section_feeds = []
    section_roles = {}
    explicit_sections_for_instructor = []
    all_sections = []

    for c in courses_list:
        for s in c['sections']:
            if s['id'] in section_ids:
                all_sections.append(s)
                _prepare_section_definition(
                    s,
                    course,
                    uid,
                    term.to_sis_term_id(),
                    lead_ta_role,
                    teacher_role,
                    is_admin_by_ccns,
                    section_feeds,
                    section_roles,
                    explicit_sections_for_instructor,
                )

    with SisImportCsv.create(fieldnames=['section_id', 'course_id', 'name', 'status', 'start_date', 'end_date']) as sections_csv:
        sections_csv.writerows(section_feeds)
        sections_csv.filehandle.close()

        upload_dated_csv(
            sections_csv.tempfile.name,
            f"course-provision-{course.sis_course_id.replace(':', '-')}-sections-sis-import",
            'canvas_sis_imports',
            utc_now().strftime('%F_%H-%M-%S'),
        )

        app.logger.debug(f'Posting course sections SIS import (canvas_site_id={course.id}).')
        sis_import = canvas.post_sis_import(attachment=sections_csv.tempfile.name)
        if not sis_import:
            raise InternalServerError(f'Course sections SIS import failed (canvas_site_id={course.id}).')

    if not is_admin_by_ccns:
        _add_instructor_to_site(
            uid,
            course,
            term.to_sis_term_id(),
            section_roles,
            teacher_role,
            explicit_sections_for_instructor,
            section_feeds,
        )

    # Background enrollment update
    job = get_current_job()
    if job:
        job = get_current_job()
        job.meta['courseSiteUrl'] = f"{app.config['CANVAS_API_URL']}/courses/{course.id}"
        job.save_meta()
    _update_section_enrollments(sis_term_id, course, section_feeds, [], sis_import)


def _prepare_section_definition(
    section,
    course,
    uid,
    sis_term_id,
    lead_ta_role,
    teacher_role,
    is_admin_by_ccns,
    section_feeds,
    section_roles,
    explicit_sections_for_instructor,
):
    sis_section_id = get_canvas_sis_section_id(sis_term_id, section['id'], ensure_unique=True)
    section_feed = {
        'section_id': sis_section_id,
        'course_id': course.sis_course_id,
        'name': f"{section['courseCode']} {section['name']}",
        'status': 'active',
        'start_date': None,
        'end_date': None,
    }
    section_feeds.append(section_feed)
    if not is_admin_by_ccns:
        instructing_assignment = next((i for i in section['instructors'] if i['uid'] == uid), None)
        if instructing_assignment:
            explicit_sections_for_instructor.append(section_feed)
            if instructing_assignment['role'] == 'APRX':
                section_roles[sis_section_id] = lead_ta_role and lead_ta_role.id
            else:
                section_roles[sis_section_id] = teacher_role and teacher_role.id


def _add_instructor_to_site(
    uid,
    course,
    sis_term_id,
    section_roles,
    teacher_role,
    explicit_sections_for_instructor,
    section_feeds,
):
    instructor_role_id = section_roles[section_feeds[0]['section_id']] or (teacher_role and teacher_role.id)
    sis_user_profile = canvas.get_sis_user_profile(uid)
    if not sis_user_profile:
        user_result = data_loch.get_users(uids=[uid])
        if user_result:
            with SisImportCsv.create(['user_id', 'login_id', 'first_name', 'last_name', 'email', 'status']) as users_csv:
                users_csv.writerow(csv_row_for_campus_user(user_result[0]))
                users_csv.filehandle.close()
                sis_import = canvas.post_sis_import(attachment=users_csv.tempfile.name)
                if not sis_import:
                    raise InternalServerError(f'Course sections SIS import failed (canvas_site_id={course.id}).')
        sis_user_profile = canvas.get_sis_user_profile(uid)
        if not sis_user_profile:
            raise InternalServerError(f'Failed to create instructor account (uids={uid}).')

    user_section_feed = explicit_sections_for_instructor[0] if explicit_sections_for_instructor else section_feeds[0]
    sis_section_id = user_section_feed['section_id']
    canvas_section = canvas.get_section(section_id=f'sis_section_id:{sis_section_id}', api_call=False, use_sis_id=True)
    canvas_section.enroll_user(
        sis_user_profile['id'],
        role_id=instructor_role_id,
        enrollment_state='active',
        notify=False,
    )


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
            'section_id': get_canvas_sis_section_id(section['term_id'], section['section_id']),
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

        # We need the complete list of site sections, including those we're not updating, in order to pass on a
        # complete list of primary sections in the course.
        all_site_official_sections, all_site_section_ids, all_site_sis_sections = get_official_sections(course.id)
        primary_sections = [s for s in all_site_sis_sections if s['is_primary']]

        job = get_current_job()
        if job:
            job.meta['sis_import_id'] = sis_import.id
            job.save_meta()
        _update_section_enrollments(canvas_sis_term_id, course, sections, section_ids_to_remove, sis_import, primary_sections)


def user_id_from_attributes(attributes):
    if (
        attributes['sid']
        and attributes['affiliations']
        and ('STUDENT-TYPE-REGISTERED' in attributes['affiliations'] or 'STUDENT-TYPE-NOT REGISTERED' in attributes['affiliations'])
    ):
        return attributes['sid']
    else:
        return f"UID:{attributes['ldap_uid']}"


def _canvas_role_sort_key(role):
    # The default Canvas UX orders roles by base role type, then built-ins first, then role ID.
    role_type_order = ['StudentEnrollment', 'TeacherEnrollment', 'TaEnrollment', 'DesignerEnrollment', 'ObserverEnrollment']
    type_key = role_type_order.index(role.base_role_type)
    # Custom roles have a "workflow_state" of "active" rather than "built_in".
    workflow_key = 0 if role.workflow_state == 'built_in' else 1
    return f'{type_key}_{workflow_key}_{role.id}'


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
    keys = ['current_score', 'current_grade', 'final_score', 'final_grade', 'override_score', 'override_grade']
    grade_hash = dict.fromkeys(keys, None)
    enrollments = list(filter(lambda e: hasattr(e, 'grades'), enrollments))
    if enrollments:
        api_grades = enrollments[0].grades
        for key in keys:
            if key in api_grades:
                grade_hash[key] = api_grades[key]
    return grade_hash


def _subaccount_for_department(dept_name):
    dept_name = dept_name.replace('/', '_')
    subaccount_id = f'ACCT:{dept_name}'
    subaccount = canvas.get_account(subaccount_id, use_sis_id=True)
    if subaccount:
        return subaccount
    else:
        with SisImportCsv.create(fieldnames=['account_id', 'parent_account_id', 'name', 'status']) as accounts_csv:
            accounts_csv.writerow({
                'account_id': subaccount_id,
                'parent_account_id': 'ACCT:OFFICIAL_COURSES',
                'name': dept_name,
                'status': 'active',
            })
            accounts_csv.filehandle.close()
            sis_import = canvas.post_sis_import(attachment=accounts_csv.tempfile.name)
            if not sis_import:
                raise InternalServerError(f'Subccount SIS import failed (account_id={subaccount_id}).')

        subaccount = canvas.get_account(subaccount_id, use_sis_id=True)
        if subaccount:
            return subaccount
        else:
            raise InternalServerError(f'Could not find bCourses account for department {dept_name}')


def _update_section_enrollments(sis_term_id, course, all_sections, deleted_section_ids, sis_import, primary_sections=None):
    from ripley.jobs.bcourses_provision_site_job import BcoursesProvisionSiteJob

    params = {
        'canvas_site_id': course.id,
        'deleted_section_ids': deleted_section_ids,
        'primary_sections': primary_sections,
        'sis_course_id': course.sis_course_id,
        'sis_term_id': sis_term_id,
        'updated_sis_section_ids': [s['section_id'] for s in all_sections if s['status'] == 'active'],
    }
    app.logger.info(f'SIS import (id={sis_import.id}) {sis_import.workflow_state}; starting job BcoursesProvisionSiteJob \
                    (sis_course_id={course.sis_course_id}).')
    BcoursesProvisionSiteJob(app.app_context).run(force_run=True, concurrent=True, params=params)
