#! /bin/bash
export $(grep -v '^#' .env | xargs)

# backup the /var/log/pidstats.log file to the backups/pidstats folder with a timestamped filename
echo "Copying the pidstats.log file to the backups/pidstats folder"
SSHPASS=$password rsync -avP --rsh="sshpass -e ssh -l root" $server_ip_address:/var/log/pidstats.log ./pidsis/data/pidstats_$(date +%Y-%m-%d_%H-%M-%S).log
