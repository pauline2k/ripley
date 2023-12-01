#!/bin/bash

# Abort immediately if a command fails
set -e

if [ "$EUID" -ne 0 ]; then
  echo "Sorry, you must use 'sudo' to run this script."; echo
  exit 1
fi

sudo tail -f /var/log/web.stdout.log \
  /var/app/current/ripley.log \
  /var/log/httpd/error_log \
  /var/log/httpd/access_log

exit 0
