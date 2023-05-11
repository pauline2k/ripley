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

import re

from flask import current_app as app
from ripley.lib.berkeley_term import BerkeleyTerm


def parse_canvas_sis_section_id(sis_section_id):
    section_id, berkeley_term = None, None
    if sis_section_id:
        m = re.fullmatch(r'^(SEC:)?(?P<term_year>\d{4})-(?P<term_code>[A-D])-(?P<section_id>\d+).*?$', sis_section_id)
        section_id = m['section_id'] if m else None
        berkeley_term = BerkeleyTerm(m['term_year'], m['term_code']) if m else None
    return section_id, berkeley_term


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


def sis_enrollment_status_to_canvas_course_role(sis_enrollment_status):
    return {
        'E': 'StudentEnrollment',
        'W': 'Waitlist Student',
        'C': 'StudentEnrollment',
    }.get(sis_enrollment_status, None)


def uid_from_canvas_login_id(login_id):
    result = {'uid': None, 'inactive': None}
    match = re.match('^(inactive-)?([0-9]+)$', login_id)
    if match:
        try:
            result = {'uid': str(match.group(2)), 'inactive': bool(match.group(1))}
        except Exception:
            pass
    return result


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
        term = BerkeleyTerm.from_canvas_sis_term_id(canvas_sis_term_id)
        if term:
            api_json = {
                'term_yr': term.year,
                'term_cd': term.season,
                'name': term.to_english(),
            }
    return api_json
