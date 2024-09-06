import tkinter
import socket
import rutil
from threading import Thread
from time import sleep
from PIL import Image, ImageTk, ImageFile
from io import BytesIO
from hashlib import sha512


clientImg = None # image from server
Closed = False
ClientSock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

IP = input("Input IP: ")
Port = rutil.GetPort("Input Port [23421]: ", 23421)

print("Connecting")

ClientSock.connect((IP,Port))
ClientSimple = rutil.SimpleSocket(ClientSock)

print("Connected to Host Successfully")

handshakeData = ClientSimple.recvall().decode()

if handshakeData[0] != "!":
	print("Handshake Failure")
	exit(1)

if handshakeData[1] == "1":
	print("Authentication Required")
	passwd = input("Input Password: ")
	ClientSimple.sendall(sha512(passwd.encode()).hexdigest())
	if ClientSimple.recvall().decode() == "0":
		print("Invalid Password")
		exit(1)
	print("Authentication Success")

print("Connected")
ClientSimple.sendall("!")

def recvImage():
	global clientImg
	img = ClientSimple.recvall()
	imgIO = BytesIO(img)
	try:
		clientImg = Image.open(imgIO)
	except:
		print("Bad image received, ignoring.")
	ClientSimple.sendall("!")

def ImageRecvLoop():
	while True:
		if Closed:
			break
		recvImage()
		sleep(1/30)

def onClose(a):
	global Closed
	if Closed:
		return
	Closed = True
	global ClientSimple
	print("Closing gracefully")
	ClientSimple.close()
	del ClientSimple
	exit(0)

def run():
	win = tkinter.Tk()
	win.geometry("1920x1080")
	win.title("Pi Camera")
	win.bind("<Destroy>", onClose)


	l = tkinter.Label(win)
	l.pack(side = "top",fill = "both")

	recvImage()
	ClientSimple.sendall("!")
	Thread(target = ImageRecvLoop, args = ()).start()

	while True:
		sleep(0.01)
		if Closed:
			break
		if clientImg == None:
			continue
		try:
			pimg = ImageTk.PhotoImage(clientImg.resize((win.winfo_width(),win.winfo_height())))
			l.configure(image=pimg)
			l.image = pimg
			win.update()
		except:
			exit(0)
