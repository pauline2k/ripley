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

import pytest
from teena.config.teena_test_config import TeenaTestConfig
from teena.models.ripley_job import RipleyJobs
from teena.models.ripley_tool import RipleyTools
from teena.test_utils import utils

test = TeenaTestConfig()
site = test.welcome_email()
email_subj = f'Welcome Email {test.test_id}'
email_body = 'Teena welcomes you'
teacher = next(filter(lambda u: u.role == 'Teacher', site.manual_members))
student_1 = next(filter(lambda u: u.role == 'Student', site.manual_members))
student_2 = next(filter(lambda u: u.role == 'Waitlist Student', site.manual_members))


@pytest.mark.usefixtures('page_objects')
class TestWelcomeEmailCreation:

    def test_setup(self):
        self.canvas_page.log_in(self.cal_net_page, test.admin.username, utils.get_admin_password())
        self.canvas_page.add_ripley_tools([t.value for t in RipleyTools])
        self.canvas_page.set_canvas_ids(site.manual_members)
        self.canvas_page.create_ripley_mailing_list_site(site, members=[teacher, student_1])
        self.canvas_page.masquerade_as(student_1, site)
        self.canvas_page.masquerade_as(teacher, site)

    def test_create_list(self):
        self.mailing_list_page.load_embedded_tool(site)
        self.mailing_list_page.create_list()

    def test_link_to_more_information(self):
        title = 'IT - How do I send a welcome email to newly enrolled students with the bCourses Mailing List tool?'
        assert self.mailing_list_page.is_external_link_valid(self.mailing_list_page.WELCOME_EMAIL_LINK, title,
                                                             switch_to_canvas_iframe=True)

    def test_subject_and_body_required(self):
        assert not self.mailing_list_page.is_el_enabled(self.mailing_list_page.EMAIL_SAVE_BUTTON)

    def test_disabled_activation_toggle(self):
        assert not self.mailing_list_page.is_el_enabled(self.mailing_list_page.EMAIL_ACTIVATION_TOGGLE)

    def test_create_email(self):
        self.mailing_list_page.enter_email_subject(email_subj)
        self.mailing_list_page.enter_email_body(email_body)
        self.mailing_list_page.click_save_email_button()
        utils.assert_equivalence(self.mailing_list_page.el_text_if_exists(self.mailing_list_page.EMAIL_SUBJECT),
                                 email_subj)
        utils.assert_equivalence(self.mailing_list_page.el_text_if_exists(self.mailing_list_page.EMAIL_BODY),
                                 email_body)

    def test_email_paused_by_default(self):
        assert self.mailing_list_page.is_present(self.mailing_list_page.EMAIL_PAUSED_MSG)

    def test_edit_email_but_cancel(self):
        self.mailing_list_page.click_edit_email_button()
        self.mailing_list_page.enter_email_subject(f'{email_subj} - edited')
        self.mailing_list_page.enter_email_body(f'{email_body} - edited')
        self.mailing_list_page.click_cancel_edit_button()
        utils.assert_equivalence(self.mailing_list_page.el_text_if_exists(self.mailing_list_page.EMAIL_SUBJECT),
                                 email_subj)
        utils.assert_equivalence(self.mailing_list_page.el_text_if_exists(self.mailing_list_page.EMAIL_BODY),
                                 email_body)

    def test_edit_email_and_save(self):
        self.mailing_list_page.click_edit_email_button()
        self.mailing_list_page.enter_email_subject(f'{email_subj} - edited')
        self.mailing_list_page.enter_email_body(f'{email_body} - edited')
        self.mailing_list_page.click_save_email_button()
        utils.assert_equivalence(self.mailing_list_page.el_text_if_exists(self.mailing_list_page.EMAIL_SUBJECT),
                                 f'{email_subj} - edited')
        utils.assert_equivalence(self.mailing_list_page.el_text_if_exists(self.mailing_list_page.EMAIL_BODY),
                                 f'{email_body} - edited')


@pytest.mark.usefixtures('page_objects')
class TestWelcomeEmailActivation:

    def test_activate_email(self):
        self.mailing_list_page.click_activation_toggle()

    def test_refresh_mailing_list(self):
        self.canvas_page.stop_masquerading()
        self.splash_page.load_page()
        self.admin_page.run_job(RipleyJobs.REFRESH_MAILING_LIST.value)

    def test_membership_updated(self):
        self.canvas_page.masquerade_as(teacher)
        self.mailing_list_page.load_embedded_tool(site)
        csv = self.mailing_list_page.download_csv(self.mailing_list_page.EMAIL_LOG_DOWNLOAD_BUTTON)
        actual = [r['Email address'] for r in csv]
        actual.sort()
        expected = [m.email for m in [teacher, student_1]]
        expected.sort()
        utils.assert_equivalence(actual, expected)

    def test_email_sent(self):
        csv = self.mailing_list_page.download_csv(self.mailing_list_page.EMAIL_LOG_DOWNLOAD_BUTTON)
        actual_sent = len([r['Message sent'] for r in csv if r['Message sent']])
        utils.assert_equivalence(actual_sent, 2)

    def test_pause_activation(self):
        self.mailing_list_page.click_activation_toggle()

    def test_add_student_enrollment(self):
        self.canvas_page.stop_masquerading()
        self.canvas_page.add_users(site, [student_2])
        self.canvas_page.masquerade_as(student_2, site)

    def test_refresh_mailing_list_again(self):
        self.canvas_page.stop_masquerading()
        self.splash_page.load_page()
        self.admin_page.run_job(RipleyJobs.REFRESH_MAILING_LIST.value)

    def test_membership_updated_again(self):
        self.canvas_page.masquerade_as(teacher)
        self.mailing_list_page.load_embedded_tool(site)
        csv = self.mailing_list_page.download_csv(self.mailing_list_page.EMAIL_LOG_DOWNLOAD_BUTTON)
        actual_emails = [e['Email address'] for e in csv]
        actual_emails.sort()
        expected_emails = [m.email for m in [teacher, student_1, student_2]]
        expected_emails.sort()
        utils.assert_equivalence(actual_emails, expected_emails)

    def test_no_new_email_sent(self):
        csv = self.mailing_list_page.download_csv(self.mailing_list_page.EMAIL_LOG_DOWNLOAD_BUTTON)
        actual_sent = len([r['Message sent'] for r in csv if r['Message sent']])
        utils.assert_equivalence(actual_sent, 2)

    def test_resume_activation(self):
        self.mailing_list_page.click_activation_toggle()

    def test_refresh_mailing_list_yet_again(self):
        self.canvas_page.stop_masquerading()
        self.splash_page.load_page()
        self.admin_page.run_job(RipleyJobs.REFRESH_MAILING_LIST.value)

    def test_new_email_sent(self):
        self.canvas_page.masquerade_as(teacher)
        self.mailing_list_page.load_embedded_tool(site)
        csv = self.mailing_list_page.download_csv(self.mailing_list_page.EMAIL_LOG_DOWNLOAD_BUTTON)
        actual_sent = len([s['Message sent'] for s in csv if s['Message sent']])
        utils.assert_equivalence(actual_sent, 3)
