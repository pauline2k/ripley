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

from enum import Enum


class RipleyJob(object):

    def __init__(self, name, key):
        self.name = name
        self.key = key


class RipleyJobs(Enum):

    ADD_GUEST_USERS = RipleyJob('Add Guest Users', 'add_guest_users')
    ADD_NEW_USERS = RipleyJob('Add New Users', 'add_new_users')
    DELETE_EMAIL_ADDRESSES = RipleyJob('Bcourses Delete Email Addresses', 'bcourses_refresh_accounts')
    EXPORT_TERM_ENROLLMENTS = RipleyJob('Export Term Enrollments', 'export_term_enrollments')
    HOUSE_KEEPING = RipleyJob('House Keeping', 'house_keeping')
    REFRESH_ACCOUNTS = RipleyJob('Bcourses Refresh Accounts', 'bcourses_refresh_accounts')
    REFRESH_FULL = RipleyJob('Bcourses Refresh Full', 'bcourses_refresh_full')
    REFRESH_INCREMENTAL = RipleyJob('Bcourses Refresh Incremental', 'bcourses_refresh_incremental')
    REFRESH_MAILING_LIST = RipleyJob('Mailing List Refresh', 'mailing_list_refresh')
    REPORT_LTI_USAGE = RipleyJob('Lti Usage Report', 'lti_usage_report')
