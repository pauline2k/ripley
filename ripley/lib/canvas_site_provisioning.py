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
from operator import itemgetter

from flask import current_app as app
from ripley.externals.data_loch import get_edo_enrollment_updates, get_edo_instructor_updates, get_section_enrollments, \
    get_section_instructors, get_sections, get_users
from ripley.lib.berkeley_term import BerkeleyTerm
from ripley.lib.calnet_utils import get_calnet_attributes_for_uids
from ripley.lib.canvas_utils import csv_formatted_course_role, csv_row_for_campus_user, parse_canvas_sis_section_id, \
    sis_enrollment_status_to_canvas_course_role
from ripley.models.canvas_synchronization import CanvasSynchronization


def get_canvas_csv_row(uid):
    user_results = get_basic_attributes([uid])
    if len(user_results):
        return csv_row_for_campus_user(next(iter(user_results.values())))
    else:
        return {}


def get_basic_attributes(uids=None):
    # First, call out the CalNet snapshot in the data loch.
    users_by_uid = {}
    remaining_uids = set(uids) if uids else None
    for r in get_users(uids):
        if remaining_uids:
            remaining_uids.discard(r['ldap_uid'])
        if (
            r['person_type'] != 'A'
            or 'STUDENT-TYPE-REGISTERED' in r['affiliations']
            or 'STUDENT-TYPE-NOT REGISTERED' in r['affiliations']
            or 'EMPLOYEE-TYPE' in r['affiliations']
            or 'GUEST-TYPE' in r['affiliations']
        ):
            users_by_uid[r['ldap_uid']] = r
    # If we've been given a specific set of UIDs to look for, then we can do a follow-up-call to LDAP for anyone the
    # snapshot didn't capture.
    if remaining_uids:
        missing_uids = set(u for u in remaining_uids if u not in users_by_uid.keys())
        if missing_uids:
            ldap_users_by_uid = {u['ldap_uid']: u for u in get_calnet_attributes_for_uids(app, missing_uids)}
            users_by_uid.update(ldap_users_by_uid)
    return users_by_uid


def initialize_recent_updates(sis_term_ids, uids_for_updates):
    def _collect_enrollment_updates(updates, status_column):
        collector = {}
        for term_id, term_rows in groupby(updates, key=itemgetter('term_id')):
            canvas_term_id = BerkeleyTerm.from_sis_term_id(term_id).to_canvas_sis_term_id()
            collector[canvas_term_id] = {}
            for section_id, section_rows in groupby(term_rows, key=itemgetter('section_id')):
                collector[canvas_term_id][section_id] = []

                def _get_uid(row):
                    if 'ldap_uid' in row:
                        return row['ldap_uid']
                    elif 'instructor_uid' in row:
                        return row['instructor_uid']

                for uid, uid_rows in groupby(section_rows, key=_get_uid):
                    if uid:
                        uids_for_updates.add(uid)
                        collector[canvas_term_id][section_id].append(list(uid_rows)[0])
        return collector

    instructor_results = get_edo_instructor_updates(CanvasSynchronization.get_last_instructor_sync())
    instructor_updates = _collect_enrollment_updates(instructor_results, 'role_code')
    enrollment_results = get_edo_enrollment_updates(CanvasSynchronization.get_last_enrollment_sync())
    enrollment_updates = _collect_enrollment_updates(enrollment_results, 'sis_enrollment_status')
    return instructor_updates, enrollment_updates


def process_course_enrollments(
    sis_term_id,
    sis_course_id,
    sis_section_ids,
    existing_term_enrollments,
    instructor_updates,
    enrollment_updates,
    sis_user_id_changes,
    csv_set,
    known_users,
    is_incremental,
):
    app.logger.debug(f'Refreshing course {sis_course_id}')
    primary_sections = _get_primary_sections(sis_term_id, sis_section_ids)

    for sis_section_id in sis_section_ids:
        section_id, berkeley_term = parse_canvas_sis_section_id(sis_section_id)
        section_instructor_updates = instructor_updates.get(sis_term_id, {}).get(section_id, [])
        section_enrollment_updates = enrollment_updates.get(sis_term_id, {}).get(section_id, [])
        process_section_enrollments(sis_term_id, sis_course_id, sis_section_id, existing_term_enrollments, section_instructor_updates,
                                    section_enrollment_updates, sis_user_id_changes, csv_set, primary_sections, known_users, is_incremental)


def process_section_enrollments(
    sis_term_id,
    sis_course_id,
    sis_section_id,
    existing_term_enrollments,
    section_instructor_updates,
    section_enrollment_updates,
    sis_user_id_changes,
    csv_set,
    primary_sections,
    known_users,
    is_incremental,
):
    app.logger.debug(f'Refreshing section: {sis_section_id}')

    existing_section_enrollments = {}
    for ldap_uid, rows in groupby(
        sorted(existing_term_enrollments.get(sis_section_id, []), key=itemgetter('sis_login_id')),
        key=itemgetter('sis_login_id'),
    ):
        if (
            not is_incremental
            or ldap_uid in [r['instructor_uid'] for r in section_instructor_updates]
            or ldap_uid in [r['ldap_uid'] for r in section_enrollment_updates]
        ):
            existing_section_enrollments[ldap_uid] = list(rows)
    process_student_enrollments(sis_term_id, sis_course_id, sis_section_id, section_enrollment_updates, csv_set, existing_section_enrollments,
                                known_users, is_incremental)
    process_instructor_enrollments(sis_term_id, sis_course_id, sis_section_id, primary_sections, section_instructor_updates, csv_set,
                                   existing_section_enrollments, known_users, is_incremental)
    # Remove existing enrollments not found in SIS
    for ldap_uid, enrollment_rows in existing_section_enrollments.items():
        process_missing_enrollments(sis_term_id, sis_course_id, sis_section_id, ldap_uid, sis_user_id_changes, csv_set, enrollment_rows)


def process_student_enrollments(
    sis_term_id,
    sis_course_id,
    sis_section_id,
    section_enrollment_updates,
    csv_set,
    existing_section_enrollments,
    known_users,
    is_incremental,
):
    section_id, berkeley_term = parse_canvas_sis_section_id(sis_section_id)
    if is_incremental:
        enrollment_rows = section_enrollment_updates
    else:
        enrollment_rows = get_section_enrollments(berkeley_term.to_sis_term_id(), [section_id], include_dropped=False)
    app.logger.debug(f'{len(enrollment_rows)} student enrollments found for section {sis_section_id}')
    for enrollment_row in enrollment_rows:
        course_role = sis_enrollment_status_to_canvas_course_role(enrollment_row['sis_enrollment_status'])
        if course_role and enrollment_row['ldap_uid']:
            process_section_enrollment(sis_term_id, sis_course_id, sis_section_id, enrollment_row['ldap_uid'], course_role, csv_set,
                                       existing_section_enrollments, known_users)


def process_instructor_enrollments(
    sis_term_id,
    sis_course_id,
    sis_section_id,
    primary_sections,
    section_instructor_updates,
    csv_set,
    existing_section_enrollments,
    known_users,
    is_incremental,
):
    section_id, berkeley_term = parse_canvas_sis_section_id(sis_section_id)
    if is_incremental:
        instructor_rows = section_instructor_updates
    else:
        instructor_rows = get_section_instructors(berkeley_term.to_sis_term_id(), [section_id])
    app.logger.debug(f'{len(instructor_rows)} instructor enrollments found for section {sis_section_id}')
    for instructor_row in instructor_rows:
        course_role = _determine_instructor_role(sis_section_id, primary_sections, instructor_row['instructor_role_code'])
        if course_role and instructor_row['instructor_uid']:
            process_section_enrollment(sis_term_id, sis_course_id, sis_section_id, instructor_row['instructor_uid'], course_role, csv_set,
                                       existing_section_enrollments, known_users)


def process_section_enrollment(sis_term_id, sis_course_id, sis_section_id, ldap_uid, course_role, csv_set, existing_enrollments, known_users):
    enrollment_csv = csv_set.enrollment_terms[sis_term_id]
    existing_user_enrollments = existing_enrollments.get(str(ldap_uid), None)
    if existing_user_enrollments:
        app.logger.debug(f'Found {len(existing_user_enrollments)} existing enrollments for UID {ldap_uid} in section {sis_section_id}')
        # If the user already has the same role, remove the old enrollment from the cleanup list.
        matching_enrollment = next((e for e in existing_user_enrollments if e['role'] == course_role), None)
        if matching_enrollment:
            app.logger.debug(f'Found matching enrollment for UID {ldap_uid}, section {sis_section_id}, role {course_role}')
            existing_user_enrollments.remove(matching_enrollment)
            # If the user's membership was due to an earlier SIS import, no further action is needed.
            if matching_enrollment['sis_import_id']:
                return
            # But if the user was manually added in this role, fall through and give Canvas a chance to convert the
            # membership stickiness from manual to SIS import.
    elif 'users' in csv_set._fields:
        _add_user_if_new(ldap_uid, known_users, csv_set.users)

    sis_user_id = known_users.get(str(ldap_uid), None) or get_canvas_csv_row(ldap_uid).get('user_id', None)
    if sis_user_id:
        app.logger.info(f'Adding UID {ldap_uid} to section {sis_section_id} with role {course_role}')
        enrollment_csv.writerow({
            'course_id': sis_course_id,
            'user_id': sis_user_id,
            'role': csv_formatted_course_role(course_role),
            'section_id': sis_section_id,
            'status': 'active',
        })


def process_missing_enrollments(sis_term_id, sis_course_id, sis_section_id, ldap_uid, sis_user_id_changes, csv_set, enrollment_rows):
    enrollment_csv = csv_set.enrollment_terms[sis_term_id]
    for enrollment in enrollment_rows:
        # Only look at enrollments which are active and were due to an SIS import.
        if enrollment['sis_import_id'] and enrollment['enrollment_state'] == 'active':
            app.logger.info(f"""No campus record for Canvas enrollment (course {enrollment['course_id']},
                section {enrollment['canvas_section_id']}, user {ldap_uid}, role {enrollment['role']}""")
            sis_user_id = sis_user_id_changes.get(f'sis_login_id:{ldap_uid}', {}).get('new_id', None) or enrollment['sis_user_id']
            enrollment_csv.writerow({
                'course_id': sis_course_id,
                'user_id': sis_user_id,
                'role': csv_formatted_course_role(enrollment['role']),
                'section_id': sis_section_id,
                'status': 'deleted',
            })


def _add_user_if_new(uid, known_users, users_csv):
    if not known_users.get(str(uid), None):
        csv_row = get_canvas_csv_row(uid)
        if csv_row:
            known_users[str(uid)] = csv_row['user_id']
            app.logger.debug(f"Adding new user (uid={uid}, sis id={csv_row['user_id']}")
            users_csv.writerow(csv_row)


def _determine_instructor_role(sis_section_id, primary_sections, role_code):
    campus_section_id = parse_canvas_sis_section_id(sis_section_id)[0]
    if primary_sections:
        if next((s for s in primary_sections if str(s['section_id']) == str(campus_section_id)), None):
            # Teacher permissions for the course site are generally determined by primary section assignment.
            # Administrative Proxy assignments (instructor role "APRX"/"5") are treated as Lead TAs.
            if role_code == 'APRX':
                return 'Lead TA'
            else:
                return 'TeacherEnrollment'
        else:
            # Although SIS marks them as 'instructors', when someone is explicitly assigned to a secondary
            # section, they are generally a GSI, and top-level bCourses Teacher access will be determined by assignment
            # to a primary section.
            return 'TaEnrollment'
    else:
        # However, if there are no primary sections in the course site, the site still needs at least one
        # member with Teacher access.
        return 'TeacherEnrollment'


def _get_primary_sections(sis_term_id, sis_section_ids):
    campus_term = BerkeleyTerm.from_canvas_sis_term_id(sis_term_id)
    if not campus_term:
        app.logger.error(f'Unknown Canvas term {sis_term_id}')
        return []
    campus_section_ids = [parse_canvas_sis_section_id(s)[0] for s in sis_section_ids]
    loch_sections = get_sections(campus_term.to_sis_term_id(), campus_section_ids)
    return [s for s in loch_sections if s['is_primary']]
