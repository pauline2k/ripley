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
from ripley.lib.util import to_percentage


EMPTY_DISTRIBUTION = {
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
}


def get_grade_distribution_with_demographics(term_id, section_ids, instructor_uid):  # noqa
    distribution = {}
    class_size = 0
    totals = deepcopy(EMPTY_DISTRIBUTION)

    student_grades = get_grades_with_demographics(term_id, section_ids, instructor_uid)
    if len(student_grades) < int(app.config['NEWT_MINIMUM_CLASS_SIZE']):
        return False

    for row in student_grades:
        if not row['grade']:
            continue
        if row['grade'] not in distribution:
            distribution[row['grade']] = deepcopy(EMPTY_DISTRIBUTION)
        distribution[row['grade']]['count'] += 1
        class_size += 1

        def _count_boolean_value(column, distribution_key):
            if row[column]:
                distribution[row['grade']][distribution_key]['true'] += 1
                totals[distribution_key]['true'] += 1
            else:
                distribution[row['grade']][distribution_key]['false'] += 1
                totals[distribution_key]['false'] += 1

        _count_boolean_value('transfer', 'transferStatus')
        _count_boolean_value('minority', 'underrepresentedMinorityStatus')
        _count_boolean_value('visa_type', 'internationalStatus')

        def _count_string_value(value, distribution_key):
            value = str(value) if value else 'none'
            if value not in distribution[row['grade']][distribution_key]:
                distribution[row['grade']][distribution_key][value] = 0
            if value not in totals[distribution_key]:
                totals[distribution_key][value] = 0
                totals[distribution_key][value] = 0
            distribution[row['grade']][distribution_key][value] += 1
            totals[distribution_key][value] += 1

        _count_string_value(_simplify_gender(row['gender']), 'genders')

    sorted_distribution = []
    for grade in sorted(distribution.keys(), key=_grade_ordering_index):
        for distribution_key, values in distribution[grade].items():
            if distribution_key == 'count':
                continue
            for distribution_value, count in values.items():
                distribution[grade][distribution_key][distribution_value] = {
                    'count': count,
                    'percentage': to_percentage(count, totals[distribution_key][distribution_value]),
                }
        distribution[grade].update({'classSize': class_size})
        distribution[grade].update({'grade': grade})
        distribution[grade].update({'percentage': to_percentage(distribution[grade]['count'], class_size)})
        sorted_distribution.append(distribution[grade])

    return sorted_distribution


def get_grade_distribution_with_enrollments(term_id, section_ids, grades):
    grades_by_course_name = {}
    for course_name, rows in groupby(get_grades_with_enrollments(term_id, section_ids), key=lambda x: x['sis_course_name']):
        grades_by_course_name[course_name] = [r for r in rows if r['grade']]

    courses_by_popularity = sorted(grades_by_course_name.items(), key=lambda r: len(r[1]), reverse=True)
    courses_by_popularity = courses_by_popularity[0:app.config['GRADE_DISTRIBUTION_MAX_DISTINCT_COURSES']]

    distribution = {}
    for course_name, course_rows in courses_by_popularity:
        distribution[course_name] = {'count': 0}
        for r in course_rows:
            if r['grade'] not in distribution[course_name]:
                distribution[course_name][r['grade']] = 1
            else:
                distribution[course_name][r['grade']] += 1
            distribution[course_name]['count'] += 1

    for course_name, course_distribution in distribution.items():
        total_prior_enroll_count = course_distribution['count']
        sorted_distribution = []
        for grade in grades.keys():
            grade_prior_enroll_count = course_distribution.get(grade, 0)
            grade_no_prior_enroll_count = grades[grade]['count'] - grade_prior_enroll_count
            total_no_prior_enroll_count = grades[grade]['classSize'] - total_prior_enroll_count
            sorted_distribution.append({
                'grade': grade,
                'noPriorEnrollCount': grade_no_prior_enroll_count,
                'noPriorEnrollPercentage': to_percentage(grade_no_prior_enroll_count, total_no_prior_enroll_count),
                'priorEnrollCount': grade_prior_enroll_count,
                'priorEnrollPercentage': to_percentage(grade_prior_enroll_count, total_prior_enroll_count),
                'totalCount': grades[grade]['count'],
                'totalPercentage': grades[grade]['percentage'],
            })
        distribution[course_name] = sorted_distribution

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
