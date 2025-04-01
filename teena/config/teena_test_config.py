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
import os

from flask import current_app as app
from teena.models.course import Course
from teena.models.course_site import CourseSite
from teena.models.person import Person
from teena.models.ripley_tool import RipleyTools
from teena.models.term import Term
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
    def students(self):
        return self.data.get('students') or []

    @students.setter
    def students(self, value):
        self.data['students'] = value

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
        self.set_real_test_course_users()

    def course_site_creation(self):
        self.get_multiple_test_sites()
        self.set_real_test_course_users()

    def e_grades_export(self):
        self.get_e_grades_test_sites()
        return self.course_sites[0]

    def e_grades_validation(self):
        self.get_e_grades_test_sites()

    def grade_distribution(self):
        site_ids = utils.grade_distribution_site_ids()
        self.course_sites = [CourseSite({'site_id': site_id}) for site_id in site_ids]
        self.set_real_test_course_users(self.course_sites[-1])

    def mailing_lists(self):
        test_users_data = app.config['TEST_USERS']
        test_users = [Person(data) for data in test_users_data]
        self.canvas_admin = Person({'role': 'Canvas Admin'})
        self.course_sites = [
            CourseSite({
                'abbreviation': f'Admin {self.test_id}',
                'manual_members': [u for u in test_users if u.role not in ['Owner', 'Maintainer', 'Member']],
                'term': self.current_term,
                'title': f'List 1 {self.test_id}',
            }),
            CourseSite({
                'abbreviation': f'Admin {self.test_id}',
                'manual_members': [u for u in test_users if u.role == 'Teacher'],
                'term': self.current_term,
                'title': f'List 2 {self.test_id}',
            }),
            CourseSite({
                'abbreviation': f'Instructor {self.test_id}',
                'manual_members': [u for u in test_users if u.role not in ['Owner', 'Maintainer', 'Member']],
                'term': self.current_term,
                'title': f'List 3 {self.test_id}',
            }),
            CourseSite({
                'abbreviation': f'Old Site {self.test_id}',
                'manual_members': [u for u in test_users if u.role == 'Teacher'],
                'term': utils.previous_term(self.previous_term),
                'title': f'Old Site {self.test_id}',
            }),
            CourseSite({
                'abbreviation': f'Project Site {self.test_id}',
                'manual_members': [u for u in test_users if u.role in ['Owner', 'Maintainer', 'Member']],
                'title': f'Project Site 5 {self.test_id}',
            }),
        ]

    def official_sections(self):
        self.set_real_test_course_users()

    def projects(self):
        site = CourseSite({'title': f'Project {self.test_id}'})
        self.set_real_test_project_users(site)
        return site

    def rosters(self):
        self.set_real_test_course_users()

    def user_provisioning(self):
        self.set_real_test_course_users()

    def welcome_email(self):
        test_users_data = app.config['TEST_USERS']
        test_users = [Person(data) for data in test_users_data]
        return CourseSite({
            'abbreviation': f'Welcome Email {self.test_id}',
            'manual_members': [u for u in test_users if u.role in ['Teacher', 'Student']],
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

    def get_courses_for_multi_course_site(self, courses):
        # For testing a course site containing multiple courses
        primary_sections = []
        for co in courses:
            if co.term == self.current_term:
                for se in co.sections:
                    if se.is_primary and se.instructors_with_roles:
                        primary_sections.append(se)
        primary_sections.sort(key=lambda s: len(s.enrollments))
        i_with_r = [p.instructor_with_roles for p in primary_sections[0:2]]
        instructors = [i.user for i in i_with_r]
        uniq_instructors = list(set(instructors))
        return Course({
            'code': primary_sections[0].course,
            'multi_course': True,
            'sections': primary_sections[0:2],
            'teachers': uniq_instructors,
            'term': self.current_term,
        })

    def get_sis_test_courses(self):
        prefixes = app.config['COURSE_PREFIXES']
        courses = [ripley_utils.get_test_course(self.current_term, p) for p in prefixes]
        courses.extend([ripley_utils.get_test_course(self.next_term, p) for p in prefixes])
        courses = [c for c in courses if c]
        # Create a pseudo course where a TA will acquire the Teacher role on a site with only secondary sections
        ta_course = self.get_course_for_ta_only_site(courses)
        if ta_course:
            courses.append(ta_course)
        # Create a pseudo course where sections from different real courses will inhabit the same site
        multi_course = self.get_courses_for_multi_course_site(courses)
        if multi_course:
            courses.append(multi_course)
        for cou in courses:
            ripley_utils.get_course_enrollment(cou)
        return courses

    # COURSE SITES

    def get_multiple_test_sites(self):
        courses = self.get_sis_test_courses()
        course_sites = []
        for course in courses:
            primaries = [sec for sec in course.sections if sec.is_primary]
            has_template = utils.course_template_dept() in course.code
            # Workflow in admin tool is by instructor UID or by CCN list
            workflow = 'uid' if len(primaries) > 1 or not primaries and not course.multi_course else 'ccn'
            course_sites.append(CourseSite({
                'abbreviation': f'{self.test_id} {course.term.name} {course.code}',
                'course': course,
                'create_site_workflow': workflow,
                'has_template': has_template,
                'sections': course.sections,
                'title': f'{self.test_id} {course.term.name} {course.code}',
            }))

        # Switch half of the UID workflows to 'masq', which means masquerade as the instructor via Canvas rather than Ripley
        instructor_workflow_sites = [site for site in course_sites if site.create_site_workflow == 'uid']
        for uid_site in instructor_workflow_sites:
            if instructor_workflow_sites.index(uid_site) % 2 == 0:
                uid_site.create_site_workflow = 'masq'

        for site in course_sites:
            if site in instructor_workflow_sites and [section for section in site.sections if section.is_primary]:

                # Only use a primary section instructor if testing primary sections
                site.course.teachers = [ripley_utils.get_primary_instructors(site)[0]]

                # Ditch sections not associated with the instructor since they shouldn't appear
                primary_ids = []
                for s in site.course.sections:
                    users = [i_and_r.user for i_and_r in s.instructor_with_roles]
                    if s.is_primary and site.course.teachers[0] in users:
                        primary_ids.append(s.section_id)
                for s in site.course.sections:
                    if s.section_id not in primary_ids or not list(set(primary_ids) & set(s.primary_assoc_ids)):
                        site.course.sections.remove(s)

            app.logger.info(f'Course: {site.course.term.name} {site.course.code} workflow {site.create_site_workflow}')
            app.logger.info(f'Instructor: {site.course.teachers[0].uid}')
            app.logger.info(f'Course sections: {[se.section_id for se in site.course.sections]}')
            app.logger.info(f'Site sections: {[sect.section_id for sect in site.sections]}')
        self.course_sites = course_sites

    def get_single_test_site(self, section_ids=None, opts=None):
        course_site = None
        if os.getenv('SITE'):
            course_site = CourseSite({
                'site_id': str(os.getenv('SITE')),
            })
        else:
            self.get_multiple_test_sites()
            for site in self.course_sites:
                sections = site.course.sections
                primaries = [s for s in sections if s.is_primary]
                secondaries = [s for s in sections if not s.is_primary]
                if primaries and secondaries:
                    if opts and opts['multi_primary']:
                        if len(primaries) > 1:
                            course_site = site
                    else:
                        if len(primaries) == 1:
                            course_site = site
        if course_site:
            if section_ids:
                self.get_existing_site_data(course_site, section_ids)
            for section in course_site.course.sections:
                if section.is_primary:
                    section.include_in_site = True
            course_site.create_site_workflow = 'self'
            course_site.course.teachers = [ripley_utils.get_primary_instructors(course_site)[0]]
            return course_site
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
        cs_course_id = ripley_utils.get_cs_course_id_from_section_id(site.term, section_ids[0])
        site.course = ripley_utils.get_course(site.term, cs_course_id)
        site.sections = [s for s in site.course.sections if s.section_id in section_ids]

        if int(site.term.sis_id) < int(self.current_term.sis_id):
            ripley_utils.get_completed_enrollments(site.course)
        elif newt:
            ripley_utils.get_newt_enrollments(site.course)
        else:
            ripley_utils.get_course_enrollment(site.course)

    def get_e_grades_test_sites(self):
        site_ids = utils.e_grades_site_ids()
        self.course_sites = [CourseSite({'site_id': site_id}) for site_id in site_ids]
        for site in self.course_sites:
            self.set_real_test_course_users(site)

    def configure_single_site(self, canvas_page, canvas_api_page, non_teachers, site=None):
        canvas_page.add_ripley_tools([t.value for t in RipleyTools])
        # Set an existing site id as an environment variable or pass an existing site object or create a new site object
        site_id = os.getenv('SITE') or (site and site.site_id)
        if site_id:
            section_ids = canvas_api_page.get_course_site_sis_section_ids(site_id)
            if site:
                self.get_existing_site_data(site, section_ids)
            else:
                site = self.get_single_test_site(section_ids, opts={'multi_primary': True})
        teacher = ripley_utils.get_primary_instructors(site)[0] or site.course.teachers[0]
        members = non_teachers + [teacher]
        canvas_page.set_canvas_ids(members)
        canvas_api_page.get_admin_canvas_id(self.canvas_admin, 'Support Admin')
        return site, teacher

    # USERS

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

        students = ripley_utils.get_users_of_affiliations('STUDENT-TYPE-REGISTERED', 3)
        self.students = students[:2]
        for student in self.students:
            student.role = 'Student'
        self.wait_list_student = students[2]
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

        self.students = ripley_utils.get_users_of_affiliations('STUDENT-TYPE-REGISTERED', 1)
        self.students[0].role = 'Student'

        self.canvas_admin = Person({'role': 'Canvas Admin'})

        if course_site:
            course_site.manual_members = [self.manual_teacher, self.staff, self.ta] + self.students
