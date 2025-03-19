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
from selenium.webdriver.common.by import By
from teena.pages.ripley.ripley_pages import RipleyPages
from teena.test_utils import utils


class AdminPage(RipleyPages):

    @staticmethod
    def run_job_button(job):
        return By.ID, f'run-job-{job.key}'

    @staticmethod
    def job_most_recent_locator(job):
        return (By.XPATH,
                f'//h2[contains(., "Job History")]/../../following-sibling::div//tbody/tr[contains(., "{job.key}")][1]')

    def job_success(self, job):
        return self.is_present((By.XPATH, f'{self.job_most_recent_locator(job)}//i[contains(@class, "success")]'))

    def job_failure(self, job):
        return self.is_present((By.XPATH, f'{self.job_most_recent_locator(job)}//i[contains(@class, "error")]'))

    def run_job(self, job):
        app.logger.info(f'Running {job.name}')
        time.sleep(3)
        cas_btn = By.ID, 'cas-auth-submit-button'
        if self.is_present(cas_btn):
            self.element(cas_btn).click()
        self.wait_for_element_and_click(self.run_job_button(job))
        self.wait_for_job_to_finish(job)

    def wait_for_job_to_finish(self, job):
        tries = utils.get_medium_timeout()
        app.logger.info(f'Waiting for {job.name} to finish')
        while tries > 0:
            try:
                tries -= 1
                self.when_present(self.job_success(job), 3)
                break
            except TimeoutError:
                if tries == 0:
                    app.logger.info('Timed out waiting for job to succeed')
                    raise
                elif self.is_present(self.job_failure(job)):
                    app.logger.info('Job failed')
                    raise
                else:
                    app.logger.info('Job still running')
