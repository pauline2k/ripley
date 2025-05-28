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
from teena.test_utils import ripley_utils
from teena.test_utils import utils

test = TeenaTestConfig()
test.official_sections()
site = test.course_site
course = test.course_site.course
add_delete_sections = [sec for sec in test.course_site.course.sections if not sec.include_in_site]
add_delete_instructors = ripley_utils.expected_instr_section_data(site, add_delete_sections)
add_delete_students = ripley_utils.expected_student_section_data(site, add_delete_sections)
roles = ['Teacher', 'Lead TA', 'TA', 'Student', 'Waitlist Student']


@pytest.mark.usefixtures('page_objects')
class TestLoadTool:

    def test_setup(self):
        self.canvas_page.log_in(self.cal_net_page, test.admin.username, utils.get_admin_password())
        self.canvas_page.configure_single_site(test)
        self.create_course_site_page.provision_course_site(site)
        self.canvas_page.publish_course_site(test.course_site)

    def test_official_sections_notice(self):
        self.canvas_page.masquerade_as(test.teachers[0])
        self.canvas_page.load_course_sections(site)
        self.canvas_page.expand_official_sections_notice()
        title = 'IT - How do I add or remove a section roster from my course site?'
        assert self.canvas_page.is_external_link_valid(self.canvas_page.OFFICIAL_SECTIONS_HELP_LINK, title)

    def test_initial_sections_count(self):
        self.official_sections_page.load_embedded_tool(test.teachers[0])
        self.official_sections_page.select_site_and_manage(site)
        utils.assert_equivalence(self.official_sections_page.static_secs_count(), len(site.sections))


@pytest.mark.usefixtures('page_objects')
@pytest.mark.parametrize(argnames='tc',
                         argvalues=[tc for tc in test.test_cases if tc.section.include_in_site],
                         ids=[tc.test_case_id for tc in test.test_cases if tc.section.include_in_site],
                         scope='class')
class TestStaticSectionsView:

    def test_course_code(self, tc):
        utils.assert_equivalence(self.official_sections_page.static_sec_course(tc.section), course.code)

    def test_section_label(self, tc):
        utils.assert_equivalence(self.official_sections_page.static_sec_label(tc.section), tc.section.label)

    def test_section_id(self, tc):
        utils.assert_equivalence(self.official_sections_page.static_sec_id(tc.section), tc.section.section_id)

    def test_section_schedules(self, tc):
        utils.assert_equivalence(self.official_sections_page.static_sec_schedules(tc.section), tc.section.schedules)

    def test_section_locations(self, tc):
        utils.assert_equivalence(self.official_sections_page.static_sec_locations(tc.section), tc.section.locations)

    def test_section_instructors(self, tc):
        utils.assert_equivalence(self.official_sections_page.static_sec_instructors(tc.section),
                                 self.official_sections_page.expected_instructors(tc.section))

    def test_no_delete_button(self, tc):
        assert not self.official_sections_page.is_present(self.official_sections_page.section_delete_button(tc.section))


@pytest.mark.usefixtures('page_objects')
@pytest.mark.parametrize(argnames='tc',
                         argvalues=[tc for tc in test.test_cases if tc.section.include_in_site],
                         ids=[tc.test_case_id for tc in test.test_cases if tc.section.include_in_site],
                         scope='class')
class TestCurrentSectionsView:

    def test_course_code(self, tc):
        if not self.official_sections_page.is_present(self.official_sections_page.available_sections_heading()):
            self.official_sections_page.click_edit_sections()
        utils.assert_equivalence(self.official_sections_page.current_sec_course(tc.section), course.code)

    def test_section_label(self, tc):
        utils.assert_equivalence(self.official_sections_page.current_sec_label(tc.section), tc.section.label)

    def test_section_id(self, tc):
        utils.assert_equivalence(self.official_sections_page.current_sec_id(tc.section), tc.section.section_id)

    def test_section_schedules(self, tc):
        utils.assert_equivalence(self.official_sections_page.current_sec_schedules(tc.section), tc.section.schedules)

    def test_section_locations(self, tc):
        utils.assert_equivalence(self.official_sections_page.current_sec_locations(tc.section), tc.section.locations)

    def test_section_instructors(self, tc):
        utils.assert_equivalence(self.official_sections_page.current_sec_instructors(tc.section),
                                 self.official_sections_page.expected_instructors(tc.section))

    def test_delete_button_present(self, tc):
        assert self.official_sections_page.is_present(self.official_sections_page.section_delete_button(tc.section))

    def test_add_button_not_present(self, tc):
        assert not self.official_sections_page.is_present(self.official_sections_page.section_add_button(tc.section))


@pytest.mark.usefixtures('page_objects')
@pytest.mark.parametrize(argnames='tc',
                         argvalues=[tc for tc in test.test_cases if not tc.section.include_in_site],
                         ids=[tc.test_case_id for tc in test.test_cases if not tc.section.include_in_site],
                         scope='class')
class TestAvailableSectionsView:

    def test_course_expanded(self, tc):
        if not self.official_sections_page.is_present(
                self.official_sections_page.available_sections_table(tc.course, tc.section)):
            self.official_sections_page.expand_available_course_sections(tc.course, tc.section)

    def test_course_code(self, tc):
        utils.assert_equivalence(self.official_sections_page.available_sec_course(tc.section), tc.course.code)

    def test_section_label(self, tc):
        utils.assert_equivalence(self.official_sections_page.available_sec_label(tc.section), tc.section.label)

    def test_section_id(self, tc):
        utils.assert_equivalence(self.official_sections_page.available_sec_id(tc.section), tc.section.section_id)

    def test_section_schedules(self, tc):
        utils.assert_equivalence(self.official_sections_page.available_sec_schedules(tc.section),
                                 tc.section.schedules)

    def test_section_locations(self, tc):
        utils.assert_equivalence(self.official_sections_page.available_sec_locations(tc.section),
                                 tc.section.locations)

    def test_section_instructors(self, tc):
        utils.assert_list_items_in_other_list(self.official_sections_page.expected_instructors(tc.section),
                                              self.official_sections_page.available_sec_instructors(tc.section))

    def test_add_button_present(self, tc):
        assert self.official_sections_page.is_present(self.official_sections_page.section_add_button(tc.section))


@pytest.mark.usefixtures('page_objects')
class TestAddSectionStagingAndUnstaging:

    def test_save_button_disabled(self):
        assert not self.official_sections_page.is_el_enabled(self.official_sections_page.SAVE_CHANGES_BUTTON)

    def test_add_section(self):
        self.official_sections_page.expand_available_course_sections(course, site.sections[0])
        self.official_sections_page.click_add_section(add_delete_sections[-1])
        assert self.official_sections_page.is_present(
            self.official_sections_page.current_sec_row(add_delete_sections[-1]))

    def test_add_button_hidden(self):
        assert not self.official_sections_page.is_present(
            self.official_sections_page.section_add_button(add_delete_sections[-1]))

    def test_section_added_msg(self):
        assert self.official_sections_page.is_present(
            self.official_sections_page.section_added_element(course, add_delete_sections[-1]))

    def test_undo_section_add(self):
        self.official_sections_page.click_undo_add_section(add_delete_sections[-1])
        assert not self.official_sections_page.is_present(
            self.official_sections_page.current_sec_row(add_delete_sections[-1]))

    def test_add_button_revealed(self):
        assert self.official_sections_page.is_present(
            self.official_sections_page.section_add_button(add_delete_sections[-1]))


@pytest.mark.usefixtures('page_objects')
class TestRemoveSectionStagingAndUnstaging:

    def test_remove_section(self):
        self.official_sections_page.click_delete_section(site.sections[0])
        assert not self.official_sections_page.is_present(
            self.official_sections_page.current_sec_row(site.sections[0]))

    def test_undo_delete_button_revealed(self):
        assert self.official_sections_page.is_present(
            self.official_sections_page.section_undo_delete_button(site.sections[0]))

    def test_undo_section_remove(self):
        self.official_sections_page.click_undo_delete_section(site.sections[0])
        assert self.official_sections_page.is_present(
            self.official_sections_page.current_sec_row(site.sections[0]))

    def test_remove_button_revealed(self):
        assert self.official_sections_page.is_present(
            self.official_sections_page.section_delete_button(site.sections[0]))


@pytest.mark.usefixtures('page_objects')
class TestAddSectionsSISImport:

    def test_add_sections(self):
        self.official_sections_page.load_embedded_tool(site.course.teachers[0])
        self.official_sections_page.select_site_and_manage(site)
        self.official_sections_page.click_edit_sections()
        self.official_sections_page.add_sections(add_delete_sections)
        site.sections.extend(add_delete_sections)

    def test_updating_msg(self):
        self.official_sections_page.when_present(self.official_sections_page.UPDATING_SECTIONS_MSG, utils.get_medium_timeout())

    def test_updated_msg(self):
        self.official_sections_page.when_present(self.official_sections_page.SECTIONS_UPDATED_MSG, utils.get_long_timeout())
        self.official_sections_page.close_section_update_success()

    def test_updated_section_rows(self):
        utils.assert_equivalence(self.official_sections_page.static_secs_count(), len(site.sections))
        for sec in add_delete_sections:
            assert self.official_sections_page.is_present(self.official_sections_page.static_sec_row(sec))

    def test_canvas_sections(self):
        canvas_secs = self.canvas_page.get_course_site_section_ccns(site)
        canvas_secs.sort()
        site_secs = [s.section_id for s in site.sections]
        site_secs.sort()
        utils.assert_equivalence(canvas_secs, site_secs)

    def test_canvas_users(self):
        self.canvas_page.wait_for_enrollment_import(site, roles)
        visible_users = self.canvas_page.visible_user_section_data(site)
        utils.assert_list_items_in_other_list(add_delete_instructors, visible_users)
        utils.assert_list_items_in_other_list(add_delete_students, visible_users)


@pytest.mark.usefixtures('page_objects')
class TestDeleteSectionsSISImport:

    def test_add_sections(self):
        self.official_sections_page.load_embedded_tool(site.course.teachers[0])
        self.official_sections_page.select_site_and_manage(site)
        self.official_sections_page.click_edit_sections()
        self.official_sections_page.delete_sections(add_delete_sections)
        site.sections = [s for s in site.sections if s not in add_delete_sections]

    def test_updating_msg(self):
        self.official_sections_page.when_present(self.official_sections_page.UPDATING_SECTIONS_MSG,
                                                 utils.get_medium_timeout())

    def test_updated_msg(self):
        self.official_sections_page.when_present(self.official_sections_page.SECTIONS_UPDATED_MSG, utils.get_long_timeout())
        self.official_sections_page.close_section_update_success()

    def test_updated_section_rows(self):
        utils.assert_equivalence(self.official_sections_page.static_secs_count(), len(site.sections))
        for sec in add_delete_sections:
            assert not self.official_sections_page.is_present(self.official_sections_page.static_sec_row(sec))

    def test_canvas_sections(self):
        canvas_secs = self.canvas_page.get_course_site_section_ccns(site)
        canvas_secs.sort()
        site_secs = [s.section_id for s in site.sections]
        site_secs.sort()
        utils.assert_equivalence(canvas_secs, site_secs)

    def test_canvas_users(self):
        self.canvas_page.wait_for_enrollment_import(site, roles)
        visible_users = self.canvas_page.visible_user_section_data(site)
        utils.assert_list_items_not_in_other_list(add_delete_instructors, visible_users)
        utils.assert_list_items_not_in_other_list(add_delete_students, visible_users)


@pytest.mark.usefixtures('page_objects')
class TestUserToolAccess:

    def test_add_users(self):
        users_to_add = [test.lead_ta, test.ta, test.designer, test.reader, test.observer, test.students[0],
                        test.wait_list_student]
        self.canvas_page.load_users_page(site)
        self.canvas_page.click_find_person_to_add()
        for user in users_to_add:
            self.add_user_page.search(user.uid, 'CalNet UID')
            self.add_user_page.add_user_by_uid(user, site.sections[0])

    def test_support_admin_has_read_only_access(self):
        self.canvas_page.masquerade_as(test.canvas_admin, site)
        self.official_sections_page.load_embedded_tool(test.canvas_admin)
        self.official_sections_page.enter_site_and_manage(site)
        self.official_sections_page.when_present(self.official_sections_page.STATIC_VIEW_SECTIONS_TABLE,
                                                 utils.get_medium_timeout())
        assert not self.official_sections_page.is_present(self.official_sections_page.EDIT_SECTIONS_BUTTON)

    def test_lead_ta_has_edit_access(self):
        self.canvas_page.masquerade_as(test.lead_ta, site)
        self.official_sections_page.load_embedded_tool(test.lead_ta)
        self.official_sections_page.select_site_and_manage(site)
        self.official_sections_page.click_edit_sections()

    def test_ta_has_read_only_access(self):
        self.canvas_page.masquerade_as(test.ta, site)
        self.official_sections_page.load_embedded_tool(test.ta)
        self.official_sections_page.select_site_and_manage(site)
        self.official_sections_page.when_present(self.official_sections_page.STATIC_VIEW_SECTIONS_TABLE,
                                                 utils.get_medium_timeout())
        assert not self.official_sections_page.is_present(self.official_sections_page.EDIT_SECTIONS_BUTTON)

    def test_designer_has_read_only_access(self):
        self.canvas_page.masquerade_as(test.designer, site)
        self.official_sections_page.load_embedded_tool(test.designer)
        self.official_sections_page.select_site_and_manage(site)
        self.official_sections_page.when_present(self.official_sections_page.STATIC_VIEW_SECTIONS_TABLE,
                                                 utils.get_medium_timeout())
        assert not self.official_sections_page.is_present(self.official_sections_page.EDIT_SECTIONS_BUTTON)

    def test_reader_has_no_access(self):
        self.canvas_page.masquerade_as(test.reader, site)
        self.official_sections_page.load_embedded_tool(test.reader)
        self.official_sections_page.when_present(self.official_sections_page.MANAGE_SECTIONS_LINK,
                                                 utils.get_short_timeout())
        assert not self.official_sections_page.is_el_enabled(self.official_sections_page.MANAGE_SECTIONS_LINK)

    def test_observer_has_no_access(self):
        self.canvas_page.masquerade_as(test.observer, site)
        self.official_sections_page.load_embedded_tool(test.observer)
        self.official_sections_page.when_present(self.official_sections_page.MANAGE_SECTIONS_LINK,
                                                 utils.get_short_timeout())
        assert not self.official_sections_page.is_el_enabled(self.official_sections_page.MANAGE_SECTIONS_LINK)

    def test_student_has_no_access(self):
        self.canvas_page.masquerade_as(test.students[0], site)
        self.official_sections_page.load_embedded_tool(test.students[0])
        self.official_sections_page.when_present(self.official_sections_page.MANAGE_SECTIONS_LINK,
                                                 utils.get_short_timeout())
        assert not self.official_sections_page.is_el_enabled(self.official_sections_page.MANAGE_SECTIONS_LINK)

    def test_waitlisted_student_has_no_access(self):
        self.canvas_page.masquerade_as(test.wait_list_student, site)
        self.official_sections_page.load_embedded_tool(test.wait_list_student)
        self.official_sections_page.when_present(self.official_sections_page.MANAGE_SECTIONS_LINK,
                                                 utils.get_short_timeout())
        assert not self.official_sections_page.is_el_enabled(self.official_sections_page.MANAGE_SECTIONS_LINK)


@pytest.mark.usefixtures('page_objects')
class TestSectionNameUpdates:

    def test_setup(self):
        self.canvas_page.stop_masquerading()
        self.canvas_page.set_course_sis_id(site)
        section_id = f'SEC:{course.term.code}-{add_delete_sections[0].section_id}'
        section_name = f'{course.code} FAKE LABEL'
        sis_import_rows = [
            ['section_id', 'course_id', 'name', 'status', 'start_date', 'end_date'],
            [section_id, site.course.sis_id, section_name, 'active', '', ''],
        ]
        csv = utils.create_csv(f'section-{site.course.code}.csv', sis_import_rows)
        self.canvas_page.upload_sis_imports([csv])

    def test_section_name_mismatch(self):
        self.canvas_page.masquerade_as(test.teachers[0])
        self.official_sections_page.load_embedded_tool(test.teachers[0])
        self.official_sections_page.select_site_and_manage(site)
        self.official_sections_page.click_edit_sections()
        self.official_sections_page.when_present(self.official_sections_page.SECTION_NAME_MSG, utils.get_short_timeout())

    def test_section_name_update(self):
        self.official_sections_page.click_update_section(add_delete_sections[0])
        self.official_sections_page.save_changes_and_wait_for_success()
        self.official_sections_page.click_edit_sections()
        self.official_sections_page.when_present(self.official_sections_page.CURRENT_SECTIONS_TABLE,
                                                 utils.get_short_timeout())
        assert not self.official_sections_page.is_present(self.official_sections_page.SECTION_NAME_MSG)
