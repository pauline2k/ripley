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

import os

import pytest
from ripley.factory import create_app
from teena.pages.cal_net_page import CalNetPage
from teena.pages.canvas.canvas_page import CanvasPage
from teena.pages.ripley.add_user_page import AddUserPage
from teena.pages.ripley.admin_page import AdminPage
from teena.pages.ripley.create_course_site_page import CreateCourseSitePage
from teena.pages.ripley.create_project_site_page import CreateProjectSitePage
from teena.pages.ripley.e_grades_page import EGradesPage
from teena.pages.ripley.grade_distribution_page import GradeDistributionPage
from teena.pages.ripley.mailing_list_page import MailingListPage
from teena.pages.ripley.mailing_lists_page import MailingListsPage
from teena.pages.ripley.official_sections_page import OfficialSectionsPage
from teena.pages.ripley.roster_photos_page import RosterPhotosPage
from teena.pages.ripley.site_creation_page import SiteCreationPage
from teena.pages.ripley.splash_page import SplashPage
from teena.test_utils.webdriver_manager import WebDriverManager


os.environ['RIPLEY_ENV'] = 'teena'  # noqa

_app = create_app()

ctx = _app.app_context()
ctx.push()


def pytest_addoption(parser):
    parser.addoption('--browser', action='store', default=_app.config['BROWSER'])
    parser.addoption('--headless', action='store')


@pytest.fixture(scope='session')
def page_objects(request):
    browser = request.config.getoption('--browser')
    headless = request.config.getoption('--headless')
    driver = WebDriverManager.launch_browser(browser=browser, headless=headless)

    # Define page objects

    add_user_page = AddUserPage(driver, headless)
    admin_page = AdminPage(driver, headless)
    cal_net_page = CalNetPage(driver, headless)
    canvas_page = CanvasPage(driver, headless)
    create_course_site_page = CreateCourseSitePage(driver, headless)
    create_project_site_page = CreateProjectSitePage(driver, headless)
    e_grades_page = EGradesPage(driver, headless)
    mailing_list_page = MailingListPage(driver, headless)
    mailing_lists_page = MailingListsPage(driver, headless)
    newt_page = GradeDistributionPage(driver, headless)
    official_sections_page = OfficialSectionsPage(driver, headless)
    roster_photos_page = RosterPhotosPage(driver, headless)
    site_creation_page = SiteCreationPage(driver, headless)
    splash_page = SplashPage(driver, headless)

    session = request.node
    try:
        for item in session.items:
            cls = item.getparent(pytest.Class)
            setattr(cls.obj, 'driver', driver)
            setattr(cls.obj, 'add_user_page', add_user_page)
            setattr(cls.obj, 'admin_page', admin_page)
            setattr(cls.obj, 'cal_net_page', cal_net_page)
            setattr(cls.obj, 'canvas_page', canvas_page)
            setattr(cls.obj, 'create_course_site_page', create_course_site_page)
            setattr(cls.obj, 'create_project_site_page', create_project_site_page)
            setattr(cls.obj, 'e_grades_page', e_grades_page)
            setattr(cls.obj, 'mailing_list_page', mailing_list_page)
            setattr(cls.obj, 'mailing_lists_page', mailing_lists_page)
            setattr(cls.obj, 'newt_page', newt_page)
            setattr(cls.obj, 'official_sections_page', official_sections_page)
            setattr(cls.obj, 'roster_photos_page', roster_photos_page)
            setattr(cls.obj, 'site_creation_page', site_creation_page)
            setattr(cls.obj, 'splash_page', splash_page)
        yield
    finally:
        WebDriverManager.quit_browser(driver)
