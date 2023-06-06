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

from flask import current_app as app
from ripley.externals import canvas
from ripley.jobs.base_job import BaseJob


class ReconfigureCanvasTestServersJob(BaseJob):

    def _run(self):
        test_servers = app.config['CANVAS_TEST_SERVERS']
        for server in test_servers:
            auth_providers = canvas.get_authentication_providers(server)
            for provider in auth_providers:
                if provider.auth_type == 'cas' and provider.auth_base != app.config['CANVAS_TEST_CAS_URL']:
                    app.logger.info(f"Updating CAS auth base on {server} to {app.config['CANVAS_TEST_CAS_URL']}.")
                    provider.update(auth_base=app.config['CANVAS_TEST_CAS_URL'])

        app.logger.info(f'Adjusted configuration on test servers: {test_servers}, job complete.')

    @classmethod
    def description(cls):
        return 'Adjust automatically copied configurations in non-production Canvas environments.'

    @classmethod
    def key(cls):
        return 'reconfigure_canvas_test_servers'
