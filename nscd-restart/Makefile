
all: nscd-restart

nscd-restart: nscd-restart.c
	gcc -o nscd-restart nscd-restart.c

install: nscd-restart
	install -m 4755 nscd-restart /usr/local/sbin
