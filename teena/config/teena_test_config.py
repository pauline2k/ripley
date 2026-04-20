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
import calendar
from datetime import datetime as dt

from flask import current_app as app
from ripley.externals import canvas
from teena.models.course import Course
from teena.models.course_site import CourseSite
from teena.models.person import Person
from teena.models.term import Term
from teena.models.test_case import TeenaTestCase
from teena.test_utils import ripley_utils
from teena.test_utils import utils


class TeenaTestConfig(object):

    def __init__(self, data=None):
        self.admin = Person({
            'uid': utils.get_admin_uid(),
            'username': utils.get_admin_username(),
        })
        self.base_url = utils.ripley_base_url()
        self.current_term = utils.current_term()
        self.data = data or {}
        self.next_term = utils.next_term(self.current_term)
        self.previous_term = utils.previous_term(self.current_term)
        self.test_cases = []
        self.test_id = f'{calendar.timegm(dt.now().timetuple())}'

    @property
    def canvas_admin(self):
        return self.data.get('canvas_admin')

    @canvas_admin.setter
    def canvas_admin(self, value):
        self.data['canvas_admin'] = value

    @property
    def course_site(self):
        return self.data.get('course_site')

    @course_site.setter
    def course_site(self, value):
        self.data['course_site'] = value

    @property
    def course_sites(self):
        return self.data.get('course_sites') or []

    @course_sites.setter
    def course_sites(self, value):
        self.data['course_sites'] = value

    @property
    def designer(self):
        return self.data.get('designer')

    @designer.setter
    def designer(self, value):
        self.data['designer'] = value

    @property
    def lead_ta(self):
        return self.data.get('lead_ta')

    @lead_ta.setter
    def lead_ta(self, value):
        self.data['lead_ta'] = value

    @property
    def manual_teacher(self):
        return self.data.get('manual_teacher')

    @manual_teacher.setter
    def manual_teacher(self, value):
        self.data['manual_teacher'] = value

    @property
    def observer(self):
        return self.data.get('observer')

    @observer.setter
    def observer(self, value):
        self.data['observer'] = value

    @property
    def reader(self):
        return self.data.get('reader')

    @reader.setter
    def reader(self, value):
        self.data['reader'] = value

    @property
    def staff(self):
        return self.data.get('staff')

    @staff.setter
    def staff(self, value):
        self.data['staff'] = value

    @property
    def student(self):
        return self.data.get('student')

    @student.setter
    def student(self, value):
        self.data['student'] = value

    @property
    def ta(self):
        return self.data.get('ta')

    @ta.setter
    def ta(self, value):
        self.data['ta'] = value

    @property
    def teachers(self):
        return self.data.get('teachers') or []

    @teachers.setter
    def teachers(self, value):
        self.data['teachers'] = value

    @property
    def wait_list_student(self):
        return self.data.get('wait_list_student')

    @wait_list_student.setter
    def wait_list_student(self, value):
        self.data['wait_list_student'] = value

    # TEST SCRIPT CONFIGURATION

    def add_user(self):
        self.get_single_test_site()
        self.set_real_test_course_users(self.course_site)

    def course_site_creation(self):
        self.get_multiple_test_sites()
        self.set_real_test_course_users()

    def e_grades(self):
        self.course_site = CourseSite({'site_id': utils.e_grades_site_id()})
        self.set_real_test_course_users(self.course_site)

    def grade_distribution(self):
        site_ids = utils.grade_distribution_site_ids()
        self.course_sites = [CourseSite({'site_id': site_id}) for site_id in site_ids]
        self.set_real_test_course_users(self.course_sites[-1])

        # Create test cases containing data per term for each course site being tested
        terms = utils.terms_since_code_red()
        for site in self.course_sites:
            canvas_sections = canvas.get_course_sections(site.site_id)
            section_ids = []
            for canvas_section in canvas_sections:
                if canvas_section.sis_section_id:
                    section_ids.append(canvas_section.sis_section_id.replace('SEC:', ''))
            self.get_existing_site_data(site, section_ids, newt=True)
            instructor = site.course.teachers[0]
            instructor.canvas_id = canvas.get_canvas_user_profile_by_uid(instructor.uid)['id']
            cs_course_id = site.sections[0].cs_course_id
            all_term_courses = ripley_utils.get_all_instr_courses_per_cs_id(terms, instructor, cs_course_id)
            for term_course in all_term_courses:
                enrollments = []
                for section in term_course.sections:
                    if section.is_primary:
                        enrollments.extend(section.enrollments)
                self.test_cases.append(TeenaTestCase(course=term_course,
                                                     enrollments=enrollments,
                                                     instructor=instructor,
                                                     site=site,
                                                     term=term_course.term,
                                                     test_case_id=f'{site.site_id} {term_course.term.sis_id}'))

    def mailing_lists(self):
        ripley_utils.drop_existing_mailing_lists()
        test_users_data = app.config['TEST_USERS']
        test_users = [Person(data) for data in test_users_data]
        test_users = self.set_fake_test_course_users(test_users)
        self.canvas_admin = Person({'role': 'Canvas Admin'})
        self.course_sites = [
            CourseSite({
                'abbreviation': f'Admin {self.test_id}',
                'manual_members': test_users,
                'term': self.current_term,
                'title': f'List 1 {self.test_id}',
            }),
            CourseSite({
                'abbreviation': f'Admin {self.test_id}',
                'manual_members': [self.manual_teacher],
                'term': self.current_term,
                'title': f'List 2 {self.test_id}',
            }),
            CourseSite({
                'abbreviation': f'Instructor {self.test_id}',
                'manual_members': [self.manual_teacher],
                'term': self.current_term,
                'title': f'List 3 {self.test_id}',
            }),
            CourseSite({
                'abbreviation': f'Old Site {self.test_id}',
                'manual_members': [self.manual_teacher],
                'term': utils.previous_term(self.previous_term),
                'title': f'Old Site {self.test_id}',
            }),
            CourseSite({
                'abbreviation': f'Project Site {self.test_id}',
                'title': f'Project Site 5 {self.test_id}',
            }),
        ]

    def official_sections(self):
        self.get_single_test_site(opts={'multi_primary': True})
        self.course_site.sections = [sec for sec in self.course_site.sections if sec.is_primary]
        for s in self.course_site.course.sections:
            s.include_in_site = True if s in self.course_site.sections else False
        self.set_real_test_course_users(self.course_site)

        # Generate test cases for parameterized tests
        site_course_sec_ids = [scs.section_id for scs in self.course_site.course.sections]
        site_course_sec_ids.sort()
        term = self.course_site.term
        courses = ripley_utils.get_instructor_term_courses(term, self.course_site.course.teachers[0])
        for course in courses:
            course_sec_ids = [cs.section_id for cs in course.sections]
            course_sec_ids.sort()
            if site_course_sec_ids == course_sec_ids:
                courses.remove(course)
        courses.append(self.course_site.course)
        for course in courses:
            for section in course.sections:
                self.test_cases.append(TeenaTestCase(course=course,
                                                     section=section,
                                                     test_case_id=f'{term.sis_id} {course.code} {section.section_id}'))

    def projects(self):
        site = CourseSite({'title': f'Project {self.test_id}'})
        self.set_real_test_project_users(site)
        return site

    def rosters(self):
        self.get_single_test_site()
        self.set_real_test_course_users(self.course_site)

    def user_provisioning(self):
        self.set_real_test_course_users()

    def welcome_email(self):
        test_users_data = app.config['TEST_USERS']
        test_users = [Person(data) for data in test_users_data]
        return CourseSite({
            'abbreviation': f'Welcome Email {self.test_id}',
            'manual_members': [u for u in test_users if u.role in ['Teacher', 'Student', 'Waitlist Student']],
            'title': f'Welcome {self.test_id}',
        })

    # SIS COURSE DATA

    @staticmethod
    def get_course_for_ta_only_site(courses):
        ta_course = None
        ta_section = None
        for co in courses:
            secondaries = [s for s in co.sections if not s.is_primary]
            for se in secondaries:
                if se.instructors_with_roles and not list(set(co.teachers) & set(se.instructors_with_roles)):
                    ta_section = se
            if ta_section:
                ta = ta_section.instructors_with_roles[0].user
                sections = []
                for sec in secondaries:
                    if ta in [i.user for i in sec.instructors_with_roles]:
                        sections.append(sec)
                ta_course = Course({
                    'code': ta_section.course,
                    'sections': sections,
                    'teachers': [ta],
                    'term': co.term,
                    'title': co.title,
                })
                break
        return ta_course

    def get_sis_test_courses(self):
        prefixes = app.config['COURSE_PREFIXES']
        courses = [ripley_utils.get_course_from_catalog_id_prefix(self.current_term, p) for p in prefixes]
        courses.extend([ripley_utils.get_course_from_catalog_id_prefix(self.next_term, p) for p in prefixes])
        courses = [c for c in courses if c]
        # Create a pseudo course where a TA will acquire the Teacher role on a site with only secondary sections
        ta_course = self.get_course_for_ta_only_site(courses)
        if ta_course:
            courses.append(ta_course)
        for course in courses:
            ripley_utils.get_course_enrollment(course)
        return courses

    # COURSE SITES

    def get_multiple_test_sites(self, opts=None):
        courses = self.get_sis_test_courses()
        course_sites = []
        for course in courses:
            has_template = utils.course_template_dept() in course.code
            if opts and 'workflow' in opts:
                workflow = opts['workflow']
            else:
                idx = courses.index(course)
                if idx == 0:
                    workflow = 'uid'
                elif idx == 1:
                    workflow = 'ccn'
                else:
                    workflow = 'masq'
            course_sites.append(CourseSite({
                'abbreviation': f'{self.test_id} {course.term.name} {course.code}',
                'course': course,
                'create_site_workflow': workflow,
                'has_template': has_template,
                'sections': course.sections,
                'term': course.term,
                'title': f'{self.test_id} {course.term.name} {course.code}',
            }))

        for site in course_sites:
            if site.create_site_workflow in ['uid', 'masq'] and [section for section in site.sections if section.is_primary]:
                # Only use a primary section instructor if testing primary sections
                site.course.teachers = [ripley_utils.get_primary_instructors(site)[0]]

                # Ditch sections not associated with the instructor since they shouldn't appear
                primary_ids = []
                for s in site.course.sections:
                    users = [i_and_r.user for i_and_r in s.instructors_with_roles]
                    if s.is_primary and site.course.teachers[0] in users:
                        primary_ids.append(s.section_id)
                for s in site.course.sections:
                    if s.section_id not in primary_ids and not list(set(primary_ids) & set(s.primary_assoc_ids)):
                        site.course.sections.remove(s)

            app.logger.info(f'Course: {site.course.term.name} {site.course.code}')
            app.logger.info(f'Workflow: {site.create_site_workflow}')
            app.logger.info(f'Instructor: {site.course.teachers[0].uid}')
            app.logger.info(f'Course sections: {[cs.section_id for cs in site.course.sections]}')
            app.logger.info(f'Site sections: {[ss.section_id for ss in site.sections]}')
        self.course_sites = course_sites

    def get_single_test_site(self, section_ids=None, opts=None):
        self.get_multiple_test_sites(opts={'workflow': 'uid'})
        for site in self.course_sites:
            sections = site.course.sections
            primaries = [s for s in sections if s.is_primary]
            secondaries = [s for s in sections if not s.is_primary]
            if primaries and secondaries:
                if opts and opts['multi_primary']:
                    if len(primaries) > 1:
                        self.course_site = site
                        break
                else:
                    if len(primaries) == 1:
                        self.course_site = site
                        break
        if self.course_site:
            if section_ids:
                self.get_existing_site_data(self.course_site, section_ids)
            for section in self.course_site.course.sections:
                if section.is_primary:
                    section.include_in_site = True
            self.course_site.create_site_workflow = 'uid'
            self.course_site.course.teachers = [ripley_utils.get_primary_instructors(self.course_site)[0]]
            self.teachers = self.course_site.course.teachers
        else:
            raise

    def get_existing_site_data(self, site, sis_section_ids, newt=False):
        term_code = '-'.join(sis_section_ids[0].split('-')[:2])
        term_name = utils.term_hyphenated_code_to_name(term_code)
        term_sis_id = utils.term_name_to_sis_code(term_name)
        site.term = Term({
            'code': term_code,
            'name': term_name,
            'sis_id': term_sis_id,
        })

        section_ids = [s_id.split('-')[2] for s_id in sis_section_ids]
        sections = ripley_utils.get_sections_from_section_ids(site.term, section_ids)
        site.course = ripley_utils.get_course_from_sections(site.term, sections)
        if newt:
            ripley_utils.get_newt_enrollments(site.course)
        elif int(site.term.sis_id) < int(self.current_term.sis_id):
            ripley_utils.get_completed_enrollments(site.course)
        else:
            ripley_utils.get_course_enrollment(site.course)
        site.sections = site.course.sections

    # USERS

    def set_fake_test_course_users(self, users):
        for user in users:
            if user.role == 'Teacher':
                self.manual_teacher = user
            elif user.role == 'Lead TA':
                self.lead_ta = user
            elif user.role == 'TA':
                self.ta = user
            elif user.role == 'Designer':
                self.designer = user
            elif user.role == 'Reader':
                self.reader = user
            elif user.role == 'Observer':
                self.observer = user
            elif user.role == 'Student':
                self.student = user
            elif user.role == 'Waitlist Student':
                self.wait_list_student = user
        members = [self.manual_teacher, self.lead_ta, self.ta, self.designer, self.reader, self.observer,
                   self.student, self.wait_list_student]
        members = [m for m in members if m]
        return members

    def set_real_test_course_users(self, course_site=None):
        teachers = ripley_utils.get_users_of_affiliations('EMPLOYEE-TYPE-ACADEMIC', 1)
        self.manual_teacher = teachers[0]
        self.manual_teacher.role = 'Teacher'

        tas = ripley_utils.get_users_of_affiliations('EMPLOYEE-TYPE-ACADEMIC,STUDENT-TYPE-REGISTERED', 2)
        self.lead_ta = tas[0]
        self.lead_ta.role = 'Lead TA'
        self.ta = tas[1]
        self.ta.role = 'TA'

        staff = ripley_utils.get_users_of_affiliations('EMPLOYEE-TYPE-STAFF', 3)
        self.designer = staff[0]
        self.designer.role = 'Designer'
        self.reader = staff[1]
        self.reader.role = 'Reader'
        self.observer = staff[2]
        self.observer.role = 'Observer'

        students = ripley_utils.get_users_of_affiliations('STUDENT-TYPE-REGISTERED', 2)
        self.student = students[0]
        self.student.role = 'Student'
        self.wait_list_student = students[1]
        self.wait_list_student.role = 'Waitlist Student'

        self.canvas_admin = Person({'role': 'Canvas Admin'})

        if course_site:
            course_site.manual_members = teachers + tas + staff + students

    def set_real_test_project_users(self, course_site=None):
        self.manual_teacher = ripley_utils.get_users_of_affiliations('EMPLOYEE-TYPE-ACADEMIC', 1)[0]
        self.manual_teacher.role = 'Teacher'

        self.staff = ripley_utils.get_users_of_affiliations('EMPLOYEE-TYPE-STAFF', 1)[0]
        self.staff.role = 'Staff'

        # Repurpose TA user as a non-teaching grad student for project tests
        self.ta = ripley_utils.get_project_grad_student()

        self.student = ripley_utils.get_users_of_affiliations('STUDENT-TYPE-REGISTERED', 1)[0]
        self.student.role = 'Student'

        self.canvas_admin = Person({'role': 'Canvas Admin'})

        if course_site:
            course_site.manual_members = [self.manual_teacher, self.staff, self.ta, self.student]
