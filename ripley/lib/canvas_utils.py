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
    if not sis_section_id:
        return None
    m = re.fullmatch(r'^(SEC:)?(?P<term_year>\d{4})-(?P<term_code>[A-D])-(?P<section_id>\d+)$', sis_section_id)
    return (m['section_id'], BerkeleyTerm(m['term_year'], m['term_code'])) if m else None


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
