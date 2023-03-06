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
from ripley.jobs.lti_usage_report_job import LtiUsageReportJob
from tests.util import mock_s3_bucket, read_s3_csv, register_canvas_uris


class TestLtiUsageReportJob:

    @mock_s3
    def test_job_run(self, app):
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'account': [
                    'create_report_provisioning_csv_accounts',
                    'create_report_provisioning_csv_courses',
                    'get_external_tools_1',
                    'get_external_tools_128848',
                    'get_external_tools_129069',
                    'get_external_tools_129409',
                    'get_external_tools_129410',
                    'get_report_provisioning_csv_accounts',
                    'get_report_provisioning_csv_courses',
                    'get_by_id',
                ],
                'course': [
                    'get_external_tools_1234567',
                    'get_external_tools_8876542',
                    'get_external_tools_9876543',
                    'get_tabs_1234567',
                    'get_tabs_8876542',
                    'get_tabs_9876543',
                    'get_teachers_1234567',
                    'get_teachers_8876542',
                    'get_teachers_9876543',
                ],
                'file': [
                    'download_provisioning_csv_accounts',
                    'download_provisioning_csv_courses',
                    'get_provisioning_csv_accounts',
                    'get_provisioning_csv_courses',
                ],
            }, m)

            with mock_s3_bucket(app) as s3:
                LtiUsageReportJob(app)._run()

                summary_report = read_s3_csv(app, s3, 'lti_usage_summary-2023-B')
                assert len(summary_report) == 11
                assert summary_report[0] == 'Tool,URL,Accounts,Courses Visible'
                assert summary_report[1] == 'Canvas Data Portal,https://beta.example.com/session/lti/launch,1,N/A'
                assert summary_report[2] == 'Chat,https://chat.instructure.com/lti/launch,1,1'
                assert summary_report[3] == 'Create a Site,https://cc-dev.example.com/canvas/embedded/site_creation,1,N/A'
                assert summary_report[4] == 'Find a Person to Add,https://cc-dev.example.com/canvas/embedded/course_add_user,1,0'
                assert summary_report[5] == 'SCORM,https://scone-test.instructure.com/packages,1,0'
                assert summary_report[6] == 'SensusAccess,https://www.edu-apps.org/redirect,1,N/A'
                assert summary_report[7] == 'User Provisioning,https://cc-dev.example.com/canvas/embedded/user_provision,1,N/A'
                assert summary_report[8] == 'Course Captures,https://cc-dev.example.com/canvas/embedded/course_mediacasts,1,0'
                assert summary_report[9] == 'W. W. Norton,ncia.wwnorton.com,,1'
                assert summary_report[10] == 'Pizza,https://example.com/pizza/basic_lti,,2'

                courses_report = read_s3_csv(app, s3, 'lti_usage_courses-2023-B')
                assert len(courses_report) == 5
                assert courses_report[0] == 'Course URL,Name,Tool,Teacher,Email'
                assert courses_report[1] == 'https://hard_knocks_api.instructure.com/courses/1234567,COM LIT ABC,W. W. Norton,,'
                assert courses_report[2] == 'https://hard_knocks_api.instructure.com/courses/1234567,COM LIT ABC,Chat,,'
                assert courses_report[3] == 'https://hard_knocks_api.instructure.com/courses/8876542,FOODSERV 10,Pizza,Fitzi Ritz,fitzi@example.com'
                assert courses_report[4] == 'https://hard_knocks_api.instructure.com/courses/9876543,FOODSERV 2,Pizza,Nancy Ritz,nancy@example.com'
