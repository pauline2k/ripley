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

from flask import current_app as app
from ripley.api.errors import BadRequestError, ResourceNotFoundError
from ripley.api.util import canvas_role_required
from ripley.lib.http import tolerant_jsonify
from ripley.models.mailing_list import MailingList


@app.route('/api/mailing_lists/<canvas_course_id>')
@canvas_role_required('TeacherEnrollment', 'TaEnrollment', 'Lead TA', 'Reader')
def mailing_lists(canvas_course_id):
    mailing_list = MailingList.find_or_initialize(canvas_course_id)
    return tolerant_jsonify(mailing_list.to_api_json() if mailing_list else None)


@app.route('/api/mailing_lists/<canvas_course_id>/create', methods=['POST'])
@canvas_role_required('TeacherEnrollment', 'TaEnrollment', 'Lead TA', 'Reader')
def create_mailing_lists(canvas_course_id):
    try:
        return tolerant_jsonify(MailingList.create(canvas_course_id).to_api_json())
    except ValueError as e:
        raise BadRequestError(e.message)


@app.route('/api/mailing_lists/<canvas_course_id>/populate', methods=['POST'])
@canvas_role_required('TeacherEnrollment', 'TaEnrollment', 'Lead TA', 'Reader')
def populate_mailing_lists(canvas_course_id):
    mailing_list = MailingList.find_or_initialize(canvas_course_id)
    if mailing_list:
        population_results = MailingList.populate(mailing_list=mailing_list)
        return tolerant_jsonify({
            **mailing_list.to_api_json(),
            'errorMessages': [],  # TODO
            'populationResults': population_results,
        })
    else:
        raise ResourceNotFoundError()
