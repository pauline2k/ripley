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
"${PYTHONPATH}/python" -c "import os; from ripley.lib.canvas_lti import configure_tools_from_current_host; \
    os.environ['RIPLEY_ENV'] = '${RIPLEY_ENV}'; \
    os.environ['RIPLEY_LOCAL_CONFIGS'] = '${RIPLEY_LOCAL_CONFIGS}'; \
    configure_tools_from_current_host()" | $LOGIT
