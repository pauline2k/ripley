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

import ssl

import ldap3


SCHEMA_DICT = {
    'berkeleyEduAffiliations': 'affiliations',
    'berkeleyEduAlternateID': 'email',
    'berkeleyEduCSID': 'csid',
    'berkeleyEduStuID': 'sid',
    'berkeleyEduPrimaryDeptUnit': 'primary_dept_code',
    'departmentNumber': 'dept_code',
    'givenName': 'first_name',
    'sn': 'last_name',
    'uid': 'uid',
}

BATCH_QUERY_MAXIMUM = 100


def client(app):
    return Client(app)


class Client:

    def __init__(self, app):
        self.app = app
        self.host = app.config['LDAP_HOST']
        self.bind = app.config['LDAP_BIND']
        self.password = app.config['LDAP_PASSWORD']
        tls = ldap3.Tls(validate=ssl.CERT_REQUIRED)
        server = ldap3.Server(self.host, port=636, use_ssl=True, get_info=ldap3.ALL, tls=tls)
        self.server = server

    def connect(self):
        return ldap3.Connection(
            self.server,
            user=self.bind,
            password=self.password,
            auto_bind=ldap3.AUTO_BIND_TLS_BEFORE_BIND,
            client_strategy=ldap3.SAFE_SYNC,
        )

    def guests_modified_since(self, utc_datetime):
        timestamp = utc_datetime.strftime('%Y%m%d%H%M%SZ')
        search_filter = _ldap_search_filter(
            {
                'createtimestamp': [timestamp],
                'modifytimestamp': [timestamp],
            },
            search_base='guests',
            comparator='>=',
        )
        results = []
        with self.connect() as conn:
            try:
                results = self._search(conn, search_filter, use_fallback_mail=True)
            except Exception as e:
                self.app.logger.error('LDAP guest search query failed')
                self.app.logger.exception(e)
        return results

    def search_uids(self, uids, search_base=None, use_fallback_mail=False):
        all_out = []
        with self.connect() as conn:
            for i in range(0, len(uids), BATCH_QUERY_MAXIMUM):
                if len(uids) == 1:
                    self.app.logger.debug(f'Executing LDAP search (UID {uids[0]})')
                else:
                    self.app.logger.debug(f'Executing LDAP UID search ({i+1} to {min(len(uids), i+BATCH_QUERY_MAXIMUM)} of {len(uids)})')
                uids_batch = uids[i:i + BATCH_QUERY_MAXIMUM]
                try:
                    _filter = _ldap_search_filter({'uid': uids_batch}, search_base)
                    all_out += self._search(conn, _filter, use_fallback_mail=use_fallback_mail)
                except Exception as e:
                    self.app.logger.error('LDAP UID search query failed')
                    self.app.logger.exception(e)
        return all_out

    def _search(self, conn, search_filter, use_fallback_mail=False):
        status, result, response, _ = conn.search('dc=berkeley,dc=edu', search_filter, attributes=ldap3.ALL_ATTRIBUTES)
        all_attributes = []
        if response:
            for entry in response:
                attributes = _attributes_to_dict(entry, use_fallback_mail)
                if attributes:
                    all_attributes.append(attributes)
        return all_attributes


def _attributes_to_dict(entry, use_fallback_mail=False):
    if 'expired' in str(entry.get('dn', '')):
        return None

    out = dict.fromkeys(SCHEMA_DICT.values(), None)
    for attr in SCHEMA_DICT:
        if attr in entry.get('attributes', {}):
            out[SCHEMA_DICT[attr]] = _unwrap_attribute(entry, attr)

    if use_fallback_mail and not out['email'] and 'mail' in entry.get('attributes', {}):
        out['email'] = _unwrap_attribute(entry, 'mail')

    return out


def _unwrap_attribute(entry, attr):
    attr_value = entry['attributes'][attr]
    if type(attr_value) is list and attr != 'berkeleyEduAffiliations':
        if len(attr_value):
            return attr_value[0]
        else:
            return None
    else:
        return attr_value


def _ldap_search_filter(attributes, search_base, comparator='='):
    attribute_filters = []
    for attribute, values in attributes.items():
        for value in values:
            attribute_filters.append(f'({attribute}{comparator}{value})')
    if search_base == 'guests':
        ou_scope = '(ou=guests)'
    elif search_base == 'active':
        ou_scope = '(|(ou=people) (ou=guests))'
    else:
        ou_scope = ''
    return f"""(&
        (|{ ''.join(attribute_filters) })
        { ou_scope }
    )"""
