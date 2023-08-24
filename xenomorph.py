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
import signal
import time

from flask import Flask
import redis
from ripley import cache, db
from ripley.configs import load_configs
from ripley.logger import initialize_logger
from rq import Connection, Queue, Worker
from rq.command import send_shutdown_command


app = None


def create_app():
    app = Flask(__name__.split('.')[0])
    load_configs(app)
    initialize_logger(app)
    cache.init_app(app)
    cache.clear()
    db.init_app(app)
    return app


def start_worker(redis_url, name='xenomorph'):
    global app
    app = create_app()
    redis_conn = redis.from_url(redis_url)
    with Connection(redis_conn), app.app_context():
        q = Queue()
        w = Worker(
            queues=[q],
            connection=redis_conn,
            name=name,
            work_horse_killed_handler=work_horse_killed_handler,
        )
        w.work(
            logging_level=app.config['LOGGING_LEVEL'],
            date_format='%Y-%m-%d %H:%M:%S,%f',
            log_format=app.config['LOGGING_FORMAT'],
        )
        app.logger.info('Initialized xenomorph.')


def stop_workers(redis_url):
    global app
    if not app:
        app = create_app()
    redis_conn = redis.from_url(redis_url)
    with Connection(redis_conn):
        worker_count = Worker.count(redis_conn)
        if worker_count > 0:
            app.logger.info(f'{worker_count} existing worker(s) need to be shut down.')
            wait_seconds = 10
            workers = Worker.all(redis_conn)
            for w in workers:
                _request_stop(redis_conn, w)

            # Wait for worker to gracefully shut down.
            time.sleep(wait_seconds)

            workers = Worker.all(redis_conn)
            # Any remaining workers, kill 'em.
            for w in workers:
                if w.pid:
                    os.kill(w.pid, signal.SIGINT)


def work_horse_killed_handler(job, pid, stat, rusage):
    app.logger.error(f'Job {job.id} (PID {pid}) failed: work horse killed. Resource usage detail: {rusage}')


def _request_stop(redis_conn, worker):
    app.logger.info(f'Sending stop request to worker {worker.name} (PID {worker.pid}).')
    send_shutdown_command(redis_conn, worker.name)
