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

from decimal import Decimal

import pytest
from ripley.merged.grade_distributions import get_grade_distribution_with_demographics, \
    get_grade_distribution_with_enrollments


class TestGradeDistributions:

    def test_demographic_distribution(self):
        gpa_demographics_distribution, grade_distribution = get_grade_distribution_with_demographics('2228', ['99999'], '30000')
        print(gpa_demographics_distribution)
        assert gpa_demographics_distribution == [
            {
                'averageGpa': Decimal('3.3705'),
                'count': 6,
                'genders': {
                    'female': {
                        'averageGpa': Decimal('3.6315'),
                        'count': 4,
                    },
                    'male': {
                        'averageGpa': Decimal('2.8485'),
                        'count': 2,
                    },
                },
                'internationalStatus': {
                    'false': {
                        'averageGpa': Decimal('3.683'),
                        'count': 5,
                    },
                    'true': {
                        'averageGpa': Decimal('1.808'),
                        'count': 1,
                    },
                },
                'termId': '2225',
                'termName': 'Summer 2022',
                'transferStatus': {
                    'false': {
                        'averageGpa': Decimal('3.3705'),
                        'count': 6,
                    },
                    'true': {
                        'averageGpa': 0,
                        'count': 0,
                    },
                },
                'underrepresentedMinorityStatus': {
                    'false': {
                        'averageGpa': Decimal('3.207'),
                        'count': 3,
                    },
                    'true': {
                        'averageGpa': Decimal('3.534'),
                        'count': 3,
                    },
                },
            },
            {
                'averageGpa': Decimal('3.528692307692307692307692308'),
                'count': 91,
                'genders': {
                    'female': {
                        'averageGpa': Decimal('3.541294117647058823529411765'),
                        'count': 68,
                    },
                    'male': {
                        'averageGpa': Decimal('3.470090909090909090909090909'),
                        'count': 22,
                    },
                    'other': {
                        'averageGpa': Decimal('3.961'),
                        'count': 1,
                    },
                },
                'internationalStatus': {
                    'false': {
                        'averageGpa': Decimal('3.543180722891566265060240964'),
                        'count': 83,
                    },
                    'true': {
                        'averageGpa': Decimal('3.378375'),
                        'count': 8,
                    },
                },
                'termId': '2228',
                'termName': 'Fall 2022',
                'transferStatus': {
                    'false': {
                        'averageGpa': Decimal('3.533546511627906976744186047'),
                        'count': 86,
                    },
                    'true': {
                        'averageGpa': Decimal('3.4452'),
                        'count': 5,
                    },
                },
                'underrepresentedMinorityStatus': {
                    'false': {
                        'averageGpa': Decimal('3.724861111111111111111111111'),
                        'count': 36,
                    },
                    'true': {
                        'averageGpa': Decimal('3.400290909090909090909090909'),
                        'count': 55,
                    },
                },
            },
        ]
        assert grade_distribution == [
            {
                'classSize': 97,
                'count': 16,
                'grade': 'A+',
                'percentage': 16.5,
            },
            {
                'classSize': 97,
                'count': 52,
                'grade': 'A',
                'percentage': 53.6,
            },
            {
                'classSize': 97,
                'count': 8,
                'grade': 'A-',
                'percentage': 8.2,
            },
            {
                'classSize': 97,
                'count': 5,
                'grade': 'B+',
                'percentage': 5.2,
            },
            {
                'classSize': 97,
                'count': 1,
                'grade': 'C+',
                'percentage': 1.0,
            },
            {
                'classSize': 97,
                'count': 1,
                'grade': 'F',
                'percentage': 1.0,
            },
            {
                'classSize': 97,
                'count': 14,
                'grade': 'P',
                'percentage': 14.4,
            },
        ]

    @pytest.mark.skip(reason='get_grade_distribution_with_enrollments will be repurposed for RIP-541')
    def test_enrollment_distribution(self):
        d = get_grade_distribution_with_enrollments('2228', ['99999'])
        assert d == {
            'ANTHRO 197': [
                {
                    'grade': 'A+',
                    'noPriorEnrollCount': 14,
                    'noPriorEnrollPercentage': 17.1,
                    'priorEnrollCount': 2,
                    'priorEnrollPercentage': 22.2,
                    'totalCount': 16,
                    'totalPercentage': 17.6,
                },
                {
                    'grade': 'A',
                    'noPriorEnrollCount': 50,
                    'noPriorEnrollPercentage': 61.0,
                    'priorEnrollCount': 2,
                    'priorEnrollPercentage': 22.2,
                    'totalCount': 52,
                    'totalPercentage': 57.1,
                },
                {
                    'grade': 'A-',
                    'noPriorEnrollCount': 8,
                    'noPriorEnrollPercentage': 9.8,
                    'priorEnrollCount': 0,
                    'priorEnrollPercentage': 0.0,
                    'totalCount': 8,
                    'totalPercentage': 8.8,
                },
                {
                    'grade': 'B+',
                    'noPriorEnrollCount': 5,
                    'noPriorEnrollPercentage': 6.1,
                    'priorEnrollCount': 0,
                    'priorEnrollPercentage': 0.0,
                    'totalCount': 5,
                    'totalPercentage': 5.5,
                },
                {
                    'grade': 'C+',
                    'noPriorEnrollCount': 1,
                    'noPriorEnrollPercentage': 1.2,
                    'priorEnrollCount': 0,
                    'priorEnrollPercentage': 0.0,
                    'totalCount': 1,
                    'totalPercentage': 1.1,
                },
                {
                    'grade': 'F',
                    'noPriorEnrollCount': 0,
                    'noPriorEnrollPercentage': 0.0,
                    'priorEnrollCount': 1,
                    'priorEnrollPercentage': 11.1,
                    'totalCount': 1,
                    'totalPercentage': 1.1,
                },
                {
                    'grade': 'P',
                    'noPriorEnrollCount': 4,
                    'noPriorEnrollPercentage': 4.9,
                    'priorEnrollCount': 4,
                    'priorEnrollPercentage': 44.4,
                    'totalCount': 8,
                    'totalPercentage': 8.8,
                },
            ],
            'ASTRON 218': [
                {
                    'grade': 'A+',
                    'noPriorEnrollCount': 15,
                    'noPriorEnrollPercentage': 17.6,
                    'priorEnrollCount': 1,
                    'priorEnrollPercentage': 16.7,
                    'totalCount': 16,
                    'totalPercentage': 17.6,
                },
                {
                    'grade': 'A',
                    'noPriorEnrollCount': 51,
                    'noPriorEnrollPercentage': 60.0,
                    'priorEnrollCount': 1,
                    'priorEnrollPercentage': 16.7,
                    'totalCount': 52,
                    'totalPercentage': 57.1,
                },
                {
                    'grade': 'A-',
                    'noPriorEnrollCount': 7,
                    'noPriorEnrollPercentage': 8.2,
                    'priorEnrollCount': 1,
                    'priorEnrollPercentage': 16.7,
                    'totalCount': 8,
                    'totalPercentage': 8.8,
                },
                {
                    'grade': 'B+',
                    'noPriorEnrollCount': 5,
                    'noPriorEnrollPercentage': 5.9,
                    'priorEnrollCount': 0,
                    'priorEnrollPercentage': 0.0,
                    'totalCount': 5,
                    'totalPercentage': 5.5,
                },
                {
                    'grade': 'C+',
                    'noPriorEnrollCount': 1,
                    'noPriorEnrollPercentage': 1.2,
                    'priorEnrollCount': 0,
                    'priorEnrollPercentage': 0.0,
                    'totalCount': 1,
                    'totalPercentage': 1.1,
                },
                {
                    'grade': 'F',
                    'noPriorEnrollCount': 0,
                    'noPriorEnrollPercentage': 0.0,
                    'priorEnrollCount': 1,
                    'priorEnrollPercentage': 16.7,
                    'totalCount': 1,
                    'totalPercentage': 1.1,
                },
                {
                    'grade': 'P',
                    'noPriorEnrollCount': 6,
                    'noPriorEnrollPercentage': 7.1,
                    'priorEnrollCount': 2,
                    'priorEnrollPercentage': 33.3,
                    'totalCount': 8,
                    'totalPercentage': 8.8,
                },
            ],
        }
