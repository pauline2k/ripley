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

import csv
import io
from time import sleep

from canvasapi import Canvas
from canvasapi.account import Account
from canvasapi.course import Course
from flask import current_app as app


# By default, we allow up to an hour for Canvas to rouse itself.
MAX_REPORT_RETRIEVAL_ATTEMPTS = 180


def ping_canvas():
    return get_account(app.config['CANVAS_BERKELEY_ACCOUNT_ID']) is not None


def get_account(account_id, api_call=True):
    c = _get_canvas()
    if api_call is False:
        return Account(c._Canvas__requester, {'id': account_id})
    else:
        account = None
        try:
            account = c.get_account(account_id)
        except Exception as e:
            app.logger.error(f'Failed to retrieve Canvas account (id={account_id})')
            app.logger.exception(e)
        return account


def get_course(course_id, api_call=True):
    c = _get_canvas()
    if api_call is False:
        return Course(c._Canvas__requester, {'id': course_id})
    else:
        course = None
        try:
            course = c.get_course(course_id)
        except Exception as e:
            app.logger.error(f'Failed to retrieve Canvas course (id={course_id})')
            app.logger.exception(e)
        return course


def get_csv_report(report_type, download_path=None, term_id=None):
    canvas = _get_canvas()
    account = canvas.get_account(app.config['CANVAS_BERKELEY_ACCOUNT_ID'])
    parameters = {report_type: 1}
    if term_id:
        parameters['enrollment_term'] = f'sis_term_id:{term_id}'

    r = account.create_report('provisioning_csv', parameters=parameters)
    if not r:
        app.logger.error(f'Failed to request CSV {report_type} report')
        return None

    app.logger.info(f'Requested CSV {report_type} report: {r}')
    attempts = 0

    while attempts < MAX_REPORT_RETRIEVAL_ATTEMPTS:
        report = account.get_report('provisioning_csv', r.id)

        if report.status == 'complete':
            file = canvas.get_file(report.attachment['id'])
            if not download_path:
                return csv.DictReader(io.StringIO(file.get_contents()))
            else:
                file.download(download_path)
                return True

        elif report.status == 'error':
            app.logger.error(f'Failed to generate CSV {report_type} report: {report}')
            return None

        else:
            attempts += 1
            sleep(5)

    app.logger.error(f'Failed to retrieve CSV {report_type} report after {MAX_REPORT_RETRIEVAL_ATTEMPTS} attempts')


def get_external_tools(obj_type, obj_id=None):
    if obj_type == 'account':
        obj = get_account(obj_id, api_call=False)
    elif obj_type == 'course':
        obj = get_course(obj_id, api_call=False)
    else:
        raise ValueError

    tools = []
    try:
        tools = obj.get_external_tools()
    except Exception as e:
        app.logger.error(f'Failed to retrieve Canvas external tools ({obj_type}_id={obj_id})')
        app.logger.exception(e)
    return tools


def get_tabs(course_id):
    tabs = []
    try:
        tabs = get_course(course_id, api_call=False).get_tabs()
    except Exception as e:
        app.logger.error(f'Failed to retrieve Canvas tabs (course_id={course_id})')
        app.logger.exception(e)
    return tabs


def get_teachers(course_id):
    teachers = []
    try:
        teachers = get_course(course_id, api_call=False).get_users(enrollment_type='teacher', include=('email', 'enrollments'))
    except Exception as e:
        app.logger.error(f'Failed to retrieve Canvas teachers (course_id={course_id})')
        app.logger.exception(e)
    return teachers


def _get_canvas():
    return Canvas(
        base_url=app.config['CANVAS_API_URL'],
        access_token=app.config['CANVAS_ACCESS_TOKEN'],
    )
