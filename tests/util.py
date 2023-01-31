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

from contextlib import contextmanager
import json

import requests_mock


@contextmanager
def override_config(app, key, value):
    """Temporarily override an app config value."""
    old_value = app.config[key]
    app.config[key] = value
    try:
        yield
    finally:
        app.config[key] = old_value


def register_canvas_uris(app, requirements, requests_mocker):
    """
    Given a list of required fixtures and an requests_mocker object, register each fixture as a uri with the mocker.

    This is the same strategy used by the canvasapi module in its internal tests.
    """
    base_url = f"{app.config['CANVAS_API_URL']}/api/v1/"
    for fixture, objects in requirements.items():
        try:
            with open(f'tests/fixtures/{fixture}.json') as file:
                data = json.loads(file.read())
        except (IOError, ValueError):
            raise ValueError(f'Fixture {fixture}.json contains invalid JSON.')

        if not isinstance(objects, list):
            raise TypeError(f'{objects} is not a list.')

        for obj_name in objects:
            obj = data.get(obj_name)

            if obj is None:
                raise ValueError(f'{obj_name.__repr__()} does not exist in {fixture}.json')

            method = requests_mock.ANY if obj['method'] == 'ANY' else obj['method']
            if obj['endpoint'] == 'ANY':
                url = requests_mock.ANY
            else:
                url = base_url + obj['endpoint']

            try:
                requests_mocker.register_uri(
                    method,
                    url,
                    json=obj.get('data'),
                    status_code=obj.get('status_code', 200),
                    headers=obj.get('headers', {}),
                )
            except Exception as e:
                print(e)
