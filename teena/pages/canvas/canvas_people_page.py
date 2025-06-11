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
import time

from flask import current_app as app
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait as Wait
from teena.models.canvas_site_roles import CanvasSiteRoles
from teena.models.person import Person
from teena.pages.canvas.canvas_settings_page import CanvasSettingsPage
from teena.test_utils import utils


class CanvasPeoplePage(CanvasSettingsPage):

    USERS_DIV = By.XPATH, '//div[@data-view="users"]'

    def load_users_page(self, site):
        self.navigate_to(f'{utils.canvas_base_url()}/courses/{site.site_id}/users')
        self.when_present(self.USERS_DIV, utils.get_medium_timeout())

    # Search

    ENROLLMENT_ROLES_SELECT = By.NAME, 'enrollment_role_id'
    SECTION_LABEL = By.XPATH, '//td[@data-testid="section-column-cell"]/div[@class="section"]'
    USER_SEARCH_INPUT = By.XPATH, '//input[@placeholder="Search people..."]'
    COURSE_USER_SEARCH_INPUT = By.XPATH, '//input[@placeholder="Search people"]'

    @staticmethod
    def user_result_link_by_email(user):
        return By.XPATH, f'//td[text()="{user.email}"]/preceding-sibling::th/a'

    @staticmethod
    def user_result_link_by_uid(user):
        return By.XPATH, f'//td[text()="{user.sis_id}" or text()="UID:{user.uid}"]/preceding-sibling::th/a'

    def search_user_by_canvas_id(self, user):
        self.wait_for_element_clear_and_send_keys(self.COURSE_USER_SEARCH_INPUT, user.canvas_id)
        time.sleep(utils.get_click_sleep())

    def set_canvas_ids(self, users):
        self.navigate_to(f'{utils.canvas_base_url()}/accounts/{utils.canvas_root_acct()}/users')
        for user in users:
            if not user.canvas_id:
                app.logger.info(f'Getting Canvas ID for {user.uid}')
                for string in [user.email, user.uid]:
                    try:
                        self.wait_for_element_clear_and_send_keys(self.USER_SEARCH_INPUT, string)
                        if string == user.email:
                            loc = self.user_result_link_by_email(user)
                        else:
                            loc = self.user_result_link_by_uid(user)
                        self.when_present(loc, utils.get_short_timeout())
                        canvas_id = self.element(loc).get_dom_attribute('href').split('/')[-1]
                        if canvas_id:
                            user.canvas_id = canvas_id
                            app.logger.info(f'Canvas ID is {user.canvas_id}')
                            break
                    except TimeoutException:
                        app.logger.info(f'Unable to find Canvas ID for UID {user.uid}')

    # Add users (Canvas)

    ADD_PEOPLE_BTN = By.ID, 'addUsers'
    ADD_USER_BY_EMAIL_INPUT = By.XPATH, '//input[@id="peoplesearch_radio_cc_path"]/..'
    ADD_USER_BY_EMAIL_LABEL = By.XPATH, '//label[@for="peoplesearch_radio_cc_path"]'
    ADD_USER_BY_UID_INPUT = By.XPATH, '//input[@id="peoplesearch_radio_unique_id"]/..'
    ADD_USER_BY_UID_LABEL = By.XPATH, '//label[@for="peoplesearch_radio_unique_id"]'
    ADD_USER_BY_SID_INPUT = By.XPATH, '//input[@id="peoplesearch_radio_sis_user_id"]/..'
    ADD_USER_BY_SID_LABEL = By.XPATH, '//label[@for="peoplesearch_radio_sis_user_id"]'
    ADD_USER_HELP_LINK = By.LINK_TEXT, 'How do I add users to my course site?'
    INVALID_USER_INFO_LINK = By.XPATH, '//a[contains(., "Accessing bCourses Without a Calnet Account")]'
    NEXT_BTN = By.ID, 'addpeople_next'
    USER_LIST_INPUT = By.XPATH, '//textarea'
    USER_OPT = By.XPATH, '//span[@role="option"]'
    USER_ROLE_SELECT = By.ID, 'peoplesearch_select_role'
    USER_SECTION_SELECT = By.ID, 'peoplesearch_select_section'
    USERS_READY_TO_ADD_MSG = By.XPATH, '//div[contains(text(),"The following users are ready to be added to the course.")]'

    def click_add_people(self):
        self.wait_for_page_and_click(self.ADD_PEOPLE_BTN)
        self.when_visible(self.FIND_PERSON_TO_ADD_LINK, utils.get_short_timeout())

    def user_role_options(self):
        self.wait_for_element_and_click(self.USER_ROLE_SELECT)
        return self.els_text_if_exist(self.USER_OPT)

    def click_add_by_email(self):
        self.wait_for_element_and_click(self.ADD_USER_BY_EMAIL_INPUT)

    def click_add_by_uid(self):
        self.wait_for_element_and_click(self.ADD_USER_BY_UID_INPUT)

    def click_add_by_sid(self):
        self.wait_for_element_and_click(self.ADD_USER_BY_SID_INPUT)

    def add_user_placeholder(self):
        return self.element(self.USER_LIST_INPUT).get_dom_attribute('placeholder')

    def get_missing_users(self, users_to_add):
        users_missing = []
        Wait(self.driver, utils.get_short_timeout()).until(ec.any_of(
            ec.presence_of_element_located(self.NO_USERS_MSG),
            ec.presence_of_element_located(self.USER_ROW),
        ))
        if self.is_present(self.NO_USERS_MSG):
            users_missing = users_to_add
        else:
            for user in users_to_add:
                try:
                    self.search_user_by_canvas_id(user)
                    self.when_present(self.user_row(user), 1)
                except TimeoutException:
                    users_missing.append(user)
        app.logger.info(f'Users who need to be added are {[u.uid for u in users_missing]}')
        return users_missing

    def add_users_of_role(self, site, users, role, section=None):
        uids = [u.uid for u in users]
        tries = 0
        max_tries = 3
        app.logger.info(f'Adding users with role {role}')
        while tries <= max_tries:
            try:
                tries += 1
                self.load_users_page(site)
                self.wait_for_element_and_click(self.ADD_PEOPLE_BTN)
                self.wait_for_element_and_click(self.ADD_USER_BY_UID_INPUT)
                self.wait_for_element_clear_and_send_keys(self.USER_LIST_INPUT, ', '.join(uids))
                self.wait_for_element_and_click(self.USER_ROLE_SELECT)
                role_opt = next(filter(lambda el: el.text == role, self.elements(self.USER_OPT)))
                role_opt.click()
                if section:
                    self.wait_for_element_and_click(self.USER_SECTION_SELECT)
                    sec_opt = next(filter(lambda el: el.text == section.sis_id, self.elements(self.USER_OPT)))
                    sec_opt.click()
                self.wait_for_element_and_click(self.NEXT_BTN)
                self.when_visible(self.USERS_READY_TO_ADD_MSG, utils.get_medium_timeout())
                self.hide_canvas_footer_and_popups()
                self.wait_for_element_and_click(self.NEXT_BTN)
                self.wait_for_users(users)
                break
            except TimeoutException:
                if tries == max_tries:
                    raise
                else:
                    app.logger.info('Add user failed, retrying')

    def add_users(self, site, users_to_add, section=None):
        uids = [u.uid for u in users_to_add]
        app.logger.info(f'Users needed for the site are {uids}')
        self.load_users_page(site)
        users_missing = self.get_missing_users(users_to_add)
        self.activate_users_and_reset_email(users_missing)
        for role in CanvasSiteRoles.PROJECT_ROLES:
            users_with_role = [u for u in users_missing if u.role == role]
            if users_with_role:
                self.add_users_of_role(site, users_with_role, role, section)

    def add_invalid_uid(self):
        self.wait_for_page_and_click(self.ADD_PEOPLE_BTN)
        self.wait_for_element_and_click(self.ADD_USER_BY_UID_INPUT)
        self.wait_for_element_clear_and_send_keys(self.USER_LIST_INPUT, '123456')
        self.wait_for_element_and_click(self.NEXT_BTN)

    # Add user (Ripley)

    FIND_PERSON_TO_ADD_LINK = By.XPATH, '//a[contains(., "Find a Person to Add")]'

    def click_find_person_to_add(self):
        app.logger.info('Clicking Find a Person to Add button')
        self.wait_for_element_and_click(self.ADD_PEOPLE_BTN)
        self.wait_for_page_and_click(self.FIND_PERSON_TO_ADD_LINK)
        self.switch_to_canvas_iframe(utils.ripley_base_url())

    # Remove users

    DONE_BTN = By.XPATH, '//button[contains(.,"Done")]'
    REMOVE_USER_SUCCESS_MSG = By.XPATH, '//*[contains(.,"User successfully removed")]'

    @staticmethod
    def edit_user_link(user):
        return By.XPATH, f'//tr[@id="user_{user.canvas_id}"]//a[contains(@class, "al-trigger")]'

    @staticmethod
    def remove_user_link(user):
        return By.XPATH, f'//tr[@id="user_{user.canvas_id}"]//a[@data-event="removeFromCourse"]'

    def click_edit_user(self, user):
        self.wait_for_element_and_click(self.edit_user_link(user))

    def remove_user_from_course(self, site, user):
        app.logger.info(f'Removing {user.role} UID {user.uid} for site {site.site_id}')
        self.click_edit_user(user)
        self.wait_for_element_and_click(self.remove_user_link(user))
        self.accept_alert()
        self.when_present(self.REMOVE_USER_SUCCESS_MSG, utils.get_short_timeout())

    def remove_users_from_course(self, site, users):
        self.load_users_page(site)
        self.hide_canvas_footer_and_popups()
        self.wait_for_users(users)
        for user in users:
            self.remove_user_from_course(site, user)

    # Edit user

    EDIT_USER_LINK = By.XPATH, '//a[@class="edit_user_link"]'
    UPDATE_DETAILS_BTN = By.XPATH, '//button[text()="Update Details"]'

    DEFAULT_EMAIL = By.XPATH, '//th[text()="Default Email:"]/following-sibling::td'
    USER_EMAIL_INPUT = By.ID, 'user_email'

    EDIT_USER_LOGIN_LINK = By.XPATH, '//a[@class="edit_pseudonym_link"]'
    USER_LOGIN = By.XPATH, '//b[@class="unique_id"]'
    USER_LOGIN_INPUT = By.ID, 'pseudonym_unique_id'
    UPDATE_USER_LOGIN_BTN = By.XPATH, '//button[text()="Update Login"]'

    def activate_users_and_reset_email(self, users):
        for user in users:
            self.navigate_to(f'{utils.canvas_base_url()}/users/{user.canvas_id}')
            self.when_present(self.DEFAULT_EMAIL, utils.get_short_timeout())
            if self.element(self.DEFAULT_EMAIL).text == user.email_address:
                app.logger.info(f'User {user.uid} email already updated')
            else:
                app.logger.info(f'Resetting user {user.uid} email to {user.email}')
                self.wait_for_element_and_click(self.EDIT_USER_LINK)
                self.wait_for_element_clear_and_send_keys(self.USER_EMAIL_INPUT, user.email)
                self.wait_for_element_and_click(self.UPDATE_DETAILS_BTN)
                self.when_present(self.DEFAULT_EMAIL, utils.get_short_timeout())
            self.when_visible(self.USER_LOGIN, utils.get_short_timeout())
            if 'inactive' in self.element(self.USER_LOGIN).text:
                app.logger.info(f'Reactivating UID {user.uid}')
                self.wait_for_element_and_click(self.EDIT_USER_LOGIN_LINK)
                self.wait_for_element_clear_and_send_keys(self.USER_LOGIN_INPUT, user.uid)
                self.wait_for_element_and_click(self.UPDATE_USER_LOGIN_BTN)
                self.wait_for_text_in_element(self.USER_LOGIN, user.uid)

    # Site users table

    NO_USERS_MSG = By.XPATH, '//h2[text()="No people found"]'
    STUDENT_ENROLLMENT_ROW = By.XPATH, '//table[contains(@class, "roster")]/tbody/tr[contains(@class, "StudentEnrollment")]'
    USER_ROW = By.XPATH, '//tr[starts-with(@id, "user_")]'
    WAITLIST_ENROLLMENT_ROW = By.XPATH, '//table[contains(@class, "roster")]/tbody/tr[contains(@class, "Waitlist")]'

    @staticmethod
    def user_row_xpath(user):
        return f'//tr[contains(@id, "{user.canvas_id}")]'

    @staticmethod
    def user_row(user):
        return By.XPATH, f'//tr[contains(@id, "{user.canvas_id}")]'

    def wait_for_users(self, users):
        self.scroll_to_bottom()
        for user in users:
            app.logger.info(f'Waiting for user row with Canvas id {user.canvas_id}')
            self.when_present((By.XPATH, self.user_row_xpath(user)), utils.get_short_timeout())

    def wait_for_user(self, user):
        self.when_present(self.user_row(user), utils.get_short_timeout())

    def roster_user_sections(self, user):
        return self.el_text_if_exists((By.XPATH, f'{self.user_row_xpath(user)}/td[5]'))

    def roster_user_roles(self, user):
        return self.el_text_if_exists((By.XPATH, f'{self.user_row_xpath(user)}/td[6]'))

    def visible_instruction_modes(self):
        self.when_present(self.SECTION_LABEL, utils.get_medium_timeout())
        modes = [el.text.split('(')[-1].replace(')', '') for el in self.elements(self.SECTION_LABEL)]
        return list(set(modes))

    # Uses the Roles select on the page to determine how many of each role are present on the page
    def user_count_per_role(self, site, roles=None):
        self.load_users_page(site)
        self.wait_for_element_and_click(self.ENROLLMENT_ROLES_SELECT)
        roles = roles or CanvasSiteRoles.COURSE_ROLES
        count_per_role = []
        sel = Select(self.element(self.ENROLLMENT_ROLES_SELECT))
        opts = sel.options
        for role in roles:
            opt = next(filter(lambda el: el.text.startswith(role), opts))
            count = int(opt.text.split('(')[-1].replace(')', '')) if opt else 0
            count_per_role.append({
                'role': role,
                'count': count,
            })
        app.logger.info(f'User count per role: {count_per_role}')
        return count_per_role

    # Waits for the role counts on the Roles select to stabilize, suggesting the SIS import is done
    def wait_for_enrollment_import(self, site, roles=None, expected_count_per_role=None):
        current_count = self.user_count_per_role(site, roles)
        if expected_count_per_role and current_count == expected_count_per_role:
            app.logger.info('Current enrollment counts match expectations')
        else:
            tries = 0
            max_tries = 10
            while tries <= max_tries:
                try:
                    tries = + 1
                    starting_count = current_count
                    time.sleep(utils.get_short_timeout())
                    current_count = self.user_count_per_role(site)
                    assert current_count == starting_count
                    return current_count
                except AssertionError:
                    if tries == max_tries:
                        app.logger.info('Timed out waiting for enrollment import to finish')
                        raise

    # Attempts to load the full roster of site members, scrolling down to trigger lazy loading
    def wait_for_site_member_row_count(self, row_el_locators, expected_count):
        tries = 0
        max_tries = int(expected_count / 25)
        while tries <= max_tries:
            try:
                tries += 1
                els = []
                for loc in row_el_locators:
                    els.extend(self.elements(loc))
                count = len(els)
                if count >= expected_count:
                    app.logger.info('All expected rows are already present')
                    break
                else:
                    self.scroll_to_bottom()
                    time.sleep(3)
                    wait = 0
                    max_wait = utils.get_short_timeout()
                    while wait <= max_wait:
                        try:
                            wait += 1
                            time.sleep(1)
                            updated_els = []
                            for loc in row_el_locators:
                                updated_els.extend(self.elements(loc))
                            assert len(updated_els) > count
                            break
                        except AssertionError:
                            if wait == max_wait:
                                break
                    updated_els = []
                    for loc in row_el_locators:
                        updated_els.extend(self.elements(loc))
                    app.logger.info(f'Visible user count is now {len(updated_els)}')
                    assert len(updated_els) >= expected_count
                    break
            except AssertionError:
                if tries == max_tries:
                    app.logger.info('Failed to load all expected course users')
                    raise

    def load_all_students(self, site):
        roles = ['Student', 'Waitlist Student']
        counts = self.user_count_per_role(site, roles)
        ttl_count = counts[0]['count'] + counts[1]['count']
        app.logger.info(f'Trying to load {ttl_count} students and waitlisted students')
        self.when_present(self.USER_ROW, utils.get_short_timeout())
        self.scroll_to_bottom()
        if len(self.elements(self.USER_ROW)) >= ttl_count:
            app.logger.info('All users are visible')
        else:
            self.wait_for_site_member_row_count([self.USER_ROW], ttl_count)

    def visible_site_user_data(self, site, sections=None):
        visible_user_data = []
        sis_sec_codes = [f'{sec.course} {sec.label}' for sec in sections] if sections else []
        self.load_all_students(site)
        if sections:
            # Collect data only from given sections
            rows = []
            for sec in sections:
                rows.extend(r for r in self.elements(self.USER_ROW) if f'{sec.course} {sec.label}' in r.text)
        else:
            # Collect everybody
            rows = self.elements(self.USER_ROW)
        for row in rows:

            # User info
            visible_canvas_id = row.get_dom_attribute('id').replace('user_', '')
            row_xpath = f'//tr[contains(@id, "user_{visible_canvas_id}")]'
            visible_uid = self.el_text_if_exists((By.XPATH, f'{row_xpath}//td[3]'), 'inactive-')
            visible_sid = self.el_text_if_exists((By.XPATH, f'{row_xpath}//td[4]'))
            visible_user = Person({
                'uid': visible_uid,
                'canvas_id': visible_canvas_id,
                'sid': visible_sid,
            })

            # User section info
            visible_section_codes = self.els_text_if_exist((By.XPATH, f'{row_xpath}//td[5]/div'))
            if sections:
                # If looking for specific sections, toss out other sections the user is in
                for sec_code in visible_section_codes:
                    if sec_code not in sis_sec_codes:
                        visible_section_codes.remove(sec_code)
            for idx, section_code in enumerate(visible_section_codes):
                if site.sections:
                    sec = next(filter(lambda s: f'{s.course} {s.label}' == section_code, site.sections))
                else:
                    sec = None

                # User section role info
                primary_roles = ['Teacher', 'TA', 'Student']
                other_roles = list(set(CanvasSiteRoles.COURSE_ROLES) - set(primary_roles))
                visible_roles = self.els_text_if_exist((By.XPATH, f'{row_xpath}//td[6]/div'))
                role = visible_roles[idx].strip()
                if role in primary_roles:
                    role = role.lower()
                elif role not in other_roles:
                    app.logger.info(f'User in users table has unrecognized role {role}')
                    role = None
                visible_user.role = role

                app.logger.info(f'Canvas id {visible_canvas_id}, UID {visible_uid}, role {role}')
                visible_user_data.append({
                    'user': visible_user,
                    'section_id': (sec and sec.section_id),
                })
        return visible_user_data

    def visible_student_enrollments(self, site, sis_sections):
        visible_enrollments = []
        visible_site_user_data = self.visible_site_user_data(site, sis_sections)
        # Match the visible enrollment in Canvas to a SIS enrollment
        for user_data in visible_site_user_data:
            for section in sis_sections:
                if section.section_id == user_data['section_id']:
                    for enrollment in section.enrollments:
                        if enrollment.student.uid == user_data['user'].uid:
                            if enrollment.student.last_name and user_data['user'].role in ['student', 'Waitlist Student']:
                                enrollment.student.canvas_id = user_data['user'].canvas_id
                                enrollment.student.role = user_data['user'].role
                                visible_enrollments.append(enrollment)
        return visible_enrollments

    def visible_uids_with_role_and_section_id(self, site):
        users_with_sections = self.visible_site_user_data(site)
        user_data = []
        for u_w_s in users_with_sections:
            data = {
                'uid': u_w_s['user'].uid,
                'role': (u_w_s['user'].role and u_w_s['user'].role.lower()),
                'section_id': u_w_s['section_id'],
            }
            if data not in user_data:
                user_data.append(data)
        user_data.sort(key=lambda ud: [ud['uid'], ud['section_id']])
        return user_data
