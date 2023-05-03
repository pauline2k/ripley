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
import tempfile

from flask import current_app as app
# TODO from ripley.externals import canvas
# TODO from ripley.externals.s3 import upload_dated_csv
from ripley.jobs.base_job import BaseJob
from ripley.lib.berkeley_term import BerkeleyTerm
from ripley.lib.util import utc_now
from ripley.models.canvas_synchronization import CanvasSynchronization


class RefreshBcoursesJob(BaseJob):

    def _run(self, params={}):
        this_sync = utc_now()

        sis_term_ids = params.get('sis_term_ids', None)
        if not sis_term_ids:
            sis_term_ids = [t.to_canvas_sis_term_id() for t in BerkeleyTerm.get_current_terms().values()]

        # TODO known_users = {}

        sis_ids_csv = tempfile.NamedTemporaryFile(suffix='.csv')
        sis_ids_export = csv.DictWriter(open(sis_ids_csv.name, 'w'), fieldnames=[
            'old_id',
            'new_id',
            'old_integration_id',
            'new_integration_id',
            'type',
        ])
        sis_ids_export.writeheader()

        users_csv = tempfile.NamedTemporaryFile(suffix='.csv')
        users_export = csv.DictWriter(open(users_csv.name, 'w'), fieldnames=[
            'user_id',
            'login_id',
            'first_name',
            'last_name',
            'email',
            'status',
        ])
        users_export.writeheader()

        enrollment_term_exports = {}

        if params['mode'] in ('all', 'recent'):
            for sis_term_id in sis_term_ids:
                enrollment_term_csv = tempfile.NamedTemporaryFile(suffix='.csv')
                enrollment_term_exports[sis_term_id] = csv.DictWriter(open(enrollment_term_csv.name, 'w'), fieldnames=[
                    'course_id',
                    'user_id',
                    'role',
                    'section_id',
                    'status',
                    'associated_user_id',
                ])
                enrollment_term_exports[sis_term_id].writeheader()

        # TODO loop through sections in term enrollments export

        sis_ids_export.close()
        users_export.close()
        if params['mode'] in ('all', 'recent'):
            for export in enrollment_term_exports.values():
                export.close()

        # TODO tempfile uploads to bCourses SIS import API

        # TODO tempfile uploads to S3 archive

        if params['mode'] in ('all', 'recent'):
            CanvasSynchronization.update(enrollments=this_sync, instructors=this_sync)
        app.logger.info(f"bCourses refresh job (mode={params['mode']}) complete.")

    @classmethod
    def description(cls):
        return 'Refreshes bCourses accounts and enrollments from campus data.'

    @classmethod
    def key(cls):
        return 'refresh_bcourses'
