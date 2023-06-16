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

from ripley.merged.grade_distributions import get_grade_distribution_with_demographics


class TestGradeDistributions:

    def test_demographic_distribution(self):
        d = get_grade_distribution_with_demographics('2228', ['99999'])
        assert d == {
            'A+': {
                'ethnicities': {
                    'Asian / Asian American': 6,
                    'Hispanic / Latinx': 10,
                    'Not Specified': 1,
                },
                'genders': {
                    'Male': 5,
                    'Female': 11,
                },
                'termsInAttendance': {
                    '8': 2,
                    '5': 7,
                    '3': 7,
                },
                'transferStatus': {
                    'true': 0,
                    'false': 16,
                },
                'underrepresentedMinorityStatus': {
                    'true': 10,
                    'false': 6,
                },
                'visaTypes': {
                    'none': 14,
                    'PR': 1,
                    'J1': 1,
                },
                'total': 16,
            },
            'A': {
                'ethnicities': {
                    'Hispanic / Latinx': 32,
                    'Asian / Asian American': 3,
                    'White': 17,
                },
                'genders': {
                    'Female': 43,
                    'Male': 8,
                    'Genderqueer/Gender Non-Conform': 1,
                },
                'termsInAttendance': {
                    '8': 2,
                    '7': 7,
                    '5': 21,
                    '3': 21,
                    '6': 1,
                },
                'transferStatus': {
                    'true': 3,
                    'false': 49,
                },
                'underrepresentedMinorityStatus': {
                    'true': 32,
                    'false': 20,
                },
                'visaTypes': {
                    'none': 47,
                    'PR': 5,
                },
                'total': 52,
            },
            'A-': {
                'ethnicities': {
                    'Hispanic / Latinx': 6,
                    'White': 1,
                    'Not Specified': 1,
                },
                'genders': {
                    'Female': 5,
                    'Male': 3,
                },
                'termsInAttendance': {
                    '8': 1,
                    '5': 4,
                    '3': 3,
                },
                'transferStatus': {
                    'true': 0,
                    'false': 8,
                },
                'underrepresentedMinorityStatus': {
                    'true': 6,
                    'false': 2,
                },
                'visaTypes': {
                    'none': 8,
                },
                'total': 8,
            },
            'B+': {
                'ethnicities': {
                    'Hispanic / Latinx': 4,
                    'Asian / Asian American': 1,
                },
                'genders': {
                    'Female': 4,
                    'Male': 1,
                },
                'termsInAttendance': {
                    '5': 3,
                    '3': 2,
                },
                'transferStatus': {
                    'true': 0,
                    'false': 5,
                },
                'underrepresentedMinorityStatus': {
                    'true': 4,
                    'false': 1,
                },
                'visaTypes': {
                    'none': 5,
                },
                'total': 5,
            },
            'C+': {
                'ethnicities': {
                    'Hispanic / Latinx': 1,
                },
                'genders': {
                    'Male': 1,
                },
                'termsInAttendance': {
                    '8': 1,
                },
                'transferStatus': {
                    'true': 1,
                    'false': 0,
                },
                'underrepresentedMinorityStatus': {
                    'true': 1,
                    'false': 0,
                },
                'visaTypes': {
                    'none': 1,
                },
                'total': 1,
            },
            'P': {
                'ethnicities': {
                    'White': 5,
                    'Hispanic / Latinx': 2,
                    'Asian / Asian American': 1,
                },
                'genders': {
                    'Male': 3,
                    'Female': 5,
                },
                'termsInAttendance': {
                    '8': 3,
                    '7': 3,
                    '5': 1,
                    '3': 1,
                },
                'transferStatus': {
                    'true': 1,
                    'false': 7,
                },
                'underrepresentedMinorityStatus': {
                    'true': 2,
                    'false': 6,
                },
                'visaTypes': {
                    'none': 8,
                },
                'total': 8,
            },
            'F': {
                'ethnicities': {
                    'White': 1,
                },
                'genders': {
                    'Male': 1,
                },
                'termsInAttendance': {
                    '8': 1,
                },
                'transferStatus': {
                    'true': 0,
                    'false': 1,
                },
                'underrepresentedMinorityStatus': {
                    'true': 0,
                    'false': 1,
                },
                'visaTypes': {
                    'OT': 1,
                },
                'total': 1,
            },
        }
