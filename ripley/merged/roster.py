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

from ripley.externals import canvas


def canvas_site_roster(canvas_site_id):
    canvas_sections = canvas.get_course_sections(canvas_site_id)
    sections = [_section(cs) for cs in canvas_sections if cs.sis_section_id]
    sections_by_id = {s['id']: s for s in sections}
    canvas_students = canvas.get_course_students(canvas_site_id, per_page=100)
    return {
        'sections': sections,
        'students': [_student(s, sections_by_id) for s in canvas_students],
    }


def _section(canvas_section):
    return {
        'id': canvas_section.sis_section_id,
        'name': canvas_section.name,
        'sisCourseId': canvas_section.sis_course_id,
    }


def _student(canvas_student, sections_by_id):
    def _get(attr):
        value = None
        if hasattr(canvas_student, attr):
            value = getattr(canvas_student, attr)
        return value
    names = canvas_student.sortable_name.split(', ')
    enrollments = canvas_student.enrollments if hasattr(canvas_student, 'enrollments') else []
    return {
        'email': _get('email'),
        'enrollStatus': enrollments[0]['enrollment_state'] if enrollments else None,
        'firstName': names[1],
        'id': canvas_student.id,
        'lastName': names[0],
        'loginId': _get('login_id'),
        'sections': [sections_by_id[e['sis_section_id']] for e in enrollments if e['sis_section_id']],
        'studentId': canvas_student.sis_user_id,
    }
