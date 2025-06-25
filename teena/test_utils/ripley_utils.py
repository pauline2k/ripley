"""
Copyright ©2025. The Regents of the University of California (Regents). All Rights Reserved.

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
from itertools import groupby
from random import shuffle
import re

from flask import current_app as app
from ripley import db, std_commit
from ripley.externals import data_loch
from sqlalchemy import text
from teena.models.course import Course
from teena.models.person import Person, PersonWithRole
from teena.models.section import Section, SectionEnrollment
from teena.test_utils import utils


# Course data


def get_cs_course_id_from_catalog_id(term, catalog_id_prefix):
    # If testing Law site templates, don't insist on secondary sections
    if catalog_id_prefix == app.config['COURSE_TEMPLATE_DEPT']:
        sql = f"""SELECT cs_course_id
                    FROM sis_data.edo_sections
                   WHERE sis_term_id = '{term.sis_id}'
                     AND sis_course_name LIKE '{catalog_id_prefix}%'
                GROUP BY cs_course_id
                   LIMIT 1"""
    else:
        sql = f"""SELECT cs_course_id
                    FROM sis_data.edo_sections
                   WHERE sis_term_id = '{term.sis_id}'
                     AND sis_course_name LIKE '{catalog_id_prefix}%'
                     AND is_primary IS FALSE
                GROUP BY cs_course_id
                  HAVING COUNT(*) > 1
                   LIMIT 1"""
    app.logger.info(sql)
    results = data_loch.safe_execute_rds(sql)
    return results[0]['cs_course_id'] if results else None


def get_cs_course_id_from_section_id(term, section_id):
    sql = f"""SELECT cs_course_id
                FROM sis_data.edo_sections
               WHERE sis_term_id = '{term.sis_id}'
                 AND sis_section_id = '{section_id}'"""
    app.logger.info(sql)
    results = data_loch.safe_execute_rds(sql)
    return results[0]['cs_course_id']


def get_course_from_sections(term, sections):
    teachers = []
    primary_sections = [sec for sec in sections if sec.is_primary]
    for prim in primary_sections:
        for i_r in prim.instructors_with_roles:
            if i_r.user not in teachers and i_r.role_code == 'PI':
                teachers.append(i_r.user)
    codes = []
    for sect in sections:
        if sect.course not in codes:
            codes.append(sect.course)
    codes.sort()
    app.logger.info(f'Course {codes[0]} in {term.name} has section count {len(sections)}')
    return Course({
        'code': codes[0],
        'sections': sections,
        'teachers': teachers,
        'term': term,
        'title': sections[0].course_title,
    })


def get_instructor_term_courses(term, instructor):
    sql = f"""SELECT sis_section_id,
                     is_primary
                FROM sis_data.edo_sections
               WHERE sis_term_id = '{term.sis_id}'
                 AND instructor_uid = '{instructor.uid}'"""
    app.logger.info(sql)
    results = data_loch.safe_execute_rds(sql)
    section_ids = [r['sis_section_id'] for r in results]

    primary_section_ids = [r['sis_section_id'] for r in results if r['is_primary']]
    if primary_section_ids:
        sql = f"""SELECT sis_section_id,
                         primary_associated_section_id
                    FROM sis_data.edo_sections
                   WHERE sis_term_id = '{term.sis_id}'
                     AND is_primary IS FALSE
                     AND primary_associated_section_id IN ({utils.in_op(primary_section_ids)})"""
        app.logger.info(sql)
        results = data_loch.safe_execute_rds(sql)
        section_ids.extend([r['sis_section_id'] for r in results])

    results = _sections_result_from_section_ids(term, section_ids)
    sections_data = _get_test_course_section_data(results)
    sections = _section_data_to_sections(sections_data, [instructor])

    course_sections_groups = [list(result) for key, result in groupby(sections, key=lambda s: [s.cs_course_id])]
    courses = []
    for group in course_sections_groups:
        course = get_course_from_sections(term, group)
        courses.append(course)
    return courses


def get_course_from_catalog_id_prefix(term, catalog_id_prefix):
    cs_id = get_cs_course_id_from_catalog_id(term, catalog_id_prefix)
    if cs_id:
        course = _get_course_from_cs_course_id(term, cs_id)
        if course:
            if course.teachers:
                return course
            else:
                app.logger.info(f'Course code {catalog_id_prefix} in term {term.sis_id} has no teachers')
                return None
        else:
            app.logger.info(f'No usable test course found matching course code {catalog_id_prefix} in term {term.sis_id}')
            return None


def _get_course_from_cs_course_id(term, cs_course_id):
    instructors = get_course_instructors(term, cs_course_id)
    results = _sections_result_from_cs_course_id(term, cs_course_id)
    sections_data = _get_test_course_section_data(results)
    sections = _section_data_to_sections(sections_data, instructors)
    primary_sections = [sec for sec in sections if sec.is_primary]
    secondary_sections = [sec for sec in sections if not sec.is_primary]

    # Course can have multiple primaries, each with different instructor(s). Keep only primaries with same instructor(s).
    desired_teacher_uids = [role.user.uid for role in primary_sections[0].instructors_with_roles]
    desired_teacher_uids.sort()
    teacher_primary_sections = []
    for sec in primary_sections:
        sec_uids = [ir.user.uid for ir in sec.instructors_with_roles]
        sec_uids.sort()
        if sec_uids == desired_teacher_uids:
            teacher_primary_sections.append(sec)
    sections = teacher_primary_sections + secondary_sections
    return get_course_from_sections(term, sections)


# Sections


def get_sections_from_section_ids(term, section_ids):
    query_result = _sections_result_from_section_ids(term, section_ids)
    section_data = _get_test_course_section_data(query_result)
    return _section_data_to_sections(section_data)


def _translate_instruction_mode(mode_code):
    if mode_code == 'EF':
        return '(Flexible)'
    elif mode_code == 'EH':
        return '(Hybrid)'
    elif mode_code == 'ER':
        return '(Remote)'
    elif mode_code == 'O':
        return '(Online)'
    elif mode_code == 'P':
        return '(In Person)'
    elif mode_code == 'W':
        return '(Web-based)'
    else:
        return f'({mode_code})'


def _translate_schedule_days(days_string):
    if days_string:
        return days_string.replace('MO', 'M').replace('WE', 'W').replace('FR', 'F').strip()
    else:
        return None


def _translate_schedule_time(time_string):
    if time_string == '00:00' or not time_string:
        return '—'
    else:
        return f"{datetime.strptime(time_string, '%H:%M').strftime('%l:%M%p')[:-1]}"


def _sections_result_from_cs_course_id(term, cs_course_id):
    sql = f"""SELECT sis_data.edo_sections.sis_section_id AS id,
                     sis_data.edo_sections.is_primary,
                     sis_data.edo_sections.primary_associated_section_id,
                     sis_data.edo_sections.cs_course_id,
                     sis_data.edo_sections.sis_course_name AS code,
                     sis_data.edo_sections.sis_course_title AS title,
                     sis_data.edo_sections.sis_instruction_format AS format,
                     sis_data.edo_sections.sis_section_num AS number,
                     sis_data.edo_sections.instructor_uid,
                     sis_data.edo_sections.instructor_role_code,
                     sis_data.edo_sections.instruction_mode AS mode,
                     sis_data.edo_sections.instructor_name,
                     sis_data.edo_basic_attributes.email_address AS instructor_email_address,
                     sis_data.edo_basic_attributes.sid AS instructor_sid,
                     sis_data.edo_sections.meeting_location AS location,
                     sis_data.edo_sections.meeting_days AS days,
                     sis_data.edo_sections.meeting_end_date AS end_date,
                     sis_data.edo_sections.meeting_start_time AS start_time,
                     sis_data.edo_sections.meeting_end_time AS end_time
                FROM sis_data.edo_sections
           LEFT JOIN sis_data.edo_basic_attributes
                  ON sis_data.edo_sections.instructor_uid = sis_data.edo_basic_attributes.ldap_uid
               WHERE sis_data.edo_sections.sis_term_id = '{term.sis_id}'
                 AND cs_course_id = '{cs_course_id}'"""
    app.logger.info(sql)
    return data_loch.safe_execute_rds(sql)


def _sections_result_from_section_ids(term, section_ids):
    sql = f"""SELECT sis_data.edo_sections.sis_section_id AS id,
                     sis_data.edo_sections.is_primary,
                     sis_data.edo_sections.primary_associated_section_id,
                     sis_data.edo_sections.cs_course_id,
                     sis_data.edo_sections.sis_course_name AS code,
                     sis_data.edo_sections.sis_course_title AS title,
                     sis_data.edo_sections.sis_instruction_format AS format,
                     sis_data.edo_sections.sis_section_num AS number,
                     sis_data.edo_sections.instructor_uid,
                     sis_data.edo_sections.instructor_role_code,
                     sis_data.edo_sections.instruction_mode AS mode,
                     sis_data.edo_sections.instructor_name,
                     sis_data.edo_basic_attributes.email_address AS instructor_email_address,
                     sis_data.edo_basic_attributes.sid AS instructor_sid,
                     sis_data.edo_sections.meeting_location AS location,
                     sis_data.edo_sections.meeting_days AS days,
                     sis_data.edo_sections.meeting_end_date AS end_date,
                     sis_data.edo_sections.meeting_start_time AS start_time,
                     sis_data.edo_sections.meeting_end_time AS end_time
                FROM sis_data.edo_sections
                JOIN sis_data.edo_basic_attributes
                  ON sis_data.edo_sections.instructor_uid = sis_data.edo_basic_attributes.ldap_uid
               WHERE sis_data.edo_sections.sis_term_id = '{term.sis_id}'
                 AND sis_data.edo_sections.sis_section_id IN ({utils.in_op(section_ids)})"""
    app.logger.info(sql)
    return data_loch.safe_execute_rds(sql)


def _get_test_course_section_data(sections_result):
    sections_data = []
    for r in sections_result:
        mode = _translate_instruction_mode(r['mode'])
        days = _translate_schedule_days(r['days'])
        start = _translate_schedule_time(r['start_time'])
        finish = _translate_schedule_time(r['end_time'])
        schedule = f'{days} {start.strip()}-{finish.strip()}'.strip() if days else '—'
        location = r['location'] or '—'
        sections_data.append({
            'section_id': r['id'],
            'code': r['code'],
            'course_title': r['title'],
            'cs_course_id': r['cs_course_id'],
            'instruction_mode': mode,
            'instructor_email_address': r['instructor_email_address'],
            'instructor_name': r['instructor_name'],
            'instructor_role_code': r['instructor_role_code'],
            'instructor_sid': r['instructor_sid'],
            'instructor_uid': r['instructor_uid'],
            'is_primary': r['is_primary'],
            'label': f"{r['format']} {r['number']} {mode}",
            'location': re.sub(r'\s+', ' ', location),
            'primary_assoc_id': r['primary_associated_section_id'],
            'schedule': schedule,
        })
    return sections_data


def _section_data_to_sections(sections_data, instructors=None):
    if not instructors:
        instructors = []
        instructor_data = []
        for data in sections_data:
            if data['instructor_uid']:
                instructor_data.append(data)
        sorted_instructors = sorted(instructor_data, key=lambda i: i['instructor_uid'])
        instructor_groups = [list(inst_result) for key, inst_result in groupby(sorted_instructors,
                                                                               key=lambda i: i['instructor_uid'])]
        for inst_group in instructor_groups:
            instructors.append(Person({
                'email': inst_group[0]['instructor_email_address'],
                'full_name': inst_group[0]['instructor_name'],
                'sid': inst_group[0]['instructor_sid'],
                'uid': inst_group[0]['instructor_uid'],
            }))

    sections = []
    sorted_sections = sorted(sections_data, key=lambda ss: ss['section_id'])
    section_groups = [list(sec_result) for key, sec_result in groupby(sorted_sections, key=lambda s: s['section_id'])]
    for sec_group in section_groups:
        teachers = []
        locations = []
        primary_assoc_ids = []
        schedules = []
        for sec in sec_group:
            for instr in instructors:
                if instr.uid == sec['instructor_uid']:
                    instr_with_role = PersonWithRole(instr, sec['instructor_role_code'])
                    if instr_with_role not in teachers:
                        teachers.append(instr_with_role)
            if sec['location'] not in locations:
                locations.append(sec['location'])
            if sec['primary_assoc_id'] not in primary_assoc_ids:
                primary_assoc_ids.append(sec['primary_assoc_id'])
            if sec['schedule'] not in schedules:
                schedules.append(sec['schedule'])

        sections.append(Section({
            'section_id': sec_group[0]['section_id'],
            'course': sec_group[0]['code'],
            'course_title': sec_group[0]['course_title'],
            'cs_course_id': sec_group[0]['cs_course_id'],
            'instruction_mode': sec_group[0]['instruction_mode'],
            'instructors_with_roles': teachers,
            'label': sec_group[0]['label'],
            'locations': locations,
            'is_primary': sec_group[0]['is_primary'],
            'primary_assoc_ids': primary_assoc_ids,
            'schedules': schedules,
        }))
    return sections


def expected_instr_section_data(site, specific_sections=None):
    instructor_data = []
    primaries = [s for s in site.sections if s.is_primary]
    sections = specific_sections or site.sections
    for section in sections:
        for i_r in section.instructors_with_roles:
            if section.is_primary:
                if i_r.role_code in ['PI', 'ICNT', 'INVT']:
                    i_r.user.role = 'Teacher'
                elif i_r.role_code == 'APRX':
                    i_r.user.role = 'Lead TA'
                else:
                    i_r.user.role = None
            else:
                if i_r.role_code in ['PI', 'TNIC']:
                    if primaries:
                        i_r.user.role = 'TA'
                    else:
                        i_r.user.role = 'Teacher'
                else:
                    i_r.user.role = None
            instructor_data.append({
                'uid': i_r.user.uid,
                'role': i_r.user.role.lower(),
                'section_id': section.section_id,
            })
    instructor_data.sort(key=lambda h: [h['uid'], h['section_id']])
    return instructor_data


def expected_student_section_data(site, specific_sections=None):
    student_data = []
    sections = specific_sections or site.sections
    for section in sections:
        for enroll in section.enrollments:
            student_data.append({
                'uid': enroll.student.uid,
                'role': ('student' if enroll.status == 'E' else 'waitlist student'),
                'section_id': enroll.section_id,
            })
    student_data.sort(key=lambda h: [h['uid'], h['section_id']])
    return student_data


# Course instructors


def get_course_instructors(term, cs_course_id):
    sql = f"""SELECT DISTINCT sis_data.edo_sections.instructor_uid,
                     sis_data.edo_sections.instructor_name,
                     sis_data.edo_basic_attributes.email_address,
                     sis_data.edo_basic_attributes.sid
                FROM sis_data.edo_sections
                JOIN sis_data.edo_basic_attributes
                  ON sis_data.edo_basic_attributes.ldap_uid = sis_data.edo_sections.instructor_uid
               WHERE sis_data.edo_sections.sis_term_id = '{term.sis_id}'
                 AND sis_data.edo_sections.cs_course_id = '{cs_course_id}'"""
    app.logger.info(sql)
    results = data_loch.safe_execute_rds(sql)
    instructors = []
    for row in results:
        instructors.append(Person({
            'email': row['email_address'],
            'full_name': row['instructor_name'],
            'sid': row['sid'],
            'uid': row['instructor_uid'],
        }))
    return instructors


def get_course_instructor_sections(course, instructor):
    sections = []
    for section in course.sections:
        for inst_role in section.instructors_with_roles:
            if inst_role.user.uid == instructor.uid:
                sections.append(section)
    return sections


def get_course_instructor_roles(course, instructor):
    instr_sections = get_course_instructor_sections(course, instructor)
    roles = []
    for section in instr_sections:
        for inst_role in section.instructors_with_roles:
            if inst_role.user.uid == instructor.uid:
                roles.append(inst_role.role_code)
    roles = list(set(roles))
    return roles


def get_course_instructor_of_role_code(course, role_code):
    for section in course.sections:
        for i_r in section.instructors_with_roles:
            if i_r.role_code == role_code:
                return i_r


def get_primary_instructors(site):
    instructors = []
    for section in site.sections:
        for i_r in section.instructors_with_roles:
            if i_r.role_code == 'PI' and i_r.user not in instructors:
                instructors.append(i_r.user)
    app.logger.info(f'Primary instructors: {[vars(i) for i in instructors]}')
    return instructors


#   Course enrollment


def get_course_enrollment(course):
    sql = f"""SELECT enrollment.sis_section_id,
                     enrollment.ldap_uid AS uid,
                     sis_data.edo_basic_attributes.sid,
                     sis_data.edo_basic_attributes.first_name,
                     sis_data.edo_basic_attributes.last_name,
                     enrollment.grade,
                     enrollment.grading_basis,
                     enrollment.sis_enrollment_status AS status,
                     sis_data.edo_basic_attributes.email_address
                FROM sis_data.edo_enrollments enrollment
                JOIN sis_data.edo_basic_attributes
                  ON sis_data.edo_basic_attributes.ldap_uid = enrollment.ldap_uid
               WHERE enrollment.sis_term_id = '{course.term.sis_id}'
                 AND enrollment.sis_section_id IN ({utils.in_op(s.section_id for s in course.sections)})
                 AND enrollment.sis_enrollment_status IN ('E', 'W')
                 AND 'W' NOT IN (SELECT DISTINCT(primary_enrollment.grade)
                                   FROM sis_data.edo_enrollments primary_enrollment
                                   JOIN sis_data.edo_sections
                                     ON primary_enrollment.ldap_uid = enrollment.ldap_uid
                                    AND primary_enrollment.sis_term_id = enrollment.sis_term_id
                                    AND primary_enrollment.sis_section_id = sis_data.edo_sections.primary_associated_section_id
                                  WHERE sis_data.edo_sections.sis_term_id = enrollment.sis_term_id
                                    AND sis_data.edo_sections.sis_section_id = enrollment.sis_section_id)"""
    app.logger.info(sql)
    results = data_loch.safe_execute_rds(sql)
    results_to_enrollments(course, results)


def get_completed_enrollments(course):
    sql = f"""SELECT sis_data.edo_enrollments.sis_section_id,
                     sis_data.edo_enrollments.ldap_uid AS uid,
                     sis_data.edo_enrollments.grade,
                     sis_data.edo_enrollments.grading_basis,
                     sis_data.edo_enrollments.sis_enrollment_status AS status,
                     sis_data.edo_basic_attributes.sid,
                     sis_data.edo_basic_attributes.first_name,
                     sis_data.edo_basic_attributes.last_name,
                     sis_data.edo_basic_attributes.email_address
                FROM sis_data.edo_enrollments
           LEFT JOIN sis_data.edo_basic_attributes
                  ON sis_data.edo_basic_attributes.ldap_uid = sis_data.edo_enrollments.ldap_uid
               WHERE sis_data.edo_enrollments.sis_term_id = '{course.term.sis_id}'
                 AND sis_data.edo_enrollments.sis_section_id IN ({utils.in_op(s.section_id for s in course.sections)})
                 AND sis_data.edo_enrollments.sis_enrollment_status = 'E'
                 AND sis_data.edo_enrollments.grade != 'W'"""
    app.logger.info(sql)
    results = data_loch.safe_execute_rds(sql)
    results_to_enrollments(course, results)


def results_to_enrollments(course, results):
    enrollments = []
    for r in results:
        student = Person({
            'uid': r['uid'],
            'email': r['email_address'],
            'first_name': r['first_name'],
            'full_name': f"{r['first_name']} {r['last_name']}",
            'last_name': r['last_name'],
            'sid': r['sid'],
        })
        enrollments.append(SectionEnrollment({
            'student': student,
            'grade': r['grade'],
            'grading_basis': r['grading_basis'],
            'section_id': str(r['sis_section_id']),
            'status': r['status'],
        }))
    for section in course.sections:
        section.enrollments = []
        for enroll in enrollments:
            if enroll.section_id == str(section.section_id):
                section.enrollments.append(enroll)


#   Test users


def get_users_of_affiliations(affiliations, count=None):
    limit_clause = f'LIMIT {str(count)}' if count else ''
    if affiliations == 'STUDENT-TYPE-REGISTERED':
        sql = f"""SELECT sis_data.edo_basic_attributes.ldap_uid AS uid,
                         sis_data.edo_basic_attributes.sid,
                         sis_data.edo_basic_attributes.first_name,
                         sis_data.edo_basic_attributes.last_name,
                         sis_data.edo_basic_attributes.email_address AS email
                    FROM sis_data.edo_basic_attributes
                    JOIN student.student_profile_index
                      ON sis_data.edo_basic_attributes.ldap_uid = student.student_profile_index.uid
                   WHERE sis_data.edo_basic_attributes.affiliations = '{affiliations}'
                     AND sis_data.edo_basic_attributes.email_address IS NOT NULL
                     AND student.student_profile_index.level NOT IN ('5', '6', '7', '8', 'GR', 'MAS', 'P1', 'P2', 'P3', 'P4')
                ORDER BY sis_data.edo_basic_attributes.ldap_uid DESC
                 {limit_clause}"""

    else:
        sql = f"""SELECT ldap_uid AS uid,
                         sid,
                         first_name,
                         last_name,
                         email_address AS email
                    FROM sis_data.edo_basic_attributes
                   WHERE affiliations = '{affiliations}'
                     AND email_address IS NOT NULL
                ORDER BY ldap_uid DESC
                 {limit_clause}"""
    app.logger.info(sql)
    results = data_loch.safe_execute_rds(sql)
    users = []
    for r in results:
        users.append(Person({
            'uid': r['uid'],
            'email': r['email'],
            'first_name': r['first_name'],
            'last_name': r['last_name'],
            'sid': r['sid'],
        }))
    return users


def get_project_grad_student():
    sql = """SELECT student.student_profile_index.sid,
                    student.student_profile_index.uid,
                    student.student_profile_index.first_name,
                    student.student_profile_index.last_name,
                    student.student_profile_index.email_address AS email
               FROM student.student_profile_index
               JOIN sis_data.edo_basic_attributes
                 ON sis_data.edo_basic_attributes.ldap_uid = student.student_profile_index.uid
              WHERE student.student_profile_index.level IN ('5', '6', '7', '8', 'GR', 'MAS', 'P1', 'P2', 'P3', 'P4')
                AND sis_data.edo_basic_attributes.affiliations = 'STUDENT-TYPE-REGISTERED'"""
    app.logger.info(sql)
    results = data_loch.safe_execute_rds(sql)
    grads = []
    for r in results:
        grads.append(Person({
            'uid': r['uid'],
            'email': r['email'],
            'first_name': r['first_name'],
            'last_name': r['last_name'],
            'role': 'TA',
            'sid': r['sid'],
        }))
    shuffle(grads)
    return grads[0]


#   Mailing lists


def drop_existing_mailing_lists():
    sql = 'DELETE FROM canvas_site_mailing_lists'
    app.logger.info(sql)
    db.session.execute(text(sql))
    std_commit(allow_test_environment=True)


def set_mailing_list_member_email(member, email_address):
    sql = f"""UPDATE canvas_site_mailing_list_members
                 SET email_address = '{email_address}'
               WHERE CONCAT(first_name, ' ', last_name) = '{member.full_name}'
                 AND deleted_at IS NULL"""
    app.logger.info(sql)
    db.session.execute(text(sql))
    std_commit(allow_test_environment=True)


def get_mailing_list_member_email(member):
    sql = f"""SELECT email_address
                FROM canvas_site_mailing_list_members
               WHERE CONCAT(first_name, ' ', last_name) = '{member.full_name}'
                 AND deleted_at IS NULL"""
    app.logger.info(sql)
    result = db.session.execute(text(sql)).first()
    std_commit(allow_test_environment=True)
    return result[0]
