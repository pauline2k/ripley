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

from fakeredis import FakeStrictRedis
from flask import current_app
import redis
from rq import Callback, Connection, Queue, Worker
from rq.job import Job


redis_conn = None


def enqueue(func, args):
    from ripley.factory import q
    get_redis_conn(current_app)
    status = redis_status()
    queue_ready = len(status['workers']) or not q.is_async
    if not (status['redis'] and queue_ready):
        current_app.logger.exception(f'Job queue unavailable! Status: {status}')
        return False
    with Connection(redis_conn):
        job = q.enqueue(
            f=func,
            args=args,
            on_failure=Callback(report_failure),
            on_stopped=Callback(report_stopped),
        )
        return job


def get_job(job_id):
    get_redis_conn(current_app)
    return Job.fetch(job_id, connection=redis_conn)


def get_redis_conn(app):
    global redis_conn
    if redis_conn is None:
        if app.config['TESTING']:
            redis_conn = FakeStrictRedis()
        elif app.config['REDIS_HOST'] is None:
            redis_conn = redis.from_url('redis://localhost:6379')
        else:
            redis_conn = redis.from_url(f"rediss://default:{app.config['REDIS_PASSWORD']}@{app.config['REDIS_HOST']}:{app.config['REDIS_PORT']}")
    return redis_conn


def redis_status():
    get_redis_conn(current_app)
    q = Queue(connection=redis_conn)
    workers = Worker.all(redis_conn)
    return {
        'redis': q is not None,
        'workers': [_worker_to_api_json(w) for w in workers],
    }


def report_failure(job, connection, type, value, traceback):  # noqa
    current_app.logger.error(f'Job {job.id} failed with {value}.')
    current_app.logger.error(traceback)


def report_stopped(job, connection):  # noqa
    current_app.logger.error(f'Job {job.id} stopped.')


def _worker_to_api_json(worker):
    return {
        'currentJobWorkingTime': worker.current_job_working_time,
        'failedJobCount': worker.failed_job_count,
        'lastHeartbeat': worker.last_heartbeat,
        'logger': worker.log,
        'name': worker.name,
        'pid': worker.pid,
        'state': worker.get_state(),
        'successfulJobCount': worker.successful_job_count,
        'totalWorkingTime': worker.total_working_time,
    }
