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

import hashlib
import hmac
from time import time

from flask import cache, current_app as app, request
from ripley.api.errors import UnauthorizedRequestError
from ripley.lib.http import tolerant_jsonify


@app.route('/api/mailing_lists/message', methods=['POST'])
def relay():
    # See https://documentation.mailgun.com/api-sending.html#retrieving-stored-messages for Mailgun's message parameters.
    params = request.get_json()
    if not _authenticate_message(params):
        raise UnauthorizedRequestError('Could not authenticate mailing list message')
    message_attrs = {
        # Capitalized params are unaltered headers from the original message.
        'id': params.get('Message-Id'),
        'from': params.get('From'),
        'to': params.get('to'),
        # Lowercase params are set by Mailgun.
        'subject': params.get('subject'),
        'body': {
            'html': params.get('body-html'),
            'plain': params.get('body-plain'),
        },
        'sender': params.get('sender'),
        'recipient': params.get('recipient'),
        # TODO handle attachments
    }
    success = _relay_to_list(message_attrs)
    return tolerant_jsonify({'success': success})


def _relay_to_list(message_attrs):
    # TODO
    return True


def _authenticate_message(params):
    timestamp = params.get('timestamp')
    signature = params.get('signature')
    if not timestamp or not _verify_timestamp(timestamp):
        return False
    if not signature or not _verify_signature(timestamp, params.get('token'), signature):
        return False
    # Cache signatures to prevent replay attempts.
    signature_key = "mailing_lists_message/signature/#{params['signature']}"
    if (not cache.get(signature_key)) and cache.set(signature_key, True, timeout=3600):
        return True


# Verify Mailgun signature per https://documentation.mailgun.com/en/latest/user_manual.html#webhooks
def _verify_signature(timestamp, token, signature):
    hmac_digest = hmac.new(key=app.config['MAILGUN_API_KEY'].encode(),
                           msg=('{}{}'.format(timestamp, token)).encode(),
                           digestmod=hashlib.sha256).hexdigest()
    return hmac.compare_digest(str(signature), str(hmac_digest))


# Timestamp must be reasonably close to the current time.
def _verify_timestamp(timestamp):
    return (int(time()) - int(timestamp)).abs <= app.config['MAILING_LISTS_TIMESTAMP_TOLERANCE']
