/*
 * Kill any running nscd process
 * Remote the nscd cache files
 * Start a new nscd process
 *
 * Marlon Dutra
 * Wed, 02 Mar 2011 18:32:30 -0300
 *
 * $Id: nscd-restart.c 4085 2011-03-03 16:53:04Z marlon $
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>

int main()
{
	if (geteuid() != 0)
	{
		printf("Only root can execute this program. Consider a setuid.\n");
		exit(1);
	}

	// Kill nscd
	system("killall nscd 2> /dev/null");
	sleep(1);
	system("killall -9 nscd 2> /dev/null");
	system("rm -f /var/cache/nscd/*");
	system("/etc/init.d/nscd stop");
	system("/etc/init.d/nscd start");

	if (system("pgrep -lx nscd") == 0)
	{
		printf("NSCD restarted\n");
	}
	else
	{
		printf("Looks like NSCD has not restarted :-(\n");
	}
}
