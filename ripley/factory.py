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

import os

from flask import Flask
from ripley import cache, db
from ripley.configs import load_configs
from ripley.jobs.background_job_manager import BackgroundJobManager
from ripley.logger import initialize_logger
from ripley.routes import register_routes


background_job_manager = BackgroundJobManager()


def create_app():
    """Initialize Ripley."""
    app = Flask(__name__.split('.')[0])
    load_configs(app)
    initialize_logger(app)
    cache.init_app(app)
    cache.clear()
    db.init_app(app)

    with app.app_context():
        register_routes(app)
        _register_jobs(app)

    return app


def _register_jobs(app):
    from ripley.jobs.add_guest_users_job import AddGuestUsersJob  # noqa
    from ripley.jobs.add_new_users_job import AddNewUsersJob  # noqa
    from ripley.jobs.export_term_enrollments_job import ExportTermEnrollmentsJob  # noqa
    from ripley.jobs.house_keeping_job import HouseKeepingJob  # noqa
    from ripley.jobs.lti_usage_report_job import LtiUsageReportJob  # noqa
    from ripley.jobs.refresh_bcourses_accounts_job import RefreshBcoursesAccountsJob  # noqa
    from ripley.jobs.refresh_bcourses_full_job import RefreshBcoursesFullJob  # noqa
    from ripley.jobs.refresh_bcourses_inactivate_job import RefreshBcoursesInactivateJob  # noqa
    from ripley.jobs.refresh_bcourses_incremental_job import RefreshBcoursesIncrementalJob  # noqa

    if app.config['JOBS_AUTO_START'] and (not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true'):
        background_job_manager.start(app)
