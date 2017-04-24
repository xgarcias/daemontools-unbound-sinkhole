# daemontools-unbound-sinkhole
DNS sinkhole using Unbound


Ansible role that installs a DNS sinkhole based on Unbound
to detect and stop known malicious or invasive advertising sites.

It uses daemontools (https://cr.yp.to/daemontools.html) to monitor
the service and a cron script that refreshes the blacklists every night.
