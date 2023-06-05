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

import redis
from ripley.factory import create_app
from rq import Connection, Queue, Worker
from rq.command import send_shutdown_command

"""On Mac OS 10.13 and later, disable the fork() crash behavior:
(see https://github.com/rq/rq/issues/1418)

>>> export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

Start the worker:

>>> rq worker
"""


def start_worker():
    app = create_app()
    redis_conn = redis.from_url(app.config['REDIS_URL'])

    # Kill predecessor
    existing_workers = Worker.all(connection=redis_conn)
    if len(existing_workers):
        print(f'Attempting to shut down {len(existing_workers)} existing workers.')
        for w in existing_workers:
            send_shutdown_command(redis_conn, w.name)

    with Connection(redis_conn), app.app_context():
        queue = Queue(connection=redis_conn)
        print(f'Using queue {queue.name}')
        print(Worker.all(connection=redis_conn))
        worker = Worker(queue)
        worker.work()
        print(f'Worker {worker.name} listening on queue {queue.name}.')
