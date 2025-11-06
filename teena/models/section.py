"""
Copyright ©2025. The Regents of the University of California (Regents). All Rights Reserved.

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


class Section(object):

    def __init__(self, data):
        self.data = data
        self.enrollments = []

    @property
    def section_id(self):
        return self.data.get('section_id')

    @section_id.setter
    def section_id(self, value):
        self.data['section_id'] = value

    @property
    def course(self):
        return self.data.get('course')

    @course.setter
    def course(self, value):
        self.data['course'] = value

    @property
    def course_title(self):
        return self.data.get('course_title')

    @course_title.setter
    def course_title(self, value):
        self.data['course_title'] = value

    @property
    def cs_course_id(self):
        return self.data.get('cs_course_id')

    @cs_course_id.setter
    def cs_course_id(self, value):
        self.data['cs_course_id'] = value

    @property
    def include_in_site(self):
        return self.data.get('include_in_site')

    @include_in_site.setter
    def include_in_site(self, value):
        self.data['include_in_site'] = value

    @property
    def instruction_mode(self):
        return self.data.get('instruction_mode')

    @instruction_mode.setter
    def instruction_mode(self, value):
        self.data['instruction_mode'] = value

    @property
    def instructors_with_roles(self):
        return self.data.get('instructors_with_roles')

    @instructors_with_roles.setter
    def instructors_with_roles(self, value):
        self.data['instructors_with_roles'] = value

    @property
    def label(self):
        return self.data.get('label')

    @label.setter
    def label(self, value):
        self.data['label'] = value

    @property
    def locations(self):
        return self.data.get('locations')

    @locations.setter
    def locations(self, value):
        self.data['locations'] = value

    @property
    def number(self):
        return self.data.get('number')

    @number.setter
    def number(self, value):
        self.data['number'] = value

    @property
    def is_primary(self):
        return self.data.get('is_primary')

    @is_primary.setter
    def is_primary(self, value):
        self.data['is_primary'] = value

    @property
    def primary_assoc_ids(self):
        return self.data.get('primary_assoc_ids')

    @primary_assoc_ids.setter
    def primary_assoc_ids(self, value):
        self.data['primary_assoc_ids'] = value

    @property
    def schedules(self):
        return self.data.get('schedules')

    @schedules.setter
    def schedules(self, value):
        self.data['schedules'] = value

    @property
    def sis_id(self):
        return self.data.get('sis_id')

    @sis_id.setter
    def sis_id(self, value):
        self.data['sis_id'] = value

    def enrolled_sids(self):
        sids = [e.student.sid for e in self.enrollments if e.student.sid]
        sids.sort()
        return sids

    def enrolled_last_names(self):
        names = [e.student.last_name.strip().lower() for e in self.enrollments if e.student.last_name]
        names.sort()
        return names

    def enrolled_grades(self):
        grades = [e.grade for e in self.enrollments if e.grade]
        grades.sort()
        return grades

    def enrolled_grading_bases(self):
        grading_bases = [e.grading_basis for e in self.enrollments if e.grading_basis]
        grading_bases.sort()
        return grading_bases


class SectionEnrollment(object):

    def __init__(self, data):
        self.data = data

    @property
    def student(self):
        return self.data.get('student')

    @student.setter
    def student(self, value):
        self.data['student'] = value

    @property
    def grade(self):
        return self.data.get('grade')

    @grade.setter
    def grade(self, value):
        self.data['grade'] = value

    @property
    def grading_basis(self):
        return self.data.get('grading_basis')

    @grading_basis.setter
    def grading_basis(self, value):
        self.data['grading_basis'] = value

    @property
    def section_id(self):
        return self.data.get('section_id')

    @section_id.setter
    def section_id(self, value):
        self.data['section_id'] = value

    @property
    def status(self):
        return self.data.get('status')

    @status.setter
    def status(self, value):
        self.data['status'] = value

    @property
    def term(self):
        return self.data.get('term')

    @term.setter
    def term(self, value):
        self.data['term'] = value
