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
import secrets
import signal
import time

from flask import Flask
import redis
from ripley import cache, db
from ripley.configs import load_configs
from ripley.externals.redis import get_url as get_redis_url
from ripley.logger import initialize_logger
from rq import Connection, Queue, Worker
from rq.command import send_shutdown_command


app = Flask(__name__.split('.')[0])
load_configs(app)
initialize_logger(app)
cache.init_app(app)
cache.clear()
db.init_app(app)


def is_worker_alive(redis_url):
    redis_conn = redis.from_url(redis_url)
    workers = Worker.all(redis_conn)
    live_worker = next((w for w in workers if w.pid and w.last_heartbeat and (datetime.now() - w.last_heartbeat).seconds < 600), False)
    return bool(live_worker)


def start_worker(redis_url, name='xenomorph'):
    redis_conn = redis.from_url(redis_url)
    with Connection(redis_conn), app.app_context():
        q = Queue()
        # Shut down existing worker, if running.
        send_shutdown_command(redis_conn, name)
        w = Worker(
            queues=[q],
            connection=redis_conn,
            name=name,
            work_horse_killed_handler=work_horse_killed_handler,
        )
        app.logger.info(_xenomorph_spawned)
        w.work(
            logging_level=app.config['LOGGING_LEVEL'],
            date_format='%Y-%m-%d %H:%M:%S,%f',
            log_format=app.config['LOGGING_FORMAT'],
        )


def stop_workers(redis_url):
    redis_conn = redis.from_url(redis_url)
    with Connection(redis_conn):
        worker_count = Worker.count(redis_conn)
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
                app.logger.info(f'Existing worker (PID {w.pid}) did not stop when asked.')
                os.kill(w.pid, signal.SIGINT)
                w.teardown()
            else:
                # A worker without a PID is incapable of doing any work and needs to be taken off the payroll.
                w.teardown()


def work_horse_killed_handler(job, pid, stat, rusage):
    app.logger.error(f'Job {job.id} (PID {pid}) failed: work horse killed. Resource usage detail: {rusage}')


def _request_stop(redis_conn, worker):
    app.logger.info(f'Sending stop request to worker {worker.name} (PID {worker.pid}).')
    send_shutdown_command(redis_conn, worker.name)


_xenomorph_spawned = r"""
    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    @@                                                                 @@
    @@    __   __ _____ _   _ ________  ____________________ _   _     @@
    @@    \ \ / /|  ___| \ | |  _  |  \/  |  _  | ___ \ ___ \ | | |    @@
    @@     \ V / | |__ |  \| | | | | .  . | | | | |_/ / |_/ / |_| |    @@
    @@     /   \ |  __|| . ` | | | | |\/| | | | |    /|  __/|  _  |    @@
    @@    / /^\ \| |___| |\  \ \_/ / |  | \ \_/ / |\ \| |   | | | |    @@
    @@    \/   \/\____/\_| \_/\___/\_|  |_/\___/\_| \_\_|   \_| |_/    @@
    @@                                                                 @@
    @@          ___________  ___  _    _ _   _  ___________ _          @@
    @@         /  ___| ___ \/ _ \| |  | | \ | ||  ___|  _  \ |         @@
    @@         \ `--.| |_/ / /_\ \ |  | |  \| || |__ | | | | |         @@
    @@          `--. \  __/|  _  | |/\| | . ` ||  __|| | | | |         @@
    @@         /\__/ / |   | | | \  /\  / |\  || |___| |/ /|_|         @@
    @@         \____/\_|   \_| |_/\/  \/\_| \_/\____/|___/ (_)         @@
    @@                                                                 @@
    @@                     ___--=--------___                           @@
    @@                    /. \___\____   _, \_      /-\                @@
    @@                   /. .  _______     __/=====@                   @@
    @@                   \----/  |  / \______/      \-/                @@
    @@               _/         _/ o \                                 @@
    @@              / |    o   /  ___ \                                @@
    @@             / /    o\\ |  / O \ /|      __-_                    @@
    @@            |o|     o\\\   |  \ \ /__--o/o___-_                  @@
    @@            | |      \\\-_  \____  ----  o___-                   @@
    @@            |o|       \_ \     /\______-o\_-                     @@
    @@            | \       _\ \  _/ / |                               @@
    @@            \o \_   _/      __/ /                                @@
    @@             \   \-/   _       /|_                               @@
    @@              \_      / |   - \  |\                              @@
    @@                \____/  \ | /  \   |\                            @@
    @@                        | o |   | \ |                            @@
    @@                        | | |    \ | \                           @@
    @@                       / | /      \ \ \                          @@
    @@                     /|  \o|\--\  /  o |\--\                     @@
    @@                     \----------' \---------'                    @@
    @@                                                                 @@
    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"""


with app.app_context():
    redis_url = get_redis_url()
    while True:
        app.logger.debug('Checking worker status')
        # If we already have a worker (on this instance or another) that seems to be doing its job, leave it be.
        if is_worker_alive(redis_url):
            app.logger.debug('Worker alive, will recheck in 60 seconds')
            time.sleep(60)
        else:
            # Any existing workers have quit, either quietly or loudly. Clear them out of Redis.
            stop_workers(redis_url)
            # Start a new worker with a unique name so that it can coexist alongside any lingering slackers.
            start_worker(redis_url, f'xenomorph_{secrets.token_hex(8)}')
