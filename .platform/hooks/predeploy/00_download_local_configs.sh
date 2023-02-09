#!/bin/bash
PYTHONPATH='' aws s3 cp s3://ripley-deploy-configs/ripley/${EB_ENVIRONMENT}.py config/production-local.py
printf "\nEB_ENVIRONMENT = '${EB_ENVIRONMENT}'\n\n" >> config/production-local.py
chown webapp config/production-local.py
chmod 400 config/production-local.py

PYTHONPATH='' aws s3 cp s3://ripley-deploy-configs/ripley/lti_rsa config/lti_rsa
chown webapp config/lti_rsa
chmod 400 config/lti_rsa
