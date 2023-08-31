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

from flask import current_app as app, request
from flask_login import current_user
from ripley.api.errors import BadRequestError, InternalServerError
from ripley.api.util import canvas_role_required, csv_download_response
from ripley.externals import canvas
from ripley.externals.redis import enqueue, get_job
from ripley.lib.berkeley_term import BerkeleyTerm
from ripley.lib.canvas_utils import get_official_sections, get_teaching_terms, prepare_egrades_export
from ripley.lib.egrade_utils import LETTER_GRADES
from ripley.lib.http import tolerant_jsonify


@app.route('/api/canvas_site/egrades_export/options')
@canvas_role_required('TeacherEnrollment')
def egrades_export_options():
    course_settings = canvas.get_course_settings(current_user.canvas_site_id)
    official_sections, section_ids, sections = get_official_sections(current_user.canvas_site_id)
    return tolerant_jsonify({
        'gradingStandardEnabled': course_settings['grading_standard_enabled'],
        'officialSections': [s for s in official_sections if s['id']],
        'sectionTerms': [] if not len(section_ids) else get_teaching_terms(current_user, section_ids=section_ids, sections=sections),
    })


@app.route('/api/canvas_site/egrades_export/prepare', methods=['POST'])
@canvas_role_required('TeacherEnrollment')
def egrades_export_prepare():
    params = request.get_json()
    grade_type = params.get('gradeType', None)
    pnp_cutoff = params.get('pnpCutoff', None)
    section_id = params.get('sectionId', None)
    term_id = params.get('termId', None)

    if None in [grade_type, pnp_cutoff, section_id, term_id]:
        raise BadRequestError('Required parameter(s) are missing')
    if grade_type not in ['current', 'final']:
        raise BadRequestError(f'Invalid gradeType value: {grade_type}')
    if pnp_cutoff not in LETTER_GRADES and pnp_cutoff != 'ignore':
        raise BadRequestError(f'Invalid pnpCutoff value: {pnp_cutoff}')
    try:
        job = enqueue(
            args=[current_user.canvas_site_id, grade_type, pnp_cutoff, section_id, term_id],
            func=prepare_egrades_export,
        )
        if not job:
            raise InternalServerError('Updates cannot be completed at this time.')
    except Exception as e:
        app.logger.error(f'Failed to enqueue egrades_export job where canvas_site_id = {current_user.canvas_site_id}')
        raise e
    return tolerant_jsonify(
        {
            'jobId': job.id,
            'jobRequestStatus': 'Success',
        },
    )


@app.route('/api/canvas_site/egrades_export/download')
@canvas_role_required('TeacherEnrollment')
def egrades_download():
    params = request.args
    job_id = params.get('jobId', None)
    job = get_job(job_id)
    job_status = job.get_status(refresh=True)
    if job_status == 'finished':
        job_result = job.result
        grade_type = job_result['grade_type']
        rows = job_result['rows']
        section_id = job_result['section_id']
        term_id = job_result['term_id']
        term = BerkeleyTerm.from_sis_term_id(term_id)
        return csv_download_response(
            rows=rows,
            filename=f'egrades-{grade_type}-{section_id}-{term.season}-{term.year}-{current_user.canvas_site_id}.csv',
            fieldnames=['ID', 'Name', 'Grade', 'Grading Basis', 'Comments'],
        )
    else:
        raise BadRequestError(f'Sorry, job {job_id} has not finished or failed. (Job status: {job_status})')


@app.route('/api/canvas_site/egrades_export/status', methods=['POST'])
@canvas_role_required('TeacherEnrollment')
def canvas_egrades_export_status():
    job_id = request.get_json().get('jobId', None)
    job = get_job(job_id)
    job_status = job.get_status(refresh=True)
    return tolerant_jsonify({
        'jobStatus': job_status,
        'percentComplete': 0.5,  # TODO: Can we deduce 'percentComplete' value?
    })
