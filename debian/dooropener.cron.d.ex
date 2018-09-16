#
# Regular cron jobs for the dooropener package
#
0 4	* * *	root	[ -x /usr/bin/dooropener_maintenance ] && /usr/bin/dooropener_maintenance
