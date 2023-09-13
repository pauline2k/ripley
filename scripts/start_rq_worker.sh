#!/bin/bash

# Abort immediately if a command fails
set -e

if [ $(command -v /opt/elasticbeanstalk/bin/get-config) ]; then
  PYTHONPATH=$(/opt/elasticbeanstalk/bin/get-config environment -k PYTHONPATH)
  RIPLEY_ENV=$(/opt/elasticbeanstalk/bin/get-config environment -k RIPLEY_ENV)
  app_dir="/var/app/current"
  config_dir="/var/app/current/config"
else
  PYTHONPATH=$(which python | sed "s/\/python//")
  RIPLEY_ENV=development
  app_dir="."
  config_dir="config"
fi

export RIPLEY_ENV=${RIPLEY_ENV}
export RIPLEY_LOCAL_CONFIGS=${config_dir}

local_app_config="${config_dir}/${RIPLEY_ENV}-local.py"
default_app_config="${config_dir}/default.py"

cat ${local_app_config} ${default_app_config} > "${config_dir}/merged.py";
if [ -e "${config_dir}/merged.py" ]; then
  log_location=$(sudo grep -m 1 LOGGING_LOCATION "${config_dir}/merged.py" | sed "s/^LOGGING_LOCATION[ ]*=[ ]*'//" | sed "s/'[ ]*//")
  # Clean up
  rm "${config_dir}/merged.py";
else
  echo "File not found: ${config_dir}/merged.py"; echo
  exit 1
fi

echo "Starting worker routine..."; echo
"${PYTHONPATH}/python" ${app_dir}/xenomorph.py >> "${log_location}" 2>&1
