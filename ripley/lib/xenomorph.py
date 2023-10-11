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

from flask import current_app as app
import redis
from ripley.externals.redis import get_url as get_redis_url
from rq import Connection, Queue, Worker
from rq.command import send_shutdown_command


class Xenomorph:

    exit_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        self.redis_url = get_redis_url(app)

    def is_worker_alive(self):
        redis_conn = self.get_redis_conn()
        workers = Worker.all(redis_conn)
        live_worker = next(
            (w for w in workers if w.pid and w.last_heartbeat
                and (datetime.now() - w.last_heartbeat).seconds < (app.config['XENOMORPH_HEARTBEAT_SECONDS'] + 15)),
            False,
        )
        return bool(live_worker)

    def start_worker(self, name='xenomorph'):
        redis_conn = self.get_redis_conn()
        with Connection(redis_conn), app.app_context():
            q = Queue()
            # Shut down existing worker, if running.
            send_shutdown_command(redis_conn, name)
            w = Worker(
                queues=[q],
                connection=redis_conn,
                name=name,
                work_horse_killed_handler=self.work_horse_killed_handler,
                default_worker_ttl=app.config['XENOMORPH_HEARTBEAT_SECONDS'],
            )
            _log_xenomorph_start()
            w.work(
                logging_level=app.config['LOGGING_LEVEL'],
                date_format='%Y-%m-%d %H:%M:%S,%f',
                log_format=app.config['LOGGING_FORMAT'],
            )

    def stop_workers(self):
        redis_conn = self.get_redis_conn()
        with Connection(redis_conn):
            worker_count = Worker.count(redis_conn)
            app.logger.info(f'{worker_count} existing worker(s) need to be shut down.')
            wait_seconds = 10
            workers = Worker.all(redis_conn)
            for w in workers:
                self.request_stop(redis_conn, w)

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

    def get_redis_conn(self):
        return redis.from_url(self.redis_url)

    @staticmethod
    def work_horse_killed_handler(job, pid, stat, rusage):
        app.logger.error(f'Job {job.id} (PID {pid}) failed: work horse killed. Resource usage detail: {rusage}')

    @staticmethod
    def request_stop(redis_conn, worker):
        app.logger.info(f'Sending stop request to worker {worker.name} (PID {worker.pid}).')
        send_shutdown_command(redis_conn, worker.name)

    def exit_gracefully(self, *args):
        self.exit_now = True


def start_xenomorph_loop():
    xenomorph = Xenomorph()
    while True:
        app.logger.debug('Checking worker status')
        # If we already have a worker (on this instance or another) that seems to be doing its job, leave it be.
        if xenomorph.is_worker_alive():
            app.logger.debug(f"Worker alive, will recheck in {app.config['XENOMORPH_HEARTBEAT_SECONDS']} seconds")
            for i in range(app.config['XENOMORPH_HEARTBEAT_SECONDS']):
                time.sleep(1)
                if xenomorph.exit_now:
                    xenomorph.stop_workers()
                    break
        elif xenomorph.exit_now:
            break
        else:
            # Any existing workers have quit, either quietly or loudly. Clear them out of Redis.
            xenomorph.stop_workers()
            # Start a new worker with a unique name so that it can coexist alongside any lingering slackers.
            xenomorph.start_worker(f'xenomorph_{secrets.token_hex(8)}')


def _log_xenomorph_start():
    app.logger.info(r"""
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
        @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@""")
