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

import collections
from contextlib import contextmanager
import csv
from itertools import groupby
import tempfile

from flask import current_app as app
from ripley.externals import canvas
from ripley.externals.data_loch import get_all_active_users
from ripley.externals.s3 import find_last_dated_csvs, upload_dated_csv
from ripley.jobs.base_job import BaseJob
from ripley.jobs.errors import BackgroundJobError
from ripley.lib.berkeley_term import BerkeleyTerm
from ripley.lib.canvas_utils import csv_row_for_campus_user, format_term_enrollments_export, uid_from_canvas_login_id
from ripley.lib.util import utc_now
from ripley.models.canvas_synchronization import CanvasSynchronization
from ripley.models.user_auth import UserAuth


class RefreshBcoursesJob(BaseJob):

    def _run(self, params={}):
        self.dry_run = params.get('isDryRun', None) or False
        self.mode = params.get('mode', None)

        this_sync = utc_now()

        # TODO The incremental flavor of the refresh job will want to pull a stashed user report from S3 rather than generate a new one.
        # It will also pull only a subset of UIDs from campus.
        canvas_users_file = tempfile.NamedTemporaryFile()
        canvas.get_csv_report('users', download_path=canvas_users_file.name)
        all_users_by_uid = {r['ldap_uid']: r for r in get_all_active_users()}
        self.whitelisted_uids = [user.uid for user in UserAuth.get_canvas_whitelist()]

        sis_term_ids = params.get('sis_term_ids', None)
        if not sis_term_ids:
            sis_term_ids = [t.to_canvas_sis_term_id() for t in BerkeleyTerm.get_current_terms().values()]

        if self.mode == 'all':
            export_filenames = [format_term_enrollments_export(term_id) for term_id in sis_term_ids]
            self.enrollment_provisioning_reports = find_last_dated_csvs('canvas_provisioning_reports', export_filenames)

        with sis_import_csv_set(sis_term_ids) as csv_set:
            self.email_deletions = {}
            self.sis_user_id_changes = {}
            self.known_sis_id_updates = {}
            self.known_users = {}

            with open(canvas_users_file.name, 'r') as f:
                canvas_users = csv.DictReader(f)
                for row in canvas_users:
                    new_row = self.process_user(row, all_users_by_uid)
                    if _csv_data_changed(row, new_row):
                        csv_set.users.writerow(new_row)

            if self.mode == 'all':
                self.process_enrollments(csv_set)

            if self.sis_user_id_changes:
                app.logger.warn(f'About to add {len(self.sis_user_id_changes)} SIS user ID changes to CSV')
                for change in self.sis_user_id_changes.values():
                    csv_set.sis_ids.writerow(change)

            for _csv in csv_set.all:
                _csv.filehandle.close()

            self.upload_results(csv_set, this_sync.strftime('%F_%H-%M-%S'))

        app.logger.info('Job complete.')

        if self.mode in ('all', 'recent'):
            CanvasSynchronization.update(enrollments=this_sync, instructors=this_sync)
        app.logger.info(f'bCourses refresh job (mode={self.mode}) complete.')

    def process_user(self, row, all_users_by_uid):
        account_data = uid_from_canvas_login_id(row['login_id'])
        uid = account_data['uid']
        is_inactive = account_data['inactive']

        if not uid:
            return
        if uid in self.known_users:
            app.logger.info(f'User account for UID {uid} already processed, will not attempt to re-process.')
            return

        # Update user attributes from campus data.
        campus_user = all_users_by_uid.get(uid, None)
        if campus_user:
            if is_inactive:
                app.logger.warn(f'Reactivating account for LDAP UID {uid}.')
            new_row = csv_row_for_campus_user(campus_user)
        else:
            new_row = row.copy()
            if uid in self.whitelisted_uids and is_inactive:
                app.logger.warn(f'Reactivating account for unknown LDAP UID {uid}.')
                new_row['login_id'] = uid
            else:
                # Check if there are obsolete email addresses to (potentially) delete.
                if account_data['email'] and (is_inactive or self.mode == 'inactivate'):
                    self.email_deletions.append(account_data['canvas_user_id'])
                if self.mode == 'inactivate':
                    # This LDAP UID no longer appears in campus data. Mark the Canvas user account as inactive.
                    if not is_inactive:
                        app.logger.warn(f'Inactivating account for LDAP UID {uid}.')
                    new_row.update({
                        'login_id': 'inactive-{uid}',
                        'user_id': f'UID:{uid}',
                        'email': None,
                    })

        self.known_users[uid] = new_row['user_id']

        # Update user SIS ID if required.
        if row['user_id'] != new_row['user_id']:
            if row['user_id'] in self.known_sis_id_updates:
                app.logger.debug(f"SIS ID change from {row['user_id']} to {new_row['user_id']} already processed, will not attempt to re-process.")
            else:
                app.logger.warn(f"Will change SIS ID for user sis_login_id:{row['login_id']} from {row['user_id']} to {new_row['user_id']}")
            self.sis_user_id_changes[f"sis_login_id:{row['login_id']}"] = {
                'old_id': row['user_id'],
                'new_id': new_row['user_id'],
                'old_integration_id': None,
                'new_integration_id': None,
                'type': 'user',
            }

        return new_row

    def process_enrollments(self, csv_set):
        for term_id in csv_set.enrollment_terms.keys():
            sections_report = canvas.get_csv_report('sections', term_id=term_id)
            if not sections_report:
                continue

            def by_course_id(r):
                return r['course_id']

            for course_id, csv_rows in groupby(sorted(sections_report, key=by_course_id), key=by_course_id):
                app.logger.debug(f'Refreshing Course ID {course_id}.')
                if course_id:
                    sis_section_ids = set(r['section_id'] for r in csv_rows if r['section_id'])
                    self.process_course_enrollments(term_id, course_id, sis_section_ids, csv_set)

    def process_course_enrollments(self, term_id, course_id, sis_section_ids, csv_set):
        enrollment_provisioning_report = self.enrollment_provisioning_reports.get(format_term_enrollments_export(term_id), None) # noqa
        enrollment_csv = csv_set.enrollment_terms[term_id] # noqa
        # TODO Processing code equivalent to CanvasCsv::SiteMembershipsMaintainer

    def upload_results(self, csv_set, timestamp):
        if csv_set.sis_ids.count:
            upload_dated_csv(csv_set.sis_ids.tempfile.name, 'sis-id-sis-import', 'canvas_sis_imports', timestamp)
            if self.dry_run:
                app.logger.info('Dry run mode, will not post SIS import files to Canvas.')
            else:
                app.logger.info(f'Will post {csv_set.sis_ids.count} SIS ID changes to Canvas.')
                if not canvas.post_sis_import(csv_set.sis_ids.tempfile.name):
                    raise BackgroundJobError('SIS id changes import failed.')

        if csv_set.users.count:
            upload_dated_csv(csv_set.users.tempfile.name, 'user-sis-import', 'canvas_sis_imports', timestamp)
            if self.dry_run:
                app.logger.info('Dry run mode, will not post user import files to Canvas.')
            else:
                app.logger.info(f'Will post {csv_set.users.count} user updates to Canvas.')
                if not canvas.post_sis_import(csv_set.users.tempfile.name):
                    raise BackgroundJobError('Changed users import failed.')

    @classmethod
    def description(cls):
        return 'Refreshes bCourses accounts and enrollments from campus data.'

    @classmethod
    def key(cls):
        return 'refresh_bcourses'


@contextmanager
def sis_import_csv_set(sis_term_ids):
    all_csvs = []

    users_csv = SisImportCsv(['user_id', 'login_id', 'first_name', 'last_name', 'email', 'status'])
    all_csvs.append(users_csv)

    sis_ids_csv = SisImportCsv([
        'old_id',
        'new_id',
        'old_integration_id',
        'new_integration_id',
        'type',
    ])
    all_csvs.append(sis_ids_csv)

    enrollment_term_csvs = {}
    for sis_term_id in sis_term_ids:
        term_csv = SisImportCsv([
            'course_id',
            'user_id',
            'role',
            'section_id',
            'status',
            'associated_user_id',
        ])
        enrollment_term_csvs[sis_term_id] = term_csv
        all_csvs.append(term_csv)

    SisImportCsvSet = collections.namedtuple('SisImportCsvSet', ['users', 'sis_ids', 'enrollment_terms', 'all'])

    try:
        yield SisImportCsvSet(users_csv, sis_ids_csv, enrollment_term_csvs, all_csvs)
    finally:
        for _csv in all_csvs:
            _csv.tempfile.close()


class SisImportCsv:

    def __init__(self, fieldnames):
        self.fieldnames = fieldnames
        self.tempfile = tempfile.NamedTemporaryFile(suffix='.csv')
        self.filehandle = open(self.tempfile.name, 'w')
        self.writer = csv.DictWriter(self.filehandle, fieldnames=self.fieldnames)
        self.writer.writeheader()
        self.count = 0

    def writerow(self, row):
        self.writer.writerow(row)
        self.count += 1


def _csv_data_changed(row, new_row):
    return (
        row['login_id'] != new_row['login_id']
        # Canvas interprets an empty 'email' column as 'Do not change.'
        or (row['email'] and row['email'] != new_row['email'])
        or (row['full_name'] != f"{new_row['first_name']} {new_row['last_name']}"))
