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

from moto import mock_s3
import requests_mock
from ripley.jobs.export_term_enrollments_job import ExportTermEnrollmentsJob
from tests.util import mock_s3_bucket, read_s3_csv, register_canvas_uris


class TestExportTermEnrollmentsJob:

    @mock_s3
    def test_job_run(self, app):
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'account': [
                    'create_report_provisioning_csv_sections',
                    'get_by_id',
                    'get_report_provisioning_csv_sections',
                ],
                'file': [
                    'download_provisioning_csv_sections',
                    'get_provisioning_csv_sections',
                ],
                'section': [
                    'get_enrollments_10000',
                ],
            }, m)

            with mock_s3_bucket(app) as s3:
                ExportTermEnrollmentsJob(app)._run(params={'sis_term_id': 'TERM:2023-B'})
                provisioning_report = read_s3_csv(app, s3, 'TERM-2023-B-term-enrollments-export')
                assert len(provisioning_report) == 2
                assert provisioning_report[0] ==\
                    'course_id,canvas_section_id,sis_section_id,canvas_user_id,sis_login_id,sis_user_id,role,sis_import_id,enrollment_state'
                assert provisioning_report[1] == '8876542,10000,SEC:2023-B-32936,5678901,40000,UID:40000,TaEnrollment,,active'
