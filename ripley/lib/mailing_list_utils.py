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


def send_welcome_emails():
    # TODO:
    #   payload = {
    #     'from' => 'bCourses Mailing Lists <no-reply@bcourses-mail.berkeley.edu>',
    #     'subject' => self.welcome_email_subject,
    #     'html' => self.welcome_email_body,
    #     'text' => text_format_email(self.welcome_email_body)
    #   }
    #
    #   unwelcomed_members = active_members.where(welcomed_at: nil)
    #   population_results[:welcome_emails][:total] = unwelcomed_members.count
    #   unwelcomed_members.each_slice(1000) do |unwelcomed_slice|
    #     recipient_fields = MailingLists::OutgoingMessage.get_recipient_fields unwelcomed_slice
    #     response = Mailgun::SendMessage.new.post payload.merge(recipient_fields)
    #     break unless response.try(:[], :response).try(:[], :sending)
    #     ActiveRecord::Base.transaction do
    #       unwelcomed_slice.each { |member| member.update(welcomed_at: DateTime.now) }
    #     end
    #     population_results[:welcome_emails][:success] += unwelcomed_slice.count
    #   end
    pass
