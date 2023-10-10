#!/bin/bash

# Abort immediately if a command fails
set -e

if [ $(command -v /opt/elasticbeanstalk/bin/get-config) ]; then
  PYTHONPATH=$(/opt/elasticbeanstalk/bin/get-config environment -k PYTHONPATH)
  RIPLEY_ENV=$(/opt/elasticbeanstalk/bin/get-config environment -k RIPLEY_ENV)
  app_dir="/var/app/current"
else
  PYTHONPATH=$(which python | sed "s/\/python//")
  RIPLEY_ENV=development
  app_dir="."
fi

cd $app_dir

export RIPLEY_ENV=${RIPLEY_ENV}
export RIPLEY_LOCAL_CONFIGS="$PWD/config"

LOG=`date +"$PWD/ripley.log"`
LOGIT="tee -a $LOG"

echo | $LOGIT
echo "------------------------------------------" | $LOGIT
echo "`date`: About to run the LTI application configuration script..." | $LOGIT
"${PYTHONPATH}/python" "${app_dir}/scripts/configure_tools_from_current_host.py" | $LOGIT
