from sys import argv

server = False # if we run in server mode (set by the below for loop)
passwd = None

inc = 0
for arg in argv:
	if arg == "--server" or arg == "-s":
		server = True
	if arg == "--passwd" and len(argv) >= inc:
		passwd = argv[inc+1]
	inc += 1

if server:
	from rserver import run
	run(passwd)
else:
	from rclient import run
	run()