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
        d = get_grade_distribution_with_demographics('2228', ['99999'])
        assert d == [
            {
                'ethnicities': {
                    'Asian / Asian American': {
                        'count': 6,
                        'percentage': 54.5,
                    },
                    'Hispanic / Latinx': {
                        'count': 10,
                        'percentage': 18.2,
                    },
                    'Not Specified': {
                        'count': 1,
                        'percentage': 50.0,
                    },
                },
                'genders': {
                    'Male': {
                        'count': 5,
                        'percentage': 22.7,
                    },
                    'Female': {
                        'count': 11,
                        'percentage': 16.2,
                    },
                },
                'grade': 'A+',
                'termsInAttendance': {
                    '8': {
                        'count': 2,
                        'percentage': 20.0,
                    },
                    '5': {
                        'count': 7,
                        'percentage': 19.4,
                    },
                    '3': {
                        'count': 7,
                        'percentage': 20.6,
                    },
                },
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
                'visaTypes': {
                    'none': {
                        'count': 14,
                        'percentage': 16.9,
                    },
                    'J1': {
                        'count': 1,
                        'percentage': 100.0,
                    },
                    'PR': {
                        'count': 1,
                        'percentage': 16.7,
                    },
                },
                'total': 16,
            },
            {
                'ethnicities': {
                    'Hispanic / Latinx': {
                        'count': 32,
                        'percentage': 58.2,
                    },
                    'Asian / Asian American': {
                        'count': 3,
                        'percentage': 27.3,
                    },
                    'White': {
                        'count': 17,
                        'percentage': 70.8,
                    },
                },
                'genders': {
                    'Female': {
                        'count': 43,
                        'percentage': 63.2,
                    },
                    'Male': {
                        'count': 8,
                        'percentage': 36.4,
                    },
                    'Genderqueer/Gender Non-Conform': {
                        'count': 1,
                        'percentage': 100.0,
                    },
                },
                'grade': 'A',
                'termsInAttendance': {
                    '8': {
                        'count': 2,
                        'percentage': 20.0,
                    },
                    '7': {
                        'count': 7,
                        'percentage': 70.0,
                    },
                    '5': {
                        'count': 21,
                        'percentage': 58.3,
                    },
                    '3': {
                        'count': 21,
                        'percentage': 61.8,
                    },
                    '6': {
                        'count': 1,
                        'percentage': 100.0,
                    },
                },
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
                'visaTypes': {
                    'none': {
                        'count': 47,
                        'percentage': 56.6,
                    },
                    'PR': {
                        'count': 5,
                        'percentage': 83.3,
                    },
                },
                'total': 52,
            },
            {
                'ethnicities': {
                    'Hispanic / Latinx': {
                        'count': 6,
                        'percentage': 10.9,
                    },
                    'White': {
                        'count': 1,
                        'percentage': 4.2,
                    },
                    'Not Specified': {
                        'count': 1,
                        'percentage': 50.0,
                    },
                },
                'genders': {
                    'Female': {
                        'count': 5,
                        'percentage': 7.4,
                    },
                    'Male': {
                        'count': 3,
                        'percentage': 13.6,
                    },
                },
                'grade': 'A-',
                'termsInAttendance': {
                    '8': {
                        'count': 1,
                        'percentage': 10.0,
                    },
                    '5': {
                        'count': 4,
                        'percentage': 11.1,
                    },
                    '3': {
                        'count': 3,
                        'percentage': 8.8,
                    },
                },
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
                'visaTypes': {
                    'none': {
                        'count': 8,
                        'percentage': 9.6,
                    },
                },
                'total': 8,
            },
            {
                'ethnicities': {
                    'Hispanic / Latinx': {
                        'count': 4,
                        'percentage': 7.3,
                    },
                    'Asian / Asian American': {
                        'count': 1,
                        'percentage': 9.1,
                    },
                },
                'genders': {
                    'Female': {
                        'count': 4,
                        'percentage': 5.9,
                    },
                    'Male': {
                        'count': 1,
                        'percentage': 4.5,
                    },
                },
                'grade': 'B+',
                'termsInAttendance': {
                    '5': {
                        'count': 3,
                        'percentage': 8.3,
                    },
                    '3': {
                        'count': 2,
                        'percentage': 5.9,
                    },
                },
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
                'visaTypes': {
                    'none': {
                        'count': 5,
                        'percentage': 6.0,
                    },
                },
                'total': 5,
            },
            {
                'ethnicities': {
                    'Hispanic / Latinx': {
                        'count': 1,
                        'percentage': 1.8,
                    },
                },
                'genders': {
                    'Male': {
                        'count': 1,
                        'percentage': 4.5,
                    },
                },
                'grade': 'C+',
                'termsInAttendance': {
                    '8': {
                        'count': 1,
                        'percentage': 10.0,
                    },
                },
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
                'visaTypes': {
                    'none': {
                        'count': 1,
                        'percentage': 1.2,
                    },
                },
                'total': 1,
            },
            {
                'ethnicities': {
                    'White': {
                        'count': 1,
                        'percentage': 4.2,
                    },
                },
                'genders': {
                    'Male': {
                        'count': 1,
                        'percentage': 4.5,
                    },
                },
                'grade': 'F',
                'termsInAttendance': {
                    '8': {
                        'count': 1,
                        'percentage': 10.0,
                    },
                },
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
                'visaTypes': {
                    'OT': {
                        'count': 1,
                        'percentage': 100.0,
                    },
                },
                'total': 1,
            },
            {
                'ethnicities': {
                    'White': {
                        'count': 5,
                        'percentage': 20.8,
                    },
                    'Hispanic / Latinx': {
                        'count': 2,
                        'percentage': 3.6,
                    },
                    'Asian / Asian American': {
                        'count': 1,
                        'percentage': 9.1,
                    },
                },
                'genders': {
                    'Male': {
                        'count': 3,
                        'percentage': 13.6,
                    },
                    'Female': {
                        'count': 5,
                        'percentage': 7.4,
                    },
                },
                'grade': 'P',
                'termsInAttendance': {
                    '8': {
                        'count': 3,
                        'percentage': 30.0,
                    },
                    '7': {
                        'count': 3,
                        'percentage': 30.0,
                    },
                    '5': {
                        'count': 1,
                        'percentage': 2.8,
                    },
                    '3': {
                        'count': 1,
                        'percentage': 2.9,
                    },
                },
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
                'visaTypes': {
                    'none': {
                        'count': 8,
                        'percentage': 9.6,
                    },
                },
                'total': 8,
            },
        ]

    def test_enrollment_distribution(self):
        d = get_grade_distribution_with_enrollments('2228', ['99999'])
        assert d == {
            'ANTHRO 197': {
                'A': 2,
                'A+': 2,
                'F': 1,
                'P': 4,
            },
            'ASTRON 218': {
                'A': 1,
                'A-': 1,
                'A+': 1,
                'F': 1,
                'P': 2,
            },
        }
