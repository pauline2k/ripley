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


def get_grade_distribution_with_demographics(term_id, section_ids, instructor_uid):  # noqa
    gpa_distribution = {}
    gpa_totals = {}
    grade_distribution = {
        'count': 0,
    }
    student_grades = get_grades_with_demographics(term_id, section_ids, instructor_uid)
    if len(student_grades) < int(app.config['NEWT_MINIMUM_CLASS_SIZE']):
        return False, False

    for row in student_grades:
        if row['term_id'] not in gpa_distribution:
            gpa_distribution[row['term_id']] = deepcopy(EMPTY_DEMOGRAPHIC_DISTRIBUTION)
            gpa_totals[row['term_id']] = deepcopy(EMPTY_DEMOGRAPHIC_DISTRIBUTION)
        gpa_distribution[row['term_id']]['count'] += 1
        gpa_distribution[row['term_id']]['totalGpa'] += row['gpa']
        gpa_distribution[row['term_id']]['courseName'] = row['sis_course_name']

        def _count_boolean_value(column, distribution_key):
            if row[column]:
                gpa_distribution[row['term_id']][distribution_key]['true'] += row['gpa']
                gpa_totals[row['term_id']][distribution_key]['true'] += 1
            else:
                gpa_distribution[row['term_id']][distribution_key]['false'] += row['gpa']
                gpa_totals[row['term_id']][distribution_key]['false'] += 1

        _count_boolean_value('transfer', 'transferStatus')
        _count_boolean_value('minority', 'underrepresentedMinorityStatus')
        _count_boolean_value('visa_type', 'internationalStatus')

        def _count_string_value(value, distribution_key):
            value = str(value) if value else 'none'
            if value not in gpa_distribution[row['term_id']][distribution_key]:
                gpa_distribution[row['term_id']][distribution_key][value] = 0
            if value not in gpa_totals[row['term_id']][distribution_key]:
                gpa_totals[row['term_id']][distribution_key][value] = 0
            gpa_distribution[row['term_id']][distribution_key][value] += row['gpa']
            gpa_totals[row['term_id']][distribution_key][value] += 1

        _count_string_value(_simplify_gender(row['gender']), 'genders')

        if row['grade'] not in grade_distribution:
            grade_distribution[row['grade']] = {'count': 0}
        grade_distribution[row['grade']]['count'] += 1
        grade_distribution['count'] += 1

    sorted_grade_distribution = []
    for grade in sorted(grade_distribution.keys(), key=_grade_ordering_index):
        if grade in GRADE_ORDERING:
            grade_distribution[grade].update({
                'classSize': grade_distribution['count'],
                'grade': grade,
                'percentage': to_percentage(grade_distribution[grade]['count'], grade_distribution['count']),
            })
            sorted_grade_distribution.append(grade_distribution[grade])

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
    return sorted_gpa_distribution, sorted_grade_distribution


def get_grade_distribution_with_prior_enrollments(term_id, course_name, instructor_uid, prior_course_name):
    distribution = {}
    totals = {
        'count': 0,
    }
    for term_id, rows in groupby(
        get_grades_with_enrollments(term_id, course_name, instructor_uid, prior_course_name),
        key=lambda x: x['sis_term_id'],
    ):
        if term_id not in distribution:
            distribution[term_id] = {'count': 0}
        for r in rows:
            if r['grade'] not in distribution[term_id]:
                distribution[term_id][r['grade']] = 0
            distribution[term_id][r['grade']] += 1
            distribution[term_id]['count'] += 1
            if r['grade'] not in totals:
                totals[r['grade']] = 0
            totals[r['grade']] += 1
            totals['count'] += 1
    class_size = sum(totals[grade] for grade in totals.keys() if grade != 'count')

    for term_id, course_distribution in distribution.items():
        total_prior_enroll_count = course_distribution['count']
        sorted_distribution = []
        for grade in sorted(course_distribution.keys(), key=_grade_ordering_index):
            if grade in GRADE_ORDERING:
                grade_prior_enroll_count = course_distribution.get(grade, 0)
                grade_no_prior_enroll_count = totals[grade] - grade_prior_enroll_count
                total_no_prior_enroll_count = class_size - total_prior_enroll_count
                sorted_distribution.append({
                    'grade': grade,
                    'noPriorEnrollCount': grade_no_prior_enroll_count,
                    'noPriorEnrollPercentage': to_percentage(grade_no_prior_enroll_count, total_no_prior_enroll_count),
                    'priorEnrollCount': grade_prior_enroll_count,
                    'priorEnrollPercentage': to_percentage(grade_prior_enroll_count, total_prior_enroll_count),
                    'termName': BerkeleyTerm.from_sis_term_id(term_id).to_english(),
                    'totalCount': totals[grade],
                    'totalPercentage': to_percentage(totals[grade], class_size),
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
