#!/bin/bash
sudo systemctl daemon-reload
sudo systemctl enable xenomorph.service
sudo systemctl restart xenomorph.service
