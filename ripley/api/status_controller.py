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

import traceback

from canvasapi.exceptions import CanvasException
from flask import current_app as app
import psycopg2
from ripley import db
from ripley.externals import data_loch
from ripley.externals.b_connected import BConnected
from ripley.externals.canvas import ping_canvas
from ripley.externals.rds import log_db_error
from ripley.externals.redis import redis_status
from ripley.lib.calnet_utils import get_calnet_user_for_uid
from ripley.lib.http import tolerant_jsonify
from ripley.merged.emailer import send_system_error_email
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text


@app.route('/api/ping')
def ping():
    b_connected_ping = None
    calnet_ping = None
    canvas_ping = None
    data_loch_ping = None
    db_ping = None
    _redis_queue_ping = None
    try:
        b_connected_ping = BConnected().ping()
        calnet_ping = _ping_calnet()
        canvas_ping = _ping_canvas()
        data_loch_ping = _data_loch_status()
        db_ping = _db_status()
        _redis_queue_ping = _redis_queue_status()
    except Exception as e:
        subject = str(e)
        subject = f'{subject[:100]}...' if len(subject) > 100 else subject
        message = f'Error during /api/ping: {subject}'
        app.logger.error(message)
        app.logger.exception(e)
        if app.config['EMAIL_IF_PING_HAS_ERROR']:
            send_system_error_email(
                message=f'{message}\n\n<pre>{traceback.format_exc()}</pre>',
                subject=message,
            )

    finally:
        return tolerant_jsonify(
            {
                'app': True,
                'b_connected': b_connected_ping,
                'calnet': calnet_ping,
                'canvas': canvas_ping,
                'data_loch': data_loch_ping,
                'db': db_ping,
                'rq': _redis_queue_ping,
            },
        )


def _data_loch_status():
    sql = 'SELECT 1'
    try:
        rows = data_loch.safe_execute_rds(sql)
        return rows is not None
    except psycopg2.Error as e:
        log_db_error(e, sql)
        return False
    except SQLAlchemyError as e:
        app.logger.error('Database connection error during /api/ping')
        app.logger.exception(e)
        return False


def _db_status():
    sql = text('SELECT 1')
    try:
        db.session.execute(sql)
        return True
    except psycopg2.Error as e:
        log_db_error(e, sql)
        return False
    except SQLAlchemyError as e:
        app.logger.error('Database connection error during /api/ping')
        app.logger.exception(e)
        return False


def _ping_calnet():
    try:
        uid = '1022796'
        calnet_user = get_calnet_user_for_uid(app, uid)
        return calnet_user and calnet_user.get('uid', None)
    except Exception as e:
        app.logger.error('Calnet error during /api/ping')
        app.logger.exception(e)
        return False


def _ping_canvas():
    try:
        return ping_canvas()
    except CanvasException as e:
        app.logger.error('Canvas error during /api/ping')
        app.logger.exception(e)
        return False


def _redis_queue_status():
    try:
        return redis_status()
    except Exception as e:
        app.logger.error('Redis error during /api/ping')
        app.logger.exception(e)
        return False
