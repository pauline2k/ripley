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

from copy import deepcopy
from itertools import groupby

from flask import current_app as app
from ripley.externals.data_loch import get_grades_with_demographics, get_grades_with_enrollments
from ripley.lib.berkeley_term import BerkeleyTerm
from ripley.lib.util import to_percentage


EMPTY_DEMOGRAPHIC_DISTRIBUTION = {
    'genders': {},
    'internationalStatus': {
        'true': 0,
        'false': 0,
    },
    'transferStatus': {
        'true': 0,
        'false': 0,
    },
    'underrepresentedMinorityStatus': {
        'true': 0,
        'false': 0,
    },
    'count': 0,
    'totalGpa': 0,
}


def get_grade_distributions(term_id, section_ids, instructor_uid):  # noqa
    gpa_distribution = {}
    gpa_totals = {}
    grade_distribution_by_term = {}
    student_grades = get_grades_with_demographics(term_id, section_ids, instructor_uid)
    if len(student_grades) < int(app.config['NEWT_MINIMUM_CLASS_SIZE']):
        return False, False

    for row in student_grades:
        term_id = row['term_id']
        if row['gpa']:
            if term_id not in gpa_distribution:
                gpa_distribution[term_id] = deepcopy(EMPTY_DEMOGRAPHIC_DISTRIBUTION)
                gpa_totals[term_id] = deepcopy(EMPTY_DEMOGRAPHIC_DISTRIBUTION)
            gpa_distribution[term_id]['count'] += 1
            gpa_distribution[term_id]['totalGpa'] += row['gpa']
            gpa_distribution[term_id]['courseName'] = row['sis_course_name']

            def _count_boolean_value(column, distribution_key):
                if row[column]:
                    gpa_distribution[term_id][distribution_key]['true'] += row['gpa']
                    gpa_totals[term_id][distribution_key]['true'] += 1
                else:
                    gpa_distribution[term_id][distribution_key]['false'] += row['gpa']
                    gpa_totals[term_id][distribution_key]['false'] += 1

            _count_boolean_value('transfer', 'transferStatus')
            _count_boolean_value('minority', 'underrepresentedMinorityStatus')
            _count_boolean_value('visa_type', 'internationalStatus')

            def _count_string_value(value, distribution_key):
                value = str(value) if value else 'none'
                if value not in gpa_distribution[term_id][distribution_key]:
                    gpa_distribution[term_id][distribution_key][value] = 0
                if value not in gpa_totals[term_id][distribution_key]:
                    gpa_totals[term_id][distribution_key][value] = 0
                gpa_distribution[term_id][distribution_key][value] += row['gpa']
                gpa_totals[term_id][distribution_key][value] += 1

            _count_string_value(_simplify_gender(row['gender']), 'genders')

        if row['grade']:
            if term_id not in grade_distribution_by_term:
                grade_distribution_by_term[term_id] = {
                    'count': 0,
                }
            if row['grade'] not in grade_distribution_by_term[term_id]:
                grade_distribution_by_term[term_id][row['grade']] = {
                    'count': 0,
                    'courseName': row['sis_course_name'],
                }
            grade_distribution_by_term[term_id][row['grade']]['count'] += 1
            grade_distribution_by_term[term_id]['count'] += 1

    sorted_grade_distribution_by_term = {}
    for term_id, term_distribution in grade_distribution_by_term.items():
        sorted_grade_distribution = []
        for grade in sorted(term_distribution.keys(), key=_grade_ordering_index):
            if grade in GRADE_ORDERING:
                term_distribution[grade].update({
                    'classSize': term_distribution['count'],
                    'grade': grade,
                    'percentage': to_percentage(
                        term_distribution[grade]['count'],
                        term_distribution['count'],
                    ),
                })
                sorted_grade_distribution.append(term_distribution[grade])
        sorted_grade_distribution_by_term[term_id] = sorted_grade_distribution

    sorted_gpa_distribution = []
    for term_id in sorted(gpa_distribution.keys()):
        for distribution_key, values in gpa_distribution[term_id].items():
            if distribution_key in ['count', 'courseName', 'totalGpa']:
                continue
            for distribution_value, total_gpa in values.items():
                student_count = gpa_totals[term_id][distribution_key][distribution_value]
                gpa_distribution[term_id][distribution_key][distribution_value] = {
                    'count': student_count,
                    'averageGpa': (total_gpa / student_count) if student_count > 0 else 0,
                }
        term_student_count = gpa_distribution[term_id]['count']
        term_total_gpa = gpa_distribution[term_id].pop('totalGpa', 0)
        sorted_gpa_distribution.append({
            'averageGpa': (term_total_gpa / term_student_count) if term_student_count > 0 else 0,
            **gpa_distribution[term_id],
            'termId': term_id,
            'termName': BerkeleyTerm.from_sis_term_id(term_id).to_english(),
        })
    return sorted_gpa_distribution, sorted_grade_distribution_by_term


def get_grade_distribution_with_prior_enrollments(term_id, course_name, instructor_uid, prior_course_name):
    distribution = {}
    for term_id, rows in groupby(
        get_grades_with_enrollments(term_id, course_name, instructor_uid, prior_course_name),
        key=lambda x: x['sis_term_id'],
    ):
        if term_id not in distribution:
            distribution[term_id] = {
                'count': 0,
                'total': 0,
            }
        for r in rows:
            if r['grade'] not in distribution[term_id]:
                distribution[term_id][r['grade']] = {
                    'count': 0,
                    'total': 0,
                }
            distribution[term_id][r['grade']]['count'] += r['has_prior_enrollment']
            distribution[term_id][r['grade']]['total'] += 1
            distribution[term_id]['count'] += r['has_prior_enrollment']
            distribution[term_id]['total'] += 1

    for term_id, term_distribution in distribution.items():
        total_prior_enroll_count = term_distribution['count']
        total_no_prior_enroll_count = term_distribution['total'] - total_prior_enroll_count
        sorted_distribution = []
        for grade in sorted(term_distribution.keys(), key=_grade_ordering_index):
            if grade in GRADE_ORDERING:
                grade_values = term_distribution.get(grade, {})
                grade_prior_enroll_count = grade_values.get('count', 0)
                total_grade_count = grade_values.get('total', 0)
                grade_no_prior_enroll_count = total_grade_count - grade_prior_enroll_count
                sorted_distribution.append({
                    'classSize': term_distribution['total'],
                    'courseName': prior_course_name,
                    'grade': grade,
                    'noPriorEnrollCount': grade_no_prior_enroll_count,
                    'noPriorEnrollPercentage': to_percentage(grade_no_prior_enroll_count, total_no_prior_enroll_count),
                    'priorEnrollCount': grade_prior_enroll_count,
                    'priorEnrollPercentage': to_percentage(grade_prior_enroll_count, total_prior_enroll_count),
                    'termName': BerkeleyTerm.from_sis_term_id(term_id).to_english(),
                    'totalCount': total_grade_count,
                    'totalPercentage': to_percentage(total_grade_count, term_distribution['total']),
                })
        distribution[term_id] = sorted_distribution
    return distribution


GRADE_ORDERING = ('A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F', 'P', 'NP', 'I')


def _grade_ordering_index(grade):
    try:
        return GRADE_ORDERING.index(grade)
    except ValueError:
        return len(GRADE_ORDERING)


def _simplify_gender(gender):
    if gender == 'Female':
        return 'female'
    elif gender == 'Male':
        return 'male'
    else:
        return 'other'
