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

import csv
from datetime import datetime

from flask import current_app as app
from ripley.externals import canvas
from ripley.externals.data_loch import get_all_active_users
from ripley.jobs.base_job import BaseJob
from ripley.jobs.errors import BackgroundJobError
from ripley.lib.canvas_utils import uid_from_canvas_login_id, user_id_from_attributes


class AddNewUsersJob(BaseJob):

    def _run(self):
        timestamp = datetime.now().strftime('%F_%H-%M-%S')
        canvas_export_filename = f"{app.config['CANVAS_EXPORT_PATH']}/canvas-{timestamp}-sync-all-users.csv"
        canvas_import_filename = f"{app.config['CANVAS_EXPORT_PATH']}/canvas-{timestamp}-users-report.csv"

        canvas.get_csv_report('users', download_path=canvas_export_filename)

        # Start with a map of all users.
        new_users_by_uid = {r['ldap_uid']: r for r in get_all_active_users()}

        with open(canvas_export_filename, 'r') as canvas_export_file:
            canvas_export = csv.DictReader(canvas_export_file)
            # Remove users from map where UID already exists in Canvas.
            for row in canvas_export:
                uid = uid_from_canvas_login_id(row['login_id'])['uid']
                new_users_by_uid.pop(uid, None)

        if not len(new_users_by_uid):
            app.logger.info('No new users to add, job complete.')
            return
        else:
            app.logger.info(f'Will add {len(new_users_by_uid)} new users.')
            with open(canvas_import_filename, 'w') as canvas_import_file:
                canvas_import = csv.DictWriter(canvas_import_file, fieldnames=['user_id', 'login_id', 'first_name', 'last_name', 'email', 'status']) # noqa
                canvas_import.writeheader()
                for user in new_users_by_uid.values():
                    canvas_import.writerow({
                        'user_id': user_id_from_attributes(user),
                        'login_id': str(user['ldap_uid']),
                        'first_name': user['first_name'],
                        'last_name': user['last_name'],
                        'email': user['email_address'],
                        'status': 'active',
                    })

            if canvas.post_sis_import(canvas_import_filename):
                app.logger.info('Users added, job complete.')
            else:
                raise BackgroundJobError('New users import failed.')

    @classmethod
    def description(cls):
        return 'Adds new campus users to Canvas.'

    @classmethod
    def key(cls):
        return 'add_users'
