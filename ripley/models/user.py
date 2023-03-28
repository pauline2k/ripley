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
import json

from flask import current_app as app
from flask_login import UserMixin
from ripley.externals import canvas
from ripley.lib.calnet_utils import get_calnet_user_for_uid
from ripley.models.user_auth import UserAuth


class User(UserMixin):

    # We will lazy-load canvas_user site data.
    __canvas_site_id = None

    def __init__(self, serialized_composite_key=None):
        composite_key = json.loads(serialized_composite_key) if serialized_composite_key else {}
        uid = composite_key.get('uid', None)
        canvas_site_id = str(composite_key.get('canvas_site_id', None)).strip()
        self.__canvas_site_id = int(canvas_site_id) if canvas_site_id and canvas_site_id.isnumeric() else None
        if uid:
            try:
                uid = str(int(uid))
            except ValueError:
                pass
        self.user = self._load_user(uid=uid)

    def __repr__(self):
        return f"""<User
                    canvas_site_id={self.user['canvasSiteId']},
                    email_address={self.email_address},
                    is_active={self.is_active},
                    is_admin={self.is_admin},
                    is_anonymous={self.is_anonymous},
                    is_authenticated={self.is_authenticated},
                    uid={self.user['uid']},
                """

    @property
    def canvas_site_id(self):
        return self.__canvas_site_id

    @property
    def canvas_site_user_roles(self):
        self._load_canvas_user_data()
        return self.user.get('canvasSiteUserRoles')

    @property
    def canvas_user_id(self):
        self._load_canvas_user_data()
        return self.user['canvasUserId']

    def get_id(self):
        return self.get_serialized_composite_key(canvas_site_id=self.canvas_site_id, uid=self.uid)

    @property
    def uid(self):
        return self.user['uid']

    @property
    def email_address(self):
        return self.user['emailAddress']

    @property
    def is_active(self):
        return self.user['isActive']

    @property
    def is_authenticated(self):
        return self.user['isAuthenticated']

    @property
    def is_anonymous(self):
        return self.user['isAnonymous']

    @property
    def is_admin(self):
        return self.user['isAdmin']

    def logout(self):
        self.user = self._load_user()

    @property
    def name(self):
        return self.user['name']

    def to_api_json(self, include_canvas_user_data=False):
        if include_canvas_user_data:
            self._load_canvas_user_data()
        return self.user

    @classmethod
    def get_serialized_composite_key(cls, canvas_site_id, uid):
        return json.dumps({
            'canvas_site_id': canvas_site_id,
            'uid': uid,
        })

    def _load_canvas_user_data(self):
        if self.uid and 'canvasUserId' not in self.user:
            course = canvas.get_course(course_id=self.__canvas_site_id)
            p = canvas.get_sis_user_profile(self.uid) or {}
            canvas_user_id = p.get('id')
            self.user.update({
                'canvasSiteId': self.__canvas_site_id,
                'canvasSiteCourseCode': course.course_code if course else None,
                'canvasSiteEnrollmentTermId': course.enrollment_term_id if course else None,
                'canvasSiteName': course.name if course else None,
                'canvasSiteSisCourseId': course.sis_course_id if course else None,
                'canvasSiteUserRoles': [],
                'canvasUserId': canvas_user_id,
                'canvasUserAvatarUrl': p.get('avatar_url'),
                'canvasUserLoginId': p.get('login_id'),
                'canvasUserName': p.get('name'),
                'canvasUserPrimaryEmail': p.get('primary_email'),
                'canvasUserShortName': p.get('short_name'),
                'canvasUserSisUserId': p.get('sis_user_id'),
                'canvasUserSortableName': p.get('sortable_name'),
                'canvasUserTitle': p.get('title'),
            })
            is_teaching = False
            if self.__canvas_site_id:
                canvas_site_user = canvas.get_course_user(self.__canvas_site_id, canvas_user_id)
                if canvas_site_user and canvas_site_user.enrollments:
                    roles = [e['role'] for e in canvas_site_user.enrollments]
                    self.user['canvasSiteUserRoles'] = roles
                    roles_that_teach = ['TeacherEnrollment', 'TaEnrollment', 'Lead TA', 'Reader']
                    is_teaching = bool(next((role for role in roles if role in roles_that_teach), None))
            self.user['isTeaching'] = is_teaching

    def _load_user(self, uid=None):
        user = UserAuth.find_by_uid(uid) if uid else None
        calnet_profile = get_calnet_user_for_uid(app, uid) if uid else {}
        expired = calnet_profile.get('isExpiredPerLdap', True)
        is_active = not expired and (user.active if user else True)
        is_admin = is_active and (user.is_superuser if user else False)

        affiliations = calnet_profile.get('affiliations', []) or []
        affiliations = set(affiliations if calnet_profile else [])
        is_faculty = 'EMPLOYEE-TYPE-ACADEMIC' in affiliations
        is_staff = 'EMPLOYEE-TYPE-STAFF' in affiliations
        return {
            **calnet_profile,
            **{
                'canvasSiteId': self.__canvas_site_id,
                'emailAddress': calnet_profile.get('email'),
                'isActive': is_active,
                'isAdmin': is_admin,
                'isAnonymous': not is_active,
                'isAuthenticated': is_active,
                'isFaculty': is_faculty,
                'isStaff': is_staff,
                'name': calnet_profile.get('name') or f'UID {uid}',
                'uid': uid,
            },
        }
