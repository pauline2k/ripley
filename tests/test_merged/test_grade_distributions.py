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

from ripley.merged.grade_distributions import get_grade_distribution_with_prior_enrollments, get_grade_distributions
from tests.util import override_config


class TestGradeDistributions:

    def test_get_grade_distributions(self, app):
        with override_config(app, 'GRADE_DISTRIBUTION_MIN_STUDENTS_PER_CATEGORY', 0):
            demographics_distribution, grade_distribution = get_grade_distributions('2228', ['99999'])
            assert demographics_distribution == [
                {
                    'averageGradePoints': 1.1166666666666667,
                    'count': 6,
                    'courseName': 'ASTRON 218',
                    'genders': {
                        'female': {
                            'averageGradePoints': 1.675,
                            'count': 4,
                        },
                        'male': {
                            'averageGradePoints': 0.0,
                            'count': 2,
                        },
                    },
                    'internationalStatus': {
                        'false': {
                            'averageGradePoints': 1.34,
                            'count': 5,
                        },
                        'true': {
                            'averageGradePoints': 0.0,
                            'count': 1,
                        },
                    },
                    'termId': '2225',
                    'termName': 'Summer 2022',
                    'transferStatus': {
                        'false': {
                            'averageGradePoints': 1.1166666666666667,
                            'count': 6,
                        },
                        'true': {
                            'averageGradePoints': 0,
                            'count': 0,
                        },
                    },
                    'underrepresentedMinorityStatus': {
                        'false': {
                            'averageGradePoints': 0.0,
                            'count': 3,
                        },
                        'true': {
                            'averageGradePoints': 2.2333333333333334,
                            'count': 3,
                        },
                    },
                },
                {
                    'averageGradePoints': 3.520879120879121,
                    'count': 91,
                    'courseName': 'ASTRON 218',
                    'genders': {
                        'female': {
                            'averageGradePoints': 3.6426470588235293,
                            'count': 68,
                        },
                        'male': {
                            'averageGradePoints': 3.122727272727273,
                            'count': 22,
                        },
                        'other': {
                            'averageGradePoints': 4.0,
                            'count': 1,
                        },
                    },
                    'internationalStatus': {
                        'false': {
                            'averageGradePoints': 3.52289156626506,
                            'count': 83,
                        },
                        'true': {
                            'averageGradePoints': 3.5,
                            'count': 8,
                        },
                    },
                    'termId': '2228',
                    'termName': 'Fall 2022',
                    'transferStatus': {
                        'false': {
                            'averageGradePoints': 3.559302325581395,
                            'count': 86,
                        },
                        'true': {
                            'averageGradePoints': 2.8600000000000003,
                            'count': 5,
                        },
                    },
                    'underrepresentedMinorityStatus': {
                        'false': {
                            'averageGradePoints': 3.1861111111111113,
                            'count': 36,
                        },
                        'true': {
                            'averageGradePoints': 3.7399999999999998,
                            'count': 55,
                        },
                    },
                },
            ]
            assert grade_distribution == {
                '2225': [
                    {
                        'count': 1,
                        'courseName': 'ASTRON 218',
                        'classSize': 6,
                        'grade': 'A-',
                        'percentage': 16.7,
                    },
                    {
                        'count': 1,
                        'courseName': 'ASTRON 218',
                        'classSize': 6,
                        'grade': 'C',
                        'percentage': 16.7,
                    },
                    {
                        'count': 1,
                        'courseName': 'ASTRON 218',
                        'classSize': 6,
                        'grade': 'D',
                        'percentage': 16.7,
                    },
                    {
                        'count': 3,
                        'courseName': 'ASTRON 218',
                        'classSize': 6,
                        'grade': 'P',
                        'percentage': 50.0,
                    },
                ],
                '2228': [
                    {
                        'classSize': 91,
                        'count': 16,
                        'courseName': 'ASTRON 218',
                        'grade': 'A+',
                        'percentage': 17.6,
                    },
                    {
                        'classSize': 91,
                        'count': 52,
                        'courseName': 'ASTRON 218',
                        'grade': 'A',
                        'percentage': 57.1,
                    },
                    {
                        'classSize': 91,
                        'count': 8,
                        'courseName': 'ASTRON 218',
                        'grade': 'A-',
                        'percentage': 8.8,
                    },
                    {
                        'classSize': 91,
                        'count': 5,
                        'courseName': 'ASTRON 218',
                        'grade': 'B+',
                        'percentage': 5.5,
                    },
                    {
                        'classSize': 91,
                        'count': 1,
                        'courseName': 'ASTRON 218',
                        'grade': 'C+',
                        'percentage': 1.1,
                    },
                    {
                        'classSize': 91,
                        'count': 1,
                        'courseName': 'ASTRON 218',
                        'grade': 'F',
                        'percentage': 1.1,
                    },
                    {
                        'classSize': 91,
                        'count': 8,
                        'courseName': 'ASTRON 218',
                        'grade': 'P',
                        'percentage': 8.8,
                    },
                ],
            }

    def test_get_grade_distributions_minimum_threshold(self, app):
        with override_config(app, 'GRADE_DISTRIBUTION_MIN_STUDENTS_PER_CATEGORY', 1):
            demographics_distribution, grade_distribution = get_grade_distributions('2228', ['99999'])
            assert demographics_distribution == [
                {
                    'averageGradePoints': 1.1166666666666667,
                    'genders': {
                        'female': {
                            'averageGradePoints': 1.675,
                            'count': 4,
                        },
                        'male': {
                            'averageGradePoints': 0.0,
                            'count': 2,
                        },
                    },
                    'internationalStatus': {
                        'true': {
                            'averageGradePoints': 0.0,
                            'count': 1,
                        },
                        'false': {
                            'averageGradePoints': 1.34,
                            'count': 5,
                        },
                    },
                    'transferStatus': {
                        'true': {
                            'averageGradePoints': 0,
                            'count': 0,
                        },
                        'false': {
                            'averageGradePoints': 1.1166666666666667,
                            'count': 6,
                        },
                    },
                    'underrepresentedMinorityStatus': {
                        'true': {
                            'averageGradePoints': 2.2333333333333334,
                            'count': 3,
                        },
                        'false': {
                            'averageGradePoints': 0.0,
                            'count': 3,
                        },
                    },
                    'count': 6,
                    'courseName': 'ASTRON 218',
                    'termId': '2225',
                    'termName': 'Summer 2022',
                },
                {
                    'averageGradePoints': 3.520879120879121,
                    'count': 91,
                    'courseName': 'ASTRON 218',
                    'genders': {
                        'female': {
                            'averageGradePoints': 3.6426470588235293,
                            'count': 68,
                        },
                        'male': {
                            'averageGradePoints': 3.122727272727273,
                            'count': 22,
                        },
                        'other': {
                            'averageGradePoints': 4.0,
                            'count': 1,
                        },
                    },
                    'internationalStatus': {
                        'false': {
                            'averageGradePoints': 3.52289156626506,
                            'count': 83,
                        },
                        'true': {
                            'averageGradePoints': 3.5,
                            'count': 8,
                        },
                    },
                    'termId': '2228',
                    'termName': 'Fall 2022',
                    'transferStatus': {
                        'false': {
                            'averageGradePoints': 3.559302325581395,
                            'count': 86,
                        },
                        'true': {
                            'averageGradePoints': 2.8600000000000003,
                            'count': 5,
                        },
                    },
                    'underrepresentedMinorityStatus': {
                        'false': {
                            'averageGradePoints': 3.1861111111111113,
                            'count': 36,
                        },
                        'true': {
                            'averageGradePoints': 3.7399999999999998,
                            'count': 55,
                        },
                    },
                },
            ]
            assert grade_distribution == {
                '2225': [
                    {
                        'count': 1,
                        'courseName': 'ASTRON 218',
                        'classSize': 6,
                        'grade': 'A-',
                        'percentage': 16.7,
                    },
                    {
                        'count': 1,
                        'courseName': 'ASTRON 218',
                        'classSize': 6,
                        'grade': 'C',
                        'percentage': 16.7,
                    },
                    {
                        'count': 1,
                        'courseName': 'ASTRON 218',
                        'classSize': 6,
                        'grade': 'D',
                        'percentage': 16.7,
                    },
                    {
                        'count': 3,
                        'courseName': 'ASTRON 218',
                        'classSize': 6,
                        'grade': 'P',
                        'percentage': 50.0,
                    },
                ],
                '2228': [
                    {
                        'classSize': 91,
                        'count': 16,
                        'courseName': 'ASTRON 218',
                        'grade': 'A+',
                        'percentage': 17.6,
                    },
                    {
                        'classSize': 91,
                        'count': 52,
                        'courseName': 'ASTRON 218',
                        'grade': 'A',
                        'percentage': 57.1,
                    },
                    {
                        'classSize': 91,
                        'count': 8,
                        'courseName': 'ASTRON 218',
                        'grade': 'A-',
                        'percentage': 8.8,
                    },
                    {
                        'classSize': 91,
                        'count': 5,
                        'courseName': 'ASTRON 218',
                        'grade': 'B+',
                        'percentage': 5.5,
                    },
                    {
                        'classSize': 91,
                        'count': 1,
                        'courseName': 'ASTRON 218',
                        'grade': 'C+',
                        'percentage': 1.1,
                    },
                    {
                        'classSize': 91,
                        'count': 1,
                        'courseName': 'ASTRON 218',
                        'grade': 'F',
                        'percentage': 1.1,
                    },
                    {
                        'classSize': 91,
                        'count': 8,
                        'courseName': 'ASTRON 218',
                        'grade': 'P',
                        'percentage': 8.8,
                    },
                ],
            }

    def test_enrollment_distribution(self, app):
        with override_config(app, 'GRADE_DISTRIBUTION_MIN_STUDENTS_PER_CATEGORY', 1):
            d = get_grade_distribution_with_prior_enrollments(
                term_id='2232',
                course_name='ANTHRO 189',
                prior_course_name='ASTRON 218',
            )
            assert d == {
                '2232': [
                    {
                        'classSize': 7,
                        'courseName': 'ASTRON 218',
                        'grade': 'A+',
                        'noPriorEnrollCount': 0,
                        'noPriorEnrollPercentage': 0.0,
                        'priorEnrollCount': 1,
                        'priorEnrollPercentage': 16.7,
                        'termName': 'Spring 2023',
                        'totalCount': 1,
                        'totalPercentage': 14.3,
                    },
                    {
                        'classSize': 7,
                        'courseName': 'ASTRON 218',
                        'grade': 'A',
                        'noPriorEnrollCount': 1,
                        'noPriorEnrollPercentage': 100.0,
                        'priorEnrollCount': 1,
                        'priorEnrollPercentage': 16.7,
                        'termName': 'Spring 2023',
                        'totalCount': 2,
                        'totalPercentage': 28.6,
                    },
                    {
                        'classSize': 7,
                        'courseName': 'ASTRON 218',
                        'grade': 'A-',
                        'noPriorEnrollCount': 0,
                        'noPriorEnrollPercentage': 0.0,
                        'priorEnrollCount': 1,
                        'priorEnrollPercentage': 16.7,
                        'termName': 'Spring 2023',
                        'totalCount': 1,
                        'totalPercentage': 14.3,
                    },
                    {
                        'classSize': 7,
                        'courseName': 'ASTRON 218',
                        'grade': 'B+',
                        'noPriorEnrollCount': 0,
                        'noPriorEnrollPercentage': 0,
                        'priorEnrollCount': 2,
                        'priorEnrollPercentage': 33.3,
                        'termName': 'Spring 2023',
                        'totalCount': 2,
                        'totalPercentage': 28.6,
                    },
                    {
                        'classSize': 7,
                        'courseName': 'ASTRON 218',
                        'grade': 'B',
                        'noPriorEnrollCount': 0,
                        'noPriorEnrollPercentage': 0.0,
                        'priorEnrollCount': 1,
                        'priorEnrollPercentage': 16.7,
                        'termName': 'Spring 2023',
                        'totalCount': 1,
                        'totalPercentage': 14.3,
                    },
                ],
            }
