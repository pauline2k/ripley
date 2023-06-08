#!/bin/bash

# Abort immediately if a command fails
set -e

local_app_config="/var/app/current/config/production-local.py"

if [ -e "${local_app_config}" ]; then
  redis_host=$(sudo grep REDIS_HOST "${local_app_config}" | sed "s/^REDIS_HOST[ ]*=[ ]*'//" | sed "s/'[ ]*//")
  redis_pw=$(sudo grep REDIS_PASSWORD "${local_app_config}" | sed "s/^REDIS_PASSWORD[ ]*=[ ]*'//" | sed "s/'[ ]*//")
  redis_port=$(sudo grep REDIS_PORT "${local_app_config}" | sed "s/^REDIS_PORT[ ]*=[ ]*'//" | sed "s/'[ ]*//")

  if [ -z "${redis_host}" ]; then
    echo "[ERROR] REDIS_HOST not found in ${local_app_config}. Please report the problem."; echo
    exit 1
  elif [ -z "${redis_pw}" ]; then
    echo "[ERROR] REDIS_PASSWORD not found in ${local_app_config}. Please report the problem."; echo
    exit 1
  elif [ -z "${redis_port}" ]; then
    redis_port='6379'
  else
    echo "REDIS_HOST is '${redis_host}' according to ${local_app_config}"; echo
  fi

else
  echo "File not found: ${local_app_config}"; echo
  exit 1
fi

PYTHONPATH=$(/opt/elasticbeanstalk/bin/get-config environment -k PYTHONPATH)
sudo ${PYTHONPATH}/rq worker -n xenomorph -u "rediss://default:${redis_pw}@${redis_host}:${redis_port}"
