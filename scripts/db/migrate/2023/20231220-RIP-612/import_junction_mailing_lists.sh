#!/bin/sh

# Abort immediately if a command fails
set -e

read -p "Enter Junction Postgres db connection string: postgresql://" junction_db

script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

if [ $(command -v /opt/elasticbeanstalk/bin/get-config) ]; then
  if [ "$EUID" -ne 0 ]; then
    echo "Sorry, you must use 'sudo' to run this script."; echo
    exit 1
  fi
  local_app_config="/var/app/current/config/production-local.py"
else
  local_app_config="${script_dir}/../../../../config/development-local.py"
fi

ripley_db=$(grep ^SQLALCHEMY_DATABASE_URI "${local_app_config}" | sed "s/^SQLALCHEMY_DATABASE_URI[ ]*=[ ]*'//" | sed "s/'[ ]*//")

echo
echo "In five seconds, mailing lists will be copied from postgresql://${junction_db} to ${ripley_db}"; echo
echo "Use CTRL-C to abort..."; echo
sleep 5

psql "postgresql://${junction_db}" <<EXPORT
\copy (select mailing_list_id::integer, email_address, can_send, first_name, last_name, created_at, deleted_at, updated_at, welcomed_at FROM canvas_site_mailing_list_members ORDER BY mailing_list_id) TO ${script_dir}/canvas_site_mailing_list_members.csv WITH CSV DELIMITER ','
\copy (select id, canvas_site_id::integer, canvas_site_name, list_name, members_count, populate_add_errors, populate_remove_errors, populated_at, state, type, welcome_email_active, welcome_email_body, welcome_email_subject, created_at, updated_at, substring(list_name FROM '^.+-(\w{4})(?:-\d{1})?$') AS list_name_suffix FROM canvas_site_mailing_lists ORDER BY id) TO ${script_dir}/canvas_site_mailing_lists.csv WITH CSV DELIMITER ','
EXPORT

psql ${ripley_db} <<IMPORT
CREATE TABLE temp_mailing_lists (
    id integer NOT NULL UNIQUE,
    canvas_site_id integer NOT NULL UNIQUE,
    canvas_site_name character varying(255),
    list_name character varying(255) UNIQUE,
    members_count integer,
    populate_add_errors integer,
    populate_remove_errors integer,
    populated_at timestamp with time zone,
    state character varying(255),
    type character varying(255),
    welcome_email_active boolean NOT NULL DEFAULT false,
    welcome_email_body text,
    welcome_email_subject text,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    list_name_suffix character varying(255)
);
\copy temp_mailing_lists (id, canvas_site_id, canvas_site_name, list_name, members_count, populate_add_errors, populate_remove_errors, populated_at, state, type, welcome_email_active, welcome_email_body, welcome_email_subject, created_at, updated_at, list_name_suffix) FROM ${script_dir}/canvas_site_mailing_lists.csv WITH CSV DELIMITER ','
CREATE TABLE temp_mailing_list_members (
    mailing_list_id integer NOT NULL,
    email_address character varying(255) NOT NULL,
    can_send boolean NOT NULL DEFAULT false,
    first_name character varying(255),
    last_name character varying(255),
    created_at timestamp WITH time zone NOT NULL,
    deleted_at timestamp WITH time zone,
    updated_at timestamp WITH time zone NOT NULL,
    welcomed_at timestamp WITH time zone
);
\copy temp_mailing_list_members (mailing_list_id, email_address, can_send, first_name, last_name, created_at, deleted_at, updated_at, welcomed_at) FROM ${script_dir}/canvas_site_mailing_list_members.csv WITH CSV DELIMITER ','

WITH tmp1 AS (
    SELECT list_name, substring(list_name FROM '^.+-(\w{4})(?:-\d{1})?$') AS list_name_suffix
    FROM temp_mailing_lists
),
tmp2 AS (
    SELECT list_name,
      CASE WHEN list_name_suffix = 'list' THEN NULL ELSE '2' || substr(list_name_suffix, 3) END AS shortened_year,
      CASE WHEN list_name_suffix = 'list' THEN NULL ELSE substr(list_name_suffix, 1, 2) END AS season
    FROM tmp1
),
tmp3 AS (
    SELECT list_name,
    shortened_year || (
      CASE WHEN season = 'fa' THEN '8'
           WHEN season = 'sp' THEN '2'
           WHEN season = 'su' THEN '5'
      ELSE NULL END
    ) AS term_id
    FROM tmp2
),
mailing_lists AS (
    INSERT INTO canvas_site_mailing_lists (canvas_site_id, canvas_site_name, list_name, members_count, populate_add_errors, populate_remove_errors, populated_at, state, type, welcome_email_active, welcome_email_body, welcome_email_subject, created_at, updated_at, term_id) (
        SELECT canvas_site_id, canvas_site_name, t1.list_name, members_count, populate_add_errors, populate_remove_errors, populated_at,
            state, type, welcome_email_active, welcome_email_body, welcome_email_subject, created_at, updated_at, t3.term_id::integer
        FROM temp_mailing_lists t1 JOIN tmp3 t3 ON t1.list_name = t3.list_name
    )
    RETURNING id, canvas_site_id
)
INSERT INTO canvas_site_mailing_list_members (mailing_list_id, email_address, can_send, first_name, last_name, created_at, deleted_at, updated_at, welcomed_at) (
    SELECT ml.id AS mailing_list_id, tm.email_address, tm.can_send, tm.first_name, tm.last_name, tm.created_at, tm.deleted_at, tm.updated_at, tm.welcomed_at
    FROM temp_mailing_lists tl
    JOIN mailing_lists ml ON ml.canvas_site_id = tl.canvas_site_id
    JOIN temp_mailing_list_members tm ON tm.mailing_list_id = tl.id
);
DROP TABLE temp_mailing_list_members;
DROP TABLE temp_mailing_lists;
IMPORT

rm "${script_dir}/canvas_site_mailing_list_members.csv"
rm "${script_dir}/canvas_site_mailing_lists.csv"
