#!/bin/bash
sudo mv /tmp/ripley.conf /etc/httpd/conf.d/ripley.conf
sudo mv /tmp/ssl.conf /etc/httpd/conf.d/ssl.conf
sudo /bin/systemctl restart httpd.service
