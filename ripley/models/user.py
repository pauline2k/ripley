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
from ripley.lib.canvas_authorization import can_administrate_canvas
from ripley.models.user_auth import UserAuth


class User(UserMixin):

    # We will lazy-load canvas_user site data.
    __canvas_site_id = None

    def __init__(self, serialized_composite_key=None):
        composite_key = json.loads(serialized_composite_key) if serialized_composite_key else {}
        uid = composite_key.get('uid', None)
        canvas_site_id = str(composite_key.get('canvas_site_id', None)).strip()
        self.__canvas_site_id = int(canvas_site_id) if canvas_site_id and canvas_site_id.isnumeric() else None
        acting_as_uid = composite_key.get('acting_as_uid', None)
        self.__acting_as_uid = acting_as_uid
        if uid:
            try:
                uid = str(int(uid))
            except ValueError:
                pass
        self.user = self._load_user(uid=uid)

    def __repr__(self):
        return f"""<User
                    acting_as_uid={self.__acting_as_uid},
                    canvas_site_id={self.user['canvasSiteId']},
                    email_address={self.email_address},
                    is_active={self.is_active},
                    is_admin={self.is_admin},
                    is_anonymous={self.is_anonymous},
                    is_authenticated={self.is_authenticated},
                    uid={self.user['uid']},
                """

    @property
    def acting_as_uid(self):
        return self.__acting_as_uid

    @property
    def canvas_site_id(self):
        return self.__canvas_site_id

    @property
    def canvas_site_user_roles(self):
        return self.user.get('canvasSiteUserRoles')

    @property
    def canvas_user_id(self):
        return self.user['canvasUserId']

    def get_id(self):
        return self.get_serialized_composite_key(
            canvas_site_id=self.canvas_site_id,
            uid=self.uid,
            acting_as_uid=self.acting_as_uid,
        )

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

    @property
    def is_canvas_admin(self):
        return self.user['isCanvasAdmin']

    @property
    def is_teaching(self):
        return self.user['isTeaching']

    def logout(self):
        self.user = self._load_user()

    @property
    def name(self):
        return self.user['name']

    def to_api_json(self):
        return self.user

    @classmethod
    def get_serialized_composite_key(cls, canvas_site_id, uid, acting_as_uid=None):
        return json.dumps({
            'canvas_site_id': canvas_site_id,
            'uid': uid,
            'acting_as_uid': acting_as_uid,
        })

    def _load_canvas_user_data(self, uid):
        canvas_user_data = None
        user_profile = canvas.get_sis_user_profile(uid) if uid else None
        if user_profile:
            course = canvas.get_course(course_id=self.__canvas_site_id) if uid and self.__canvas_site_id else None
            canvas_user_id = user_profile.get('id')
            canvas_user_data = {
                'canvasSiteId': self.__canvas_site_id,
                'canvasSiteCourseCode': course.course_code if course else None,
                'canvasSiteEnrollmentTermId': course.enrollment_term_id if course else None,
                'canvasSiteName': course.name if course else None,
                'canvasSiteSisCourseId': course.sis_course_id if course else None,
                'canvasSiteUserRoles': [],
                'canvasUserId': canvas_user_id,
                'canvasUserAvatarUrl': user_profile.get('avatar_url'),
                'canvasUserLoginId': user_profile.get('login_id'),
                'canvasUserName': user_profile.get('name'),
                'canvasUserPrimaryEmail': user_profile.get('primary_email'),
                'canvasUserShortName': user_profile.get('short_name'),
                'canvasUserSisUserId': user_profile.get('sis_user_id'),
                'canvasUserSortableName': user_profile.get('sortable_name'),
                'canvasUserTitle': user_profile.get('title'),
                'isCanvasAdmin': can_administrate_canvas(uid),
            }
            is_teaching = False
            canvas_site_user = canvas.get_course_user(self.__canvas_site_id, canvas_user_id)
            if canvas_site_user and canvas_site_user.enrollments:
                roles = [e['role'] for e in canvas_site_user.enrollments]
                canvas_user_data['canvasSiteUserRoles'] = roles
                roles_that_teach = ['TeacherEnrollment', 'TaEnrollment', 'Lead TA', 'Reader']
                is_teaching = bool(next((role for role in roles if role in roles_that_teach), None))
            canvas_user_data['isTeaching'] = is_teaching
        return canvas_user_data

    def _load_user(self, uid=None):
        calnet_profile = None
        canvas_user_data = None
        email_address = None
        is_active = False
        is_admin = False
        is_faculty = False
        is_staff = False
        is_teaching = False
        name = None
        # Deduce user metadata.
        if uid:
            calnet_profile = get_calnet_user_for_uid(app, uid)
            user_auth = UserAuth.find_by_uid(uid)
            if calnet_profile:
                name = calnet_profile.get('name') or f'UID {uid}'
                email_address = calnet_profile.get('email') or None
                if not calnet_profile.get('isExpiredPerLdap', True):
                    is_admin = user_auth.is_superuser if user_auth and user_auth.active else False
                    canvas_user_data = self._load_canvas_user_data(uid) or {}
                    canvas_site_user_roles = canvas_user_data.get('canvasSiteUserRoles') if canvas_user_data else None
                    is_active = bool(is_admin or canvas_site_user_roles)
                    affiliations = set(calnet_profile.get('affiliations', []) or [])
                    is_faculty = 'EMPLOYEE-TYPE-ACADEMIC' in affiliations
                    is_staff = 'EMPLOYEE-TYPE-STAFF' in affiliations
                    is_teaching = bool(canvas_user_data and canvas_user_data['isTeaching'])
        return {
            **{
                'canvasActingAsUid': self.__acting_as_uid,
                'canvasSiteId': self.__canvas_site_id,
                'emailAddress': email_address,
                'isActive': is_active,
                'isAdmin': is_admin,
                'isAnonymous': not is_active,
                'isAuthenticated': is_active,
                'isFaculty': is_faculty,
                'isStaff': is_staff,
                'isTeaching': is_teaching,
                'name': name,
                'uid': uid,
            },
            **(calnet_profile or {}),
            **(canvas_user_data or {}),
        }
