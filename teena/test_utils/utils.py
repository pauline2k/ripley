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

import csv
import os
import shutil
import time

from flask import current_app as app
from teena.models.term import Term


# Driver config

def get_browser():
    return app.config['BROWSER']


def get_browser_chrome_binary_path():
    return app.config['BROWSER_BINARY_PATH']


def browser_is_headless():
    return app.config['BROWSER_HEADLESS']


# Timeouts

def get_click_sleep():
    return app.config['CLICK_SLEEP']


def get_short_timeout():
    return app.config['TIMEOUT_SHORT']


def get_medium_timeout():
    return app.config['TIMEOUT_MEDIUM']


def get_long_timeout():
    return app.config['TIMEOUT_LONG']


# Accounts

def ripley_base_url():
    return app.config['BASE_URL']


def ripley_prod_base_url():
    return app.config['BASE_URL_PROD']


def canvas_base_url():
    return app.config['CANVAS_BASE_URL']


def canvas_root_acct():
    return app.config['CANVAS_BERKELEY_ACCOUNT_ID']


def canvas_admin_acct():
    return app.config['CANVAS_ADMIN_TOOLS_ACCOUNT_ID']


def canvas_official_courses_acct():
    return app.config['CANVAS_COURSES_ACCOUNT_ID']


def canvas_qa_acct():
    return app.config['CANVAS_QA_ACCOUNT_ID']


def e_grades_site_ids():
    return app.config['E_GRADES_SITE_IDS']


def e_grades_student_count():
    return app.config['E_GRADES_STUDENT_COUNT']


def grade_distribution_site_ids():
    return app.config['NEWT_SITE_IDS']


def course_template_dept():
    return app.config['COURSE_TEMPLATE_DEPT']


def mailing_list_suffix():
    return '-cc-ets-qa' if '-qa' in ripley_base_url() else '-cc-ets-dev'


# Terms


def current_term():
    return Term({
        'code': app.config['TERM_CODE'],
        'name': app.config['TERM_NAME'],
        'sis_id': app.config['TERM_SIS_ID'],
    })


def term_name_to_hyphenated_code(term_name):
    parts = term_name.split()
    if parts[0] == 'Spring':
        sem = 'B'
    elif parts[0] == 'Summer':
        sem = 'C'
    else:
        sem = 'D'
    return f'{parts[1]}-{sem}'


def term_hyphenated_code_to_name(term_code):
    parts = term_code.split('-')
    if parts[1] == 'B':
        season = 'Spring'
    elif parts[1] == 'C':
        season = 'Summer'
    else:
        season = 'Fall'
    return f'{season} {parts[0]}'


def term_name_to_sis_code(term_name):
    parts = term_name.split()
    year_code = f'{parts[1][0]}{parts[1][2:4]}'
    if parts[0] == 'Spring':
        season_code = '2'
    elif parts[0] == 'Summer':
        season_code = '5'
    else:
        season_code = '8'
    return f'{year_code}{season_code}'


def next_term(this_term):
    term = Term({
        'sis_id': next_term_sis_id(this_term),
        'name': next_term_name(this_term),
    })
    term.code = term_name_to_hyphenated_code(term.name)
    return term


def next_term_sis_id(this_term):
    addend = 3 if int(this_term.sis_id) % 10 in [2, 5] else 4
    return str(int(this_term.sis_id) + addend)


def next_term_name(this_term):
    parts = this_term.name.split()
    if parts[0] == 'Spring':
        return f'Summer {parts[1]}'
    elif parts[0] == 'Summer':
        return f'Fall {parts[1]}'
    else:
        return f'Spring {int(parts[1]) + 1}'


def previous_term(this_term):
    term = Term({
        'sis_id': previous_term_sis_id(this_term),
        'name': previous_term_name(this_term),
    })
    term.code = term_name_to_hyphenated_code(term.name)
    return term


def previous_term_sis_id(this_term):
    this_id = int(this_term.sis_id)
    return str(this_id - (4 if this_id % 10 == 2 else 3))


def previous_term_name(this_term):
    parts = this_term.name.split()
    if parts[0] == 'Spring':
        return f'Fall {int(parts[1]) - 1}'
    elif parts[0] == 'Summer':
        return f'Spring {parts[1]}'
    else:
        return f'Summer {parts[1]}'


def terms_since_code_red():
    term = previous_term(current_term())
    terms = [term]
    while int(term.sis_id) > 2168:
        term = previous_term(term)
        terms.append(term)
    return terms


# Users

def get_admin_uid():
    return app.config['ADMIN_UID']


def get_admin_username():
    return os.getenv('USERNAME')


def get_admin_password():
    return os.getenv('PASSWORD')


def get_oski_uid():
    return app.config['OSKI_UID']


# Test configs and utils

def get_test_identifier():
    return f'QA TEST {int(time.time())}'


def default_download_dir():
    return f'{app.config["BASE_DIR"]}/teena/downloads'


def prepare_download_dir():
    # Make sure a clean download directory exists
    if os.path.isdir(default_download_dir()):
        shutil.rmtree(default_download_dir())
    os.mkdir(default_download_dir())


def is_download_dir_empty():
    return False if os.listdir(default_download_dir()) else True


def assert_equivalence(actual, expected):
    if isinstance(actual, list) and isinstance(expected, list):
        app.logger.info(f'Missing: {[e for e in expected if e not in actual]}')
        app.logger.info(f'Unexpected: {[a for a in actual if a not in expected]}')
    if actual != expected:
        app.logger.info(f'Expecting {expected}, got {actual}')
    assert actual == expected


def assert_actual_includes_expected(actual, expected):
    if expected not in actual:
        app.logger.info(f'Expected {actual} to include {expected}')
    assert expected in actual


def assert_list_items_in_other_list(this_list, other_list):
    for i in this_list:
        app.logger.info(f'Checking presence of {i}')
        assert i in other_list


def assert_list_items_not_in_other_list(this_list, other_list):
    for i in this_list:
        app.logger.info(f'Checking presence of {i}')
        assert i not in other_list


def assert_existence(actual):
    app.logger.info(f'Expecting {actual} not to be null or empty')
    assert actual


def assert_non_existence(actual):
    app.logger.info(f'Expecting {actual} to be null or empty')
    assert not actual


def in_op(arr):
    arr = list(map(lambda i: f"'{i}'", arr))
    return ', '.join(arr)


def create_csv(file_name, rows):
    prepare_download_dir()
    filepath = os.path.join(default_download_dir(), file_name)
    with open(filepath, 'w', newline='') as file:
        csv.writer(file).writerows(rows)
    return file
