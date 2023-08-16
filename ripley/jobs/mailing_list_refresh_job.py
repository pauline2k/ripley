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

import re

from flask import current_app as app
from ripley.jobs.base_job import BaseJob
from ripley.lib.berkeley_term import BerkeleyTerm
from ripley.models.mailing_list import MailingList


class MailingListRefreshJob(BaseJob):

    def _run(self, params={}):
        update_count = 0
        current_term_abbreviations = [t.to_abbreviation() for t in BerkeleyTerm.get_current_terms().values()]

        for mailing_list in MailingList.query.all():
            m = re.match('(?:sp|su|fa)\\d\\d\\Z/', mailing_list.list_name)
            if m and m.group(0) not in current_term_abbreviations:
                continue
            MailingList.populate(mailing_list)
            update_count += 1

        app.logger.info(f'Updated membership for {update_count} mailing lists, job complete.')

    @classmethod
    def description(cls):
        return 'Updates memberships for current term mailing lists.'

    @classmethod
    def key(cls):
        return 'mailing_list_refresh'
