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

    # We will lazy-load canvas_user_id.
    __canvas_user_id = None

    def __init__(self, serialized_composite_key=None):
        composite_key = json.loads(serialized_composite_key) if serialized_composite_key else {}
        uid = composite_key.get('uid', None)
        canvas_course_id = composite_key.get('canvas_course_id', None)
        if uid:
            try:
                uid = str(int(uid))
            except ValueError:
                pass
        self.user = self._load_user(canvas_course_id=canvas_course_id, uid=uid)

    def __repr__(self):
        return f"""<User
                    canvas_course_id={self.user['canvasCourseId']},
                    email_address={self.email_address},
                    is_active={self.is_active},
                    is_admin={self.is_admin},
                    is_anonymous={self.is_anonymous},
                    is_authenticated={self.is_authenticated},
                    uid={self.user['uid']},
                """

    @property
    def canvas_course_id(self):
        return self.user['canvasCourseId']

    def canvas_user_id(self):
        return self._lazy_load_canvas_user_id()

    def get_id(self):
        return self.get_serialized_composite_key(canvas_course_id=self.canvas_course_id, uid=self.uid)

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

    def to_api_json(self):
        return self.user

    @classmethod
    def get_serialized_composite_key(cls, canvas_course_id, uid):
        return json.dumps({
            'canvas_course_id': canvas_course_id,
            'uid': uid,
        })

    def _load_user(self, canvas_course_id=None, uid=None):
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
                'id': uid,
                'canvasCourseId': canvas_course_id,
                # Callable properties (eg, methods) will be invoked by custom serializer: LazyLoadingEncoder in http.py.
                'canvasUserId': self._lazy_load_canvas_user_id,
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

    def _lazy_load_canvas_user_id(self):
        if self.uid and self.__canvas_user_id is None:
            canvas_user_profile = canvas.get_sis_user_profile(self.uid)
            if canvas_user_profile:
                self.__canvas_user_id = canvas_user_profile.id
        return self.__canvas_user_id
