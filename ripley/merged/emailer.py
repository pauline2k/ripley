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
from ripley.externals.b_connected import BConnected


def send_system_error_email(message, subject=None):
    def _scrub(content):
        # TODO: Scrub out sensitive data?
        return content
    if subject is None:
        subject = f'{message[:50]}...' if len(message) > 50 else message
    config_value = app.config['EMAIL_RIPLEY_OPERATIONS']
    email_addresses = config_value if isinstance(config_value, list) else [config_value]
    for email_address in email_addresses:
        BConnected().send(
            message=_scrub(message),
            recipient={
                'email': email_address,
                'name': app.config['EMAIL_RIPLEY_OPERATIONS_LABEL'],
            },
            subject_line=f'Alert: {_scrub(subject)}',
            tolerate_failure_to_send=True,
        )
    app.logger.error(f'Alert: {message}')
