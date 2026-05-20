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

from ripley.lib.canvas_user_utils import csv_row_for_campus_user
from tests.util import override_config


def _campus_user(pronouns='she/her'):
    return {
        'ldap_uid': '9876543',
        'first_name': 'Ellen',
        'last_name': 'Ripley',
        'email_address': 'eripley@example.com',
        'sid': None,
        'affiliations': 'EMPLOYEE-TYPE-STAFF',
        'pronouns': pronouns,
    }


class TestCsvRowForCampusUser:

    def test_pronouns_synced_when_flag_enabled(self, app):
        with override_config(app, 'FLAG_CSV_SYNC_PRONOUNS', True):
            row = csv_row_for_campus_user(_campus_user(pronouns='she/her'))
            assert row['pronouns'] == 'she/her'

    def test_decline_to_state_becomes_none(self, app):
        with override_config(app, 'FLAG_CSV_SYNC_PRONOUNS', True):
            row = csv_row_for_campus_user(_campus_user(pronouns='Decline to state'))
            assert row['pronouns'] is None

    def test_none_pronouns_remain_none(self, app):
        with override_config(app, 'FLAG_CSV_SYNC_PRONOUNS', True):
            row = csv_row_for_campus_user(_campus_user(pronouns=None))
            assert row['pronouns'] is None

    def test_pronouns_absent_when_flag_disabled(self, app):
        with override_config(app, 'FLAG_CSV_SYNC_PRONOUNS', False):
            row = csv_row_for_campus_user(_campus_user(pronouns='she/her'))
            assert 'pronouns' not in row
