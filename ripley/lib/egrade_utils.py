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

from ripley.externals import canvas, data_loch
from ripley.lib.canvas_utils import parse_canvas_sis_section_id

GRADING_BASIS_CODES = ['CPN', 'DPN', 'EPN', 'ESU', 'PNP', 'SUS']
LETTER_GRADES = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F']


def convert_per_grading_basis(grade, override_grade, grading_basis, pnp_cutoff):
    effective_grade = override_grade or grade
    if effective_grade in LETTER_GRADES and grading_basis in GRADING_BASIS_CODES and pnp_cutoff != 'ignore':
        passing = LETTER_GRADES.index(effective_grade) <= LETTER_GRADES.index(pnp_cutoff)
        if grading_basis in ['CPN', 'DPN', 'EPN', 'PNP']:
            effective_grade = 'P' if passing else 'NP'
        else:
            effective_grade = 'S' if passing else 'U'
    return effective_grade


def get_canvas_course_student_grades(canvas_site_id, section_id, term_id):
    enrollments = data_loch.get_basic_profile_and_grades_per_enrollments(term_id=term_id, section_ids=[section_id])
    loch_enrollments_by_uid = {e['ldap_uid']: e for e in enrollments}
    students = []
    for canvas_section in canvas.get_course_sections(canvas_site_id):
        next_section_id, berkeley_term = parse_canvas_sis_section_id(canvas_section.sis_section_id)
        if section_id == next_section_id:
            for enrollment in canvas.get_section(canvas_section.id, api_call=False).get_enrollments():
                required_fields = [hasattr(enrollment, key) for key in ['enrollment_state', 'grades', 'role', 'user']]
                if all(required_fields) and enrollment.role == 'StudentEnrollment':
                    is_active = str(enrollment.enrollment_state).lower() == 'active'
                    uid = enrollment.user.get('login_id')
                    loch_enrollment = loch_enrollments_by_uid.get(uid)
                    if loch_enrollment:
                        if uid and is_active and 'current_grade' in enrollment.grades:
                            students.append({
                                'grades': {
                                    'current_grade': enrollment.grades.get('current_grade'),
                                    'current_score': enrollment.grades.get('current_score'),
                                    'final_grade': enrollment.grades.get('final_grade'),
                                    'final_score': enrollment.grades.get('final_score'),
                                    'override_grade': enrollment.grades.get('override_grade'),
                                    'override_score': enrollment.grades.get('override_score'),
                                },
                                'grading_basis': enrollment['grading_basis'],
                                'name': enrollment.user.get('sortable_name') or enrollment.user.get('name'),
                                'sid': enrollment['sid'],
                                'uid': uid,
                            })
    return students
