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

from ripley.merged.grade_distributions import get_grade_distribution_with_demographics, \
    get_grade_distribution_with_enrollments


class TestGradeDistributions:

    def test_demographic_distribution(self):
        d = get_grade_distribution_with_demographics('2228', ['99999'], '30000')
        assert d == [
            {
                'classSize': 91,
                'genders': {
                    'male': {
                        'count': 5,
                        'percentage': 22.7,
                    },
                    'female': {
                        'count': 11,
                        'percentage': 16.2,
                    },
                },
                'grade': 'A+',
                'internationalStatus': {
                    'true': {
                        'count': 2,
                        'percentage': 25.0,
                    },
                    'false': {
                        'count': 14,
                        'percentage': 16.9,
                    },
                },
                'percentage': 17.6,
                'transferStatus': {
                    'true': {
                        'count': 0,
                        'percentage': 0.0,
                    },
                    'false': {
                        'count': 16,
                        'percentage': 18.6,
                    },
                },
                'underrepresentedMinorityStatus': {
                    'true': {
                        'count': 10,
                        'percentage': 18.2,
                    },
                    'false': {
                        'count': 6,
                        'percentage': 16.7,
                    },
                },
                'count': 16,
            },
            {
                'classSize': 91,
                'genders': {
                    'female': {
                        'count': 43,
                        'percentage': 63.2,
                    },
                    'male': {
                        'count': 8,
                        'percentage': 36.4,
                    },
                    'other': {
                        'count': 1,
                        'percentage': 100.0,
                    },
                },
                'grade': 'A',
                'internationalStatus': {
                    'true': {
                        'count': 5,
                        'percentage': 62.5,
                    },
                    'false': {
                        'count': 47,
                        'percentage': 56.6,
                    },
                },
                'percentage': 57.1,
                'transferStatus': {
                    'true': {
                        'count': 3,
                        'percentage': 60.0,
                    },
                    'false': {
                        'count': 49,
                        'percentage': 57.0,
                    },
                },
                'underrepresentedMinorityStatus': {
                    'true': {
                        'count': 32,
                        'percentage': 58.2,
                    },
                    'false': {
                        'count': 20,
                        'percentage': 55.6,
                    },
                },
                'count': 52,
            },
            {
                'classSize': 91,
                'genders': {
                    'female': {
                        'count': 5,
                        'percentage': 7.4,
                    },
                    'male': {
                        'count': 3,
                        'percentage': 13.6,
                    },
                },
                'grade': 'A-',
                'internationalStatus': {
                    'true': {
                        'count': 0,
                        'percentage': 0.0,
                    },
                    'false': {
                        'count': 8,
                        'percentage': 9.6,
                    },
                },
                'percentage': 8.8,
                'transferStatus': {
                    'true': {
                        'count': 0,
                        'percentage': 0.0,
                    },
                    'false': {
                        'count': 8,
                        'percentage': 9.3,
                    },
                },
                'underrepresentedMinorityStatus': {
                    'true': {
                        'count': 6,
                        'percentage': 10.9,
                    },
                    'false': {
                        'count': 2,
                        'percentage': 5.6,
                    },
                },
                'count': 8,
            },
            {
                'classSize': 91,
                'genders': {
                    'female': {
                        'count': 4,
                        'percentage': 5.9,
                    },
                    'male': {
                        'count': 1,
                        'percentage': 4.5,
                    },
                },
                'grade': 'B+',
                'internationalStatus': {
                    'true': {
                        'count': 0,
                        'percentage': 0.0,
                    },
                    'false': {
                        'count': 5,
                        'percentage': 6.0,
                    },
                },
                'percentage': 5.5,
                'transferStatus': {
                    'true': {
                        'count': 0,
                        'percentage': 0.0,
                    },
                    'false': {
                        'count': 5,
                        'percentage': 5.8,
                    },
                },
                'underrepresentedMinorityStatus': {
                    'true': {
                        'count': 4,
                        'percentage': 7.3,
                    },
                    'false': {
                        'count': 1,
                        'percentage': 2.8,
                    },
                },
                'count': 5,
            },
            {
                'classSize': 91,
                'genders': {
                    'male': {
                        'count': 1,
                        'percentage': 4.5,
                    },
                },
                'grade': 'C+',
                'internationalStatus': {
                    'true': {
                        'count': 0,
                        'percentage': 0.0,
                    },
                    'false': {
                        'count': 1,
                        'percentage': 1.2,
                    },
                },
                'percentage': 1.1,
                'transferStatus': {
                    'true': {
                        'count': 1,
                        'percentage': 20.0,
                    },
                    'false': {
                        'count': 0,
                        'percentage': 0.0,
                    },
                },
                'underrepresentedMinorityStatus': {
                    'true': {
                        'count': 1,
                        'percentage': 1.8,
                    },
                    'false': {
                        'count': 0,
                        'percentage': 0.0,
                    },
                },
                'count': 1,
            },
            {
                'classSize': 91,
                'genders': {
                    'male': {
                        'count': 1,
                        'percentage': 4.5,
                    },
                },
                'grade': 'F',
                'internationalStatus': {
                    'true': {
                        'count': 1,
                        'percentage': 12.5,
                    },
                    'false': {
                        'count': 0,
                        'percentage': 0.0,
                    },
                },
                'percentage': 1.1,
                'transferStatus': {
                    'true': {
                        'count': 0,
                        'percentage': 0.0,
                    },
                    'false': {
                        'count': 1,
                        'percentage': 1.2,
                    },
                },
                'underrepresentedMinorityStatus': {
                    'true': {
                        'count': 0,
                        'percentage': 0.0,
                    },
                    'false': {
                        'count': 1,
                        'percentage': 2.8,
                    },
                },
                'count': 1,
            },
            {
                'classSize': 91,
                'genders': {
                    'male': {
                        'count': 3,
                        'percentage': 13.6,
                    },
                    'female': {
                        'count': 5,
                        'percentage': 7.4,
                    },
                },
                'grade': 'P',
                'internationalStatus': {
                    'true': {
                        'count': 0,
                        'percentage': 0.0,
                    },
                    'false': {
                        'count': 8,
                        'percentage': 9.6,
                    },
                },
                'percentage': 8.8,
                'transferStatus': {
                    'true': {
                        'count': 1,
                        'percentage': 20.0,
                    },
                    'false': {
                        'count': 7,
                        'percentage': 8.1,
                    },
                },
                'underrepresentedMinorityStatus': {
                    'true': {
                        'count': 2,
                        'percentage': 3.6,
                    },
                    'false': {
                        'count': 6,
                        'percentage': 16.7,
                    },
                },
                'count': 8,
            },
        ]

    def test_enrollment_distribution(self):
        grades = {
            'A+': {
                'percentage': 17.6,
                'classSize': 91,
                'count': 16,
            },
            'A': {
                'percentage': 57.1,
                'classSize': 91,
                'count': 52,
            },
            'A-': {
                'percentage': 8.8,
                'classSize': 91,
                'count': 8,
            },
            'B+': {
                'percentage': 5.5,
                'classSize': 91,
                'count': 5,
            },
            'C+': {
                'percentage': 1.1,
                'classSize': 91,
                'count': 1,
            },
            'F': {
                'percentage': 1.1,
                'classSize': 91,
                'count': 1,
            },
            'P': {
                'percentage': 8.8,
                'classSize': 91,
                'count': 8,
            },
        }
        d = get_grade_distribution_with_enrollments('2228', ['99999'], grades)
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
