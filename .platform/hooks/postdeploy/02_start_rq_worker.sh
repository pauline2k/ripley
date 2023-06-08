#!/bin/bash
PYTHONPATH=$(/opt/elasticbeanstalk/bin/get-config environment -k PYTHONPATH)
sudo ${PYTHONPATH}/rq worker -c xenomorph
