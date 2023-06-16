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


from ripley.externals.data_loch import get_grades_with_demographics


COLLAPSE_ETHNICITIES = {
    'Chinese / Chinese-American': 'Asian / Asian American',
    'East Indian / Pakistani': 'Asian / Asian American',
    'Filipino / Filipino-American': 'Asian / Asian American',
    'Japanese / Japanese American': 'Asian / Asian American',
    'Korean / Korean-American': 'Asian / Asian American',
    'Mexican / Mexican-American / Chicano': 'Hispanic / Latinx',
    'Other Asian': 'Asian / Asian American',
    'Other Spanish-American / Latino': 'Hispanic / Latinx',
    'Puerto Rican': 'Hispanic / Latinx',
    'Thai': 'Asian / Asian American',
    'Vietnamese': 'Asian / Asian American',
}


def get_grade_distribution_with_demographics(term_id, section_ids):
    distribution = {}

    for row in get_grades_with_demographics(term_id, section_ids):
        if not row['grade']:
            continue
        if row['grade'] not in distribution:
            distribution[row['grade']] = {
                'ethnicities': {},
                'genders': {},
                'termsInAttendance': {},
                'transferStatus': {
                    'true': 0,
                    'false': 0,
                },
                'underrepresentedMinorityStatus': {
                    'true': 0,
                    'false': 0,
                },
                'visaTypes': {},
                'total': 1,
            }
        else:
            distribution[row['grade']]['total'] += 1

        def _count_boolean_value(column, distribution_key):
            if row[column]:
                distribution[row['grade']][distribution_key]['true'] += 1
            else:
                distribution[row['grade']][distribution_key]['false'] += 1

        _count_boolean_value('transfer', 'transferStatus')
        _count_boolean_value('minority', 'underrepresentedMinorityStatus')

        def _count_string_value(value, distribution_key):
            value = str(value) if value else 'none'
            if value not in distribution[row['grade']][distribution_key]:
                distribution[row['grade']][distribution_key][value] = 1
            else:
                distribution[row['grade']][distribution_key][value] += 1

        _count_string_value(row['gender'], 'genders')
        _count_string_value(row['terms_in_attendance'], 'termsInAttendance')
        _count_string_value(row['visa_type'], 'visaTypes')

        collapsed_ethnicities = set(COLLAPSE_ETHNICITIES.get(e) or e for e in row['ethnicities'])
        for ethnicity in collapsed_ethnicities:
            _count_string_value(ethnicity, 'ethnicities')

    return distribution
