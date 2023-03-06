#!/bin/bash

# -------------------------------------------------------------------
#
# Copy config files from S3 to production-local.py. This
# script must be run on the target EC2 instance (eg, ripley-dev).
#
# -------------------------------------------------------------------

# Abort immediately if a command fails
set -e

echo; echo "Welcome!"; echo

if [ "$EUID" -ne 0 ]; then
  echo "Sorry, you must use 'sudo' to run this script."; echo
  exit 1
fi

local_app_config="/var/app/current/config/production-local.py"
local_lti_config="/var/app/current/config/lti-config.json"

if [ -e "${local_app_config}" ]; then
  eb_env=$(grep EB_ENVIRONMENT "${local_app_config}" | sed "s/^EB_ENVIRONMENT[ ]*=[ ]*'//" | sed "s/'[ ]*//")

  if [ -z "${eb_env}" ]; then
    echo "[ERROR] EB_ENVIRONMENT not found in ${local_app_config}. Please report the problem."; echo
    exit 1
  else
    echo "EB_ENVIRONMENT is '${eb_env}' according to ${local_app_config}"; echo
  fi

else
  echo "File not found: ${local_app_config}"; echo
  exit 1
fi

# Download from Amazon S3
app_config_location="s3://ripley-deploy-configs/ripley/${eb_env}.py"
lti_config_location="s3://ripley-deploy-configs/ripley/${eb_env}-lti-config.json"

echo "In five seconds, ${app_config_location} will be copied to ${local_app_config}
and ${lti_config_location} will be copied to ${local_lti_config}."; echo
echo "Use CTRL-C to abort..."; echo
sleep 5

AWS_REGION=us-west-2 aws s3 cp "${app_config_location}" "${local_app_config}"
chown webapp "${local_app_config}"
chmod 400 "${local_app_config}"

AWS_REGION=us-west-2 aws s3 cp "${lti_config_location}" "${local_lti_config}"
chown webapp "${local_lti_config}"
chmod 400 "${local_lti_config}"

# Add EB_ENVIRONMENT to new config file
printf "\nEB_ENVIRONMENT = '${eb_env}'\n\n" >> "${local_app_config}"

echo; echo "Done!"; echo
echo "Restart Ripley to pick up new configs. Have a nice day!"; echo

exit 0
