#!/bin/bash

# Abort immediately if a command fails
set -e

if [ $(command -v /opt/elasticbeanstalk/bin/get-config) ]; then
  PYTHONPATH=$(/opt/elasticbeanstalk/bin/get-config environment -k PYTHONPATH)
  RIPLEY_ENV=$(/opt/elasticbeanstalk/bin/get-config environment -k RIPLEY_ENV)
  config_dir="/var/app/current/config"
else
  PYTHONPATH=$(which python | sed "s/\/python//")
  RIPLEY_ENV=development
  config_dir="config"
fi


local_app_config="${config_dir}/${RIPLEY_ENV}-local.py"
default_app_config="${config_dir}/default.py"


cat ${local_app_config} ${default_app_config} > "${config_dir}/merged.py";
if [ -e "${config_dir}/merged.py" ]; then
  log_format=$(sudo grep -m 1 LOGGING_FORMAT "${config_dir}/merged.py" | sed "s/^LOGGING_FORMAT[ ]*=[ ]*'//" | sed "s/'[ ]*//")
  log_level=$(sudo grep -m 1 LOGGING_LEVEL "${config_dir}/merged.py" | sed "s/^LOGGING_LEVEL[ ]*=[ ]*logging.//" | sed "s/[ ]*//")
  log_location=$(sudo grep -m 1 LOGGING_LOCATION "${config_dir}/merged.py" | sed "s/^LOGGING_LOCATION[ ]*=[ ]*'//" | sed "s/'[ ]*//")
  redis_host=$(sudo grep -m 1 REDIS_HOST "${config_dir}/merged.py" | sed "s/^REDIS_HOST[ ]*=[ ]*'//" | sed "s/'[ ]*//")
  redis_pw=$(sudo grep -m 1 REDIS_PASSWORD "${config_dir}/merged.py" | sed "s/^REDIS_PASSWORD[ ]*=[ ]*'//" | sed "s/'[ ]*//")
  redis_port=$(sudo grep -m 1 REDIS_PORT "${config_dir}/merged.py" | sed "s/^REDIS_PORT[ ]*=[ ]*'//" | sed "s/'[ ]*//")

  if [ -z "${redis_host}" ]; then
    echo "[ERROR] REDIS_HOST not found in ${config_dir}/merged.py. Please report the problem."; echo
    exit 1
  fi

  if [ -z "${redis_port}" ]; then
    redis_port='6379'
  fi

  # Clean up
  rm "${config_dir}/merged.py";

else
  echo "File not found: ${config_dir}/merged.py"; echo
  exit 1
fi

if [ "${redis_pw}" ]; then
  redis_url="rediss://default:${redis_pw}@${redis_host}:${redis_port}"
else
  redis_url="redis://${redis_host}:${redis_port}"
fi

echo "Connecting to ${redis_host}:${redis_port}."; echo

attempt=0
until [ -z "$(sudo ps | grep rq:worker:xenomorph)" ];
do
  (( attempt++ ))
  if (( count <= 3 ))
  then
    echo "Stopping existing worker (attempt ${attempt} of 3)."; echo
    sudo ${PYTHONPATH}/python -c "from xenomorph import stop_workers; stop_workers('${redis_url}')" >> "${log_location}" 2>&1
    sleep 1
  else
    break
  fi
done

echo "Starting worker..."; echo
sudo ${PYTHONPATH}/python -c "from xenomorph import start_worker; start_worker('${redis_url}', '${log_format}', '${log_level}')" >> "${log_location}" 2>&1 &
sleep 1

cat <<'ascii_end'
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@                                                                 @@
@@    __   __ _____ _   _ ________  ____________________ _   _     @@
@@    \ \ / /|  ___| \ | |  _  |  \/  |  _  | ___ \ ___ \ | | |    @@
@@     \ V / | |__ |  \| | | | | .  . | | | | |_/ / |_/ / |_| |    @@
@@     /   \ |  __|| . ` | | | | |\/| | | | |    /|  __/|  _  |    @@
@@    / /^\ \| |___| |\  \ \_/ / |  | \ \_/ / |\ \| |   | | | |    @@
@@    \/   \/\____/\_| \_/\___/\_|  |_/\___/\_| \_\_|   \_| |_/    @@
@@                                                                 @@
@@          ___________  ___  _    _ _   _  ___________ _          @@
@@         /  ___| ___ \/ _ \| |  | | \ | ||  ___|  _  \ |         @@
@@         \ `--.| |_/ / /_\ \ |  | |  \| || |__ | | | | |         @@
@@          `--. \  __/|  _  | |/\| | . ` ||  __|| | | | |         @@
@@         /\__/ / |   | | | \  /\  / |\  || |___| |/ /|_|         @@
@@         \____/\_|   \_| |_/\/  \/\_| \_/\____/|___/ (_)         @@
@@                                                                 @@
@@                     ___--=--------___                           @@
@@                    /. \___\____   _, \_      /-\                @@
@@                   /. .  _______     __/=====@                   @@
@@                   \----/  |  / \______/      \-/                @@
@@               _/         _/ o \                                 @@
@@              / |    o   /  ___ \                                @@
@@             / /    o\\ |  / O \ /|      __-_                    @@
@@            |o|     o\\\   |  \ \ /__--o/o___-_                  @@
@@            | |      \\\-_  \____  ----  o___-                   @@
@@            |o|       \_ \     /\______-o\_-                     @@
@@            | \       _\ \  _/ / |                               @@
@@            \o \_   _/      __/ /                                @@
@@             \   \-/   _       /|_                               @@
@@              \_      / |   - \  |\                              @@
@@                \____/  \ | /  \   |\                            @@
@@                        | o |   | \ |                            @@
@@                        | | |    \ | \                           @@
@@                       / | /      \ \ \                          @@
@@                     /|  \o|\--\  /  o |\--\                     @@
@@                     \----------' \---------'                    @@
@@                                                                 @@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
ascii_end

echo; echo "Worker status:"
echo $(${PYTHONPATH}/rq info -W -u ${redis_url})
