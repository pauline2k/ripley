"""
Copyright ©2022. The Regents of the University of California (Regents). All Rights Reserved.

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

import logging
import os

AWS_PROFILE = None
AWS_S3_BUCKET = 'some-bucket'
AWS_S3_REGION = 'us-west-2'

# Base directory for the application (one level up from this config file).
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

CAS_SERVER = 'https://auth-test.berkeley.edu/cas/'

CANVAS_ACCESS_TOKEN = 'a token'
CANVAS_API_URL = 'https://hard_knocks_api.instructure.com'
CANVAS_BERKELEY_ACCOUNT_ID = 1

CURRENT_TERM_ID = '2023-B'

# The Data Loch provides read-only Postgres access.
DATA_LOCH_RDS_URI = 'postgresql://nessie:secret@secret-rds-url.com:5432/db'
DATA_LOCH_MAX_CONNECTIONS = 50

DEV_AUTH_ENABLED = False
DEV_AUTH_PASSWORD = 'another secret'

EMAIL_RIPLEY_SUPPORT = 'bcourseshelp@berkeley.edu'

# Directory to search for mock fixtures, if running in "test" or "demo" mode.
FIXTURES_PATH = None

# Minutes of inactivity before session cookie is destroyed
INACTIVE_SESSION_LIFETIME = 120

# These "INDEX_HTML" defaults are good in ripley-[dev|qa|prod]. See development.py for local configs.
INDEX_HTML = 'dist/static/index.html'

LDAP_HOST = 'ldap-test.berkeley.edu'
LDAP_BIND = 'mybind'
LDAP_PASSWORD = 'secret'

# background_job_manager configs.
JOB_HISTORY_DAYS_UNTIL_EXPIRE = 7
JOBS_AUTO_START = False
JOBS_SECONDS_BETWEEN_PENDING_CHECK = 60

# Logging
LOGGING_FORMAT = '[%(asctime)s] - %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
LOGGING_LOCATION = 'ripley.log'
LOGGING_LEVEL = logging.DEBUG
LOGGING_PROPAGATION_LEVEL = logging.WARN

REMEMBER_COOKIE_NAME = 'remember_ripley_token'

# Used to encrypt session cookie.
SECRET_KEY = 'secret'

# Override in local configs.
SQLALCHEMY_DATABASE_URI = 'postgresql://ripley:ripley@localhost:5432/nostromo'

TIMEZONE = 'America/Los_Angeles'

# This base-URL config should only be non-None in the "local" env where the Vue front-end runs on port 8080.
VUE_LOCALHOST_BASE_URL = None

# We keep these out of alphabetical sort above for readability's sake.
HOST = '0.0.0.0'
PORT = 5000
