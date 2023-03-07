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

from ripley import db
from ripley.models.base import Base


class MailingListMembers(Base):
    __tablename__ = 'canvas_site_mailing_list_members'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    mailing_list_id = db.Column(db.Integer, db.ForeignKey('canvas_site_mailing_lists.id'), nullable=False)
    can_send = db.Column(db.Boolean, nullable=False)
    email_address = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    deleted_at = db.Column(db.DateTime)
    welcomed_at = db.Column(db.DateTime)

    def __init__(self, can_send, email_address, mailing_list_id, first_name=None, last_name=None):
        self.can_send = can_send
        self.email_address = email_address
        self.first_name = first_name
        self.last_name = last_name
        self.mailing_list_id = mailing_list_id

    @classmethod
    def create(cls, canvas_site_id, list_name=None):
        pass

    @classmethod
    def get_mailing_list_members(cls, mailing_list_id):
        return cls.query.filter_by(deleted_at=None, mailing_list_id=mailing_list_id).all()

    @classmethod
    def update_memberships(cls, course_users, list_members):
        # TODO:
        # # List members are keyed by email addresses; keep track of any needed removals in a separate set.
        # addresses_to_remove = list_members.select{ |k, v| v.deleted_at.nil? }.keys.to_set
        #
        # # Note UIDs for users with send permission, defined for now as having a teacher role in the course site,
        # # or an Owner or Maintainer role in a project site.
        # sender_uids = Set.new
        # course_users.each { |user| sender_uids << user['login_id'] if can_send_to_mailing_list?(user) }
        #
        # logger.info "Starting population of mailing list #{self.list_name} for course site #{self.canvas_site_id}."
        # initialize_population_results
        #
        # population_results[:initial_count] = list_members.count
        #
        # course_users.map{ |user| user['login_id'] }.each_slice(1000) do |uid_slice|
        #   User::BasicAttributes.attributes_for_uids(uid_slice).each do |user|
        #
        #     user[:can_send] = sender_uids.include?(user[:ldap_uid])
        #
        #     # In general we want to use official berkeley.edu email addresses sourced from User::BasicAttributes.
        #     # However, we may wish to override with Canvas-sourced email addresses for testing purposes.
        #     # Note that the course_users list will not include email addresses for any members with
        #     # "enrollment_state": "invited".
        #     user_address = case Settings.canvas_mailing_lists.preferred_email_address_source
        #       when 'ldapAlternateId'
        #         user[:official_bmail_address] || user[:email_address]
        #       when 'ldapMail'
        #         user[:email_address] || user[:official_bmail_address]
        #       when 'canvas'
        #         if (canvas_user = course_users.find { |course_user| course_user['login_id'] == user[:ldap_uid] })
        #           logger.info "Setting email address for UID #{user[:ldap_uid]} to Canvas-sourced address #{canvas_user['email']}"
        #           canvas_user['email']
        #         else
        #           user[:official_bmail_address] || user[:email_address]
        #         end
        #     end
        #
        #     if user_address
        #       user_address.downcase!
        #       addresses_to_remove.delete user_address
        #       if list_members.has_key? user_address
        #         # Address is in the list but deleted; reactivate with latest data.
        #         if list_members[user_address].deleted_at
        #           population_results[:add][:total] += 1
        #           logger.debug "Reactivating previously deleted address #{user_address}"
        #           if reactivate_member(list_members[user_address], user)
        #             population_results[:add][:success] += 1
        #           else
        #             population_results[:add][:failure] << user_address
        #           end
        #         # Address is in the list and active; check if any data needs updating.
        #         elsif update_required?(list_members[user_address], user)
        #           population_results[:update][:total] += 1
        #           logger.debug "Updating address #{user_address}"
        #           if update_member(list_members[user_address], user)
        #             population_results[:update][:success] += 1
        #           else
        #             population_results[:update][:failure] << user_address
        #           end
        #         end
        #       else
        #         # Address is not currently in the list; add it.
        #         population_results[:add][:total] += 1
        #         logger.debug "Adding address #{user_address}"
        #         if add_member(user_address, user[:first_name], user[:last_name], user[:can_send])
        #           population_results[:add][:success] += 1
        #         else
        #           population_results[:add][:failure] << user_address
        #         end
        #       end
        #     else
        #       logger.warn "No email address found for UID #{user[:ldap_uid]}"
        #     end
        #   end
        # end
        #
        # population_results[:remove][:total] = addresses_to_remove.count
        #
        # addresses_to_remove.each do |address|
        #   logger.debug "Removing address #{address}"
        #   if remove_member address
        #     population_results[:remove][:success] += 1
        #   else
        #     population_results[:remove][:failure] << address
        #   end
        # end
        #
        # log_population_results
        #
        # logger.info "Finished population of mailing list #{self.list_name}."
        # self.populate_add_errors = population_results[:add][:failure].count
        # self.populate_remove_errors = population_results[:remove][:failure].count
        # self.populated_at = DateTime.now
        # save
        pass

    def to_api_json(self):
        return {
            'id': self.id,
            'canSend': self.can_send,
            'createdAt': self.created_at,
            'deletedAt': self.deleted_at,
            'emailAddress': self.email_address,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'mailingListId': self.mailing_list_id,
            'updatedAt': self.updated_at,
            'welcomedAt': self.welcomed_at,
        }
