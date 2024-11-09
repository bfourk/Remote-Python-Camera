from sys import argv

server = False # If we run in server mode (set below)
passwd = None

for arg in argv:
	if arg == "--server" or arg == "-s":
		server = True
	if arg == "--passwd" and len(argv) >= inc:
		passwd = argv[inc+1]

if server:
	from rserver import run
	run(passwd)
else:
	from rclient import run
	run()