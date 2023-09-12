files:
    /etc/systemd/system/xenomorph.service:
        mode: "000755"
        owner: root
        group: root
        content: |
            [Unit]
            Description=Xenomorph RQ Worker
            After=network.target

            [Service]
            User=webapp
            Type=simple
            WorkingDirectory=/var/app/current
            Environment=LANG=en_US.UTF-8
            Environment=LC_ALL=en_US.UTF-8
            Environment=LC_LANG=en_US.UTF-8
            ExecStart=/var/app/current/scripts/start_rq_worker.sh
            ExecReload=/bin/kill -s HUP $MAINPID
            ExecStop=/bin/kill -s TERM $MAINPID
            PrivateTmp=true
            Restart=always

            [Install]
            WantedBy=multi-user.target
