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

from contextlib import contextmanager
from datetime import datetime

from flask import current_app as app
import psycopg2
import psycopg2.extras
from psycopg2.pool import ThreadedConnectionPool

COURSE_NAME_REGEX = r'([A-Z]+)\s([A-Z]?)(\d+)([A-Z]?)([A-Z]?)'
SECTION_COLUMNS = f"""
    sis_term_id AS term_id,
    cs_course_id AS course_id,
    sis_course_name AS course_name,
    sis_course_title AS course_title,
    sis_section_id AS section_id,
    is_primary,
    sis_instruction_format AS instruction_format,
    sis_section_num AS section_number,
    instruction_mode,
    session_code,
    meeting_location,
    meeting_days,
    meeting_start_time,
    meeting_end_time,
    meeting_start_date,
    meeting_end_date,
    regexp_matches(sis_course_name, '{COURSE_NAME_REGEX}') AS sort_key"""

connection_pool = None


def safe_execute_rds(string, **kwargs):
    global connection_pool
    if connection_pool is None:
        connection_pool = ThreadedConnectionPool(1, app.config['DATA_LOCH_MAX_CONNECTIONS'], app.config['DATA_LOCH_RDS_URI'])
    with cursor_from_pool() as cursor:
        return _safe_execute(string, cursor, **kwargs)


@contextmanager
def cursor_from_pool():
    try:
        connection = connection_pool.getconn()
        yield connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    finally:
        connection_pool.putconn(connection)


def get_all_active_users():
    # Beware CLC-7157 (the occasional active user with an 'A' person type).
    sql = """SELECT * FROM sis_data.basic_attributes
        WHERE (affiliations LIKE '%-TYPE-%' AND affiliations NOT LIKE '%TYPE-SPA%')
        AND (person_type != 'A' OR affiliations LIKE '%-TYPE-REGISTERED%')"""
    return safe_execute_rds(sql)


def get_current_term_index():
    rows = safe_execute_rds('SELECT * FROM terms.current_term_index')
    return None if not rows or (len(rows) == 0) else rows[0]


def get_instructing_sections(uid, term_ids):
    params = {
        'instructor_uid': uid,
        'term_ids': term_ids,
    }
    sql = f"""SELECT {SECTION_COLUMNS}
        FROM sis_data.sis_sections
        WHERE instructor_uid = %(instructor_uid)s
        AND sis_term_id = ANY(%(term_ids)s)
        ORDER BY term_id DESC, sis_course_name, is_primary DESC, sis_instruction_format, sis_section_num"""
    return safe_execute_rds(sql, **params)


def get_sections(term_id, section_ids):
    params = {
        'section_ids': section_ids,
        'term_id': term_id,
    }
    sql = f"""SELECT {SECTION_COLUMNS}
        FROM sis_data.sis_sections
        WHERE sis_section_id = ANY(%(section_ids)s)
        AND sis_term_id = %(term_id)s
        ORDER BY sis_section_id"""
    return safe_execute_rds(sql, **params)


def get_section_enrollments(term_id, section_ids):
    params = {
        'term_id': term_id,
        'section_ids': section_ids,
    }
    sql = """SELECT se.sis_section_id AS section_id, se.ldap_uid, ba.sid, ba.first_name, ba.last_name,
            se.sis_enrollment_status, ba.email_address
        FROM sis_data.sis_enrollments se
        JOIN sis_data.basic_attributes ba on ba.ldap_uid = se.ldap_uid
        WHERE se.sis_section_id = ANY(%(section_ids)s)
        AND se.sis_term_id = %(term_id)s
        ORDER BY se.sis_section_id, ba.last_name, ba.first_name, se.ldap_uid"""
    return safe_execute_rds(sql, **params)


def get_undergraduate_term(term_id):
    sql = f"""SELECT * FROM terms.term_definitions
              WHERE term_id = '{term_id}'
           """
    return safe_execute_rds(sql)


def get_users(uids):
    uids_sql_fragment = "'" + "', '".join(uids) + "'"
    sql = f"""
        SELECT * FROM sis_data.basic_attributes
        WHERE
            (affiliations LIKE '%-TYPE-%' AND affiliations NOT LIKE '%TYPE-SPA%')
            AND (person_type != 'A' OR affiliations LIKE '%-TYPE-REGISTERED%')
            AND ldap_uid IN ({uids_sql_fragment})
    """
    return safe_execute_rds(sql)


def _safe_execute(sql, cursor, **kwargs):
    try:
        ts = datetime.now().timestamp()
        cursor.execute(sql, (kwargs or None))
        query_time = datetime.now().timestamp() - ts
    except psycopg2.Error as e:
        app.logger.error(f'SQL {sql} threw {e}')
        return None
    rows = [dict(r) for r in cursor.fetchall()]
    app.logger.debug(f'Query returned {len(rows)} rows in {query_time} seconds:\n{sql}\n{kwargs}')
    return rows
