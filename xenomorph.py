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

from datetime import datetime
import os
import signal
import time

import redis
from rq import Connection, Queue, Worker
from rq.worker import StopRequested


def start_worker(redis_url, log_format, log_level, name='xenomorph'):
    redis_conn = redis.from_url(redis_url)
    with Connection(redis_conn):
        q = Queue()
        w = Worker(
            queues=[q],
            connection=redis_conn,
            name=name,
            work_horse_killed_handler=work_horse_killed_handler,
        )
        w.work(
            logging_level=log_level,
            date_format='%Y-%m-%d %H:%M:%S,%f',
            log_format=log_format,
        )


def stop_workers(redis_url):
    redis_conn = redis.from_url(redis_url)
    with Connection(redis_conn):
        wait_seconds = 10
        workers = Worker.all(redis_conn)
        print(f'[{datetime.utcnow()}] - INFO: {Worker.count(redis_conn)} existing workers need to be shut down.')
        for w in workers:
            _request_stop(w)

        # Wait for worker to gracefully shut down.
        time.sleep(wait_seconds)

        workers = Worker.all(redis_conn)
        # Any remaining workers, kill 'em.
        for w in workers:
            os.kill(w.pid, signal.SIGINT)


def work_horse_killed_handler(job, pid, stat, rusage):
    # TODO: better handling: notify Ops or restart automatically
    print(f'[{datetime.utcnow()}] - ERROR: Job {job.id} (PID {pid}) failed: work horse killed. Resource usage detail: {rusage}')


def _request_stop(w):
    print(f'[{datetime.utcnow()}] - INFO: Sending stop request to worker {w.name} (PID {w.pid}).')
    try:
        w.request_stop(signum=signal.SIGINT, frame=None)
    except StopRequested as e:
        print(f'[{datetime.utcnow()}] - INFO: Stop request received.')
