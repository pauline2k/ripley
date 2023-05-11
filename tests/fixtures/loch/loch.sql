DROP SCHEMA IF EXISTS sis_data cascade;

CREATE SCHEMA sis_data;

CREATE TABLE sis_data.basic_attributes
(
    ldap_uid VARCHAR,
    sid VARCHAR,
    first_name VARCHAR,
    last_name VARCHAR,
    email_address VARCHAR,
    affiliations VARCHAR,
    person_type VARCHAR
);

INSERT INTO sis_data.basic_attributes
(ldap_uid, sid, first_name, last_name, email_address, affiliations, person_type)
VALUES
('10000', NULL, 'Ellen', 'Ripley', 'ellen.ripley@berkeley.edu', 'EMPLOYEE-TYPE-ACADEMIC', 'S'),
('10001', NULL, 'Dallas', '👨‍✈️', 'dallas@berkeley.edu', 'EMPLOYEE-TYPE-STAFF', 'S'),
('20000', NULL, 'Joan', 'Lambert', 'joan.lambert@berkeley.edu', 'STUDENT-TYPE-REGISTERED', 'S'),
('30000', NULL, 'Ash', '🤖', 'synthetic.ash@berkeley.edu', 'STUDENT-TYPE-NOT REGISTERED', 'S'),
('40000', NULL, 'XO', 'Kane', 'xo.kane@berkeley.edu', 'STUDENT-TYPE-REGISTERED', 'S'),
('50000', NULL, 'Dennis', 'Parker', 'dennis.parker@berkeley.edu', 'STUDENT-TYPE-REGISTERED', 'S'),
('60000', NULL, 'Samuel', 'Brett', 'sam.brett@berkeley.edu', 'STUDENT-TYPE-REGISTERED', 'S');

CREATE TABLE sis_data.sis_enrollments
(
    sis_term_id VARCHAR,
    sis_section_id VARCHAR,
    ldap_uid VARCHAR,
    sis_enrollment_status VARCHAR
);

INSERT INTO sis_data.sis_enrollments
(sis_term_id, sis_section_id, ldap_uid, sis_enrollment_status)
VALUES
('2232', '32936', '20000', 'E'),
('2232', '32936', '40000', 'E'),
('2232', '32937', '20000', 'E'),
('2232', '32937', '50000', 'E'),
('2232', '32937', '60000', 'W');

CREATE TABLE sis_data.sis_sections (
    sis_term_id VARCHAR,
    sis_section_id VARCHAR,
    is_primary BOOLEAN,
    sis_course_name VARCHAR,
    sis_course_title VARCHAR,
    sis_instruction_format VARCHAR,
    sis_section_num VARCHAR,
    allowed_units NUMERIC,
    cs_course_id VARCHAR,
    session_code VARCHAR,
    instruction_mode VARCHAR,
    instructor_uid VARCHAR,
    instructor_name VARCHAR,
    instructor_role_code VARCHAR,
    meeting_location VARCHAR,
    meeting_days VARCHAR,
    meeting_start_time VARCHAR,
    meeting_end_time VARCHAR,
    meeting_start_date VARCHAR,
    meeting_end_date VARCHAR
);

INSERT INTO sis_data.sis_sections
(sis_term_id, sis_section_id, is_primary, sis_course_name, sis_course_title, sis_instruction_format, sis_section_num, allowed_units, cs_course_id, session_code, instruction_mode, instructor_uid, instructor_name, instructor_role_code, meeting_location, meeting_days, meeting_start_time, meeting_end_time, meeting_start_date, meeting_end_date)
VALUES
('2232', '32936', TRUE, 'ANTHRO 189', 'Our Dogs, Ourselves: Encounters between the Human and the Non-Human', 'LEC', '001', NULL, '876543', 1, 'P', '', 'Fitzi Ritz', 'PI', NULL, NULL, NULL, NULL, NULL, NULL),
('2232', '32937', TRUE, 'ANTHRO 189', 'Our Dogs, Ourselves: Encounters between the Human and the Non-Human', 'LEC', '002', NULL, '876543', 1, 'P', '', 'Fitzi Ritz', 'PI', NULL, NULL, NULL, NULL, NULL, NULL),
('2228', '17275', TRUE, 'ANTHRO 197', 'Fieldwork', 'FLD', '001', NULL, '100726', 1, 'P', '', 'Fitzi Ritz', 'PI', NULL, NULL, NULL, NULL, NULL, NULL),
('2228', '17277', TRUE, 'ANTHRO 197', 'Fieldwork', 'FLD', '002', NULL, '100726', 1, 'P', '', 'Mufty Blauswater', 'PI', NULL, NULL, NULL, NULL, NULL, NULL),
('2232', '12345', TRUE, 'ASTRON 218', 'Stellar Dynamics and Galactic Structure', 'LEC', '001', NULL, '1234567', 1, 'P', '30000', 'Ash', 'PI', 'Sevastopol Station', 'SAMOWE', '09:00', '11:00', '2023-02-17', '2023-02-17'),
('2232', '12346', TRUE, 'ASTRON 218', 'Stellar Dynamics and Galactic Structure', 'LEC', '002', NULL, '1234567', 1, 'P', '30000', 'Ash', 'PI', 'Acheron LV 426', 'TUTH', '09:00', '13:30', '2023-01-17', '2023-05-05'),
('2228', '32290', TRUE, 'ASTRON C228', 'Extragalactic Astronomy and Cosmology', 'LEC', '001', NULL, '124009', 1, 'P', '30000', 'Ash', 'PI', NULL, NULL, NULL, NULL, NULL, NULL),
('2228', '32291', TRUE, 'ASTRON C228', 'Extragalactic Astronomy and Cosmology', 'LEC', '002', NULL, '124009', 1, 'P', '30000', 'Ash', 'PI', NULL, NULL, NULL, NULL, NULL, NULL);

DROP SCHEMA IF EXISTS terms cascade;

CREATE SCHEMA terms;

CREATE TABLE terms.current_term_index
(
    current_term_name VARCHAR NOT NULL,
    future_term_name VARCHAR NOT NULL
);

CREATE TABLE terms.term_definitions
(
    term_id VARCHAR(4) NOT NULL,
    term_name VARCHAR NOT NULL,
    term_begins DATE NOT NULL,
    term_ends DATE NOT NULL
);

INSERT INTO terms.current_term_index
(current_term_name, future_term_name)
VALUES
('Spring 2023', 'Summer 2023');

INSERT INTO terms.term_definitions
(term_id, term_name, term_begins, term_ends)
VALUES
('2102','Spring 2010','2010-01-12','2010-05-14'),
('2105','Summer 2010','2010-05-24','2010-08-13'),
('2108','Fall 2010','2010-08-19','2010-12-17'),
('2112','Spring 2011','2011-01-11','2011-05-13'),
('2115','Summer 2011','2011-05-23','2011-08-12'),
('2118','Fall 2011','2011-08-18','2011-12-16'),
('2122','Spring 2012','2012-01-10','2012-05-11'),
('2125','Summer 2012','2012-05-21','2012-08-10'),
('2128','Fall 2012','2012-08-16','2012-12-14'),
('2132','Spring 2013','2013-01-15','2013-05-17'),
('2135','Summer 2013','2013-05-28','2013-08-16'),
('2138','Fall 2013','2013-08-22','2013-12-20'),
('2142','Spring 2014','2014-01-14','2014-05-16'),
('2145','Summer 2014','2014-05-27','2014-08-15'),
('2148','Fall 2014','2014-08-21','2014-12-19'),
('2152','Spring 2015','2015-01-13','2015-05-15'),
('2155','Summer 2015','2015-05-26','2015-08-14'),
('2158','Fall 2015','2015-08-19','2015-12-18'),
('2162','Spring 2016','2016-01-12','2016-05-13'),
('2165','Summer 2016','2016-05-23','2016-08-12'),
('2168','Fall 2016','2016-08-17','2016-12-16'),
('2172','Spring 2017','2017-01-10','2017-05-12'),
('2175','Summer 2017','2017-05-22','2017-08-11'),
('2178','Fall 2017','2017-08-16','2017-12-15'),
('2182','Spring 2018','2018-01-09','2018-05-11'),
('2185','Summer 2018','2018-05-21','2018-08-10'),
('2188','Fall 2018','2018-08-15','2018-12-14'),
('2192','Spring 2019','2019-01-15','2019-05-17'),
('2195','Summer 2019','2019-05-28','2019-08-16'),
('2198','Fall 2019','2019-08-21','2019-12-20'),
('2202','Spring 2020','2020-01-14','2020-05-15'),
('2205','Summer 2020','2020-05-26','2020-08-14'),
('2208','Fall 2020','2020-08-19','2020-12-18'),
('2212','Spring 2021','2021-01-12','2021-05-14'),
('2215','Summer 2021','2021-05-24','2021-08-13'),
('2218','Fall 2021','2021-08-18','2021-12-17'),
('2222','Spring 2022','2022-01-11','2022-05-13'),
('2225','Summer 2022','2022-05-23','2022-08-12'),
('2228','Fall 2022','2022-08-17','2022-12-16'),
('2232','Spring 2023','2023-01-10','2023-05-12'),
('2235','Summer 2023','2023-05-22','2023-08-11'),
('2238','Fall 2023','2023-08-16','2023-12-15'),
('2242','Spring 2024','2024-01-09','2024-05-10'),
('2245','Summer 2024','2024-05-20','2024-08-09'),
('2248','Fall 2024','2024-08-21','2024-12-06'),
('2252','Spring 2025','2025-01-10','2025-05-01'),
('2255','Summer 2025','2025-05-26','2025-08-01'),
('2258','Fall 2025','2025-08-20','2025-12-12'),
('2262','Spring 2026','2026-01-13','2026-05-15'),
('2265','Summer 2026','2026-05-26','2026-08-14'),
('2268','Fall 2026','2026-08-19','2026-12-18'),
('2272','Spring 2027','2027-01-12','2027-05-14'),
('2275','Summer 2027','2027-05-24','2027-08-13'),
('2278','Fall 2027','2027-08-18','2027-12-17'),
('2282','Spring 2028','2028-01-11','2028-05-12'),
('2285','Summer 2028','2028-05-22','2028-08-11'),
('2288','Fall 2028','2028-08-16','2028-12-15'),
('2292','Spring 2029','2029-01-09','2029-05-11'),
('2295','Summer 2029','2029-05-21','2029-08-10');
