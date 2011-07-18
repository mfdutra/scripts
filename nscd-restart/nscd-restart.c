/*
 * Kill any running nscd process
 * Remote the nscd cache files
 * Start a new nscd process
 *
 * Marlon Dutra
 * Wed, 02 Mar 2011 18:32:30 -0300
 *
 * Copyright 2011 Marlon Dutra
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
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
