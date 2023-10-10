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

import logging

import requests_mock
from ripley.lib.canvas_lti import configure_tools_from_current_host
from tests.util import register_canvas_uris


class TestConfigureToolsFromCurrentHost:

    def test_configure_tools_from_current_host(self, app, caplog):
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {
                'account': ['get_external_tools_1', 'get_external_tools_129410', 'get_external_tools_129607'],
                'external_tool': [
                    'create_external_tool_1',
                    'create_external_tool_129410',
                    'create_external_tool_129607',
                    'edit_external_tool_provision_user',
                    'edit_external_tool_add_user',
                    'edit_external_tool_roster',
                    'edit_external_tool_export_grade',
                    'edit_external_tool_mailing_list',
                    'edit_external_tool_mailing_lists',
                    'edit_external_tool_manage_sites',
                    'get_external_tool_provision_user',
                    'get_external_tool_add_user',
                    'get_external_tool_roster',
                    'get_external_tool_export_grade',
                    'get_external_tool_mailing_list',
                    'get_external_tool_mailing_lists',
                    'get_external_tool_manage_sites',
                ],
            }, m)

            with caplog.at_level(logging.INFO):
                response = configure_tools_from_current_host()
                assert len(response) == 7
                assert 'Overwriting configuration for add_user (id=35251), provider from https://cc-dev.example.com to https://rip-dev.example.com' \
                    in caplog.text
                assert 'Overwriting configuration for manage_sites (id=40897), provider from https://cc-dev.example.com to https://rip-dev.example.' \
                    'com' in caplog.text
                assert 'Overwriting configuration for export_grade (id=37784), provider from https://cc-dev.example.com to https://rip-dev.example' \
                    '.com' in caplog.text
                assert 'Adding configuration for mailing_list to account 129410' in caplog.text
                assert 'Adding configuration for mailing_lists to account 129607' in caplog.text
                assert 'Overwriting configuration for provision_user (id=27784), provider from https://cc-dev.example.com to https://rip-dev.examp' \
                    'le.com' in caplog.text
                assert 'Overwriting configuration for roster_photos (id=36940), provider from https://cc-dev.example.com to https://rip-dev.exampl' \
                    'e.com' in caplog.text
