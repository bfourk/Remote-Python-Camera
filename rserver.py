import cv2
import socket
import rutil
from threading import Thread
from time import sleep
from hashlib import sha512

Framerate = 20

listenAddr = "0.0.0.0"
listenPort = 23422

# Do not edit the variables below

serverPassword = None
serverImage = None # image from webcam

"""
Constantly updates the "serverImage" variable with an image from the webcam
This is the picture that is sent to clients when requested
"""
def ServerImageLoop():
	global serverImage
	cam = cv2.VideoCapture(1)

	while True:
		s,frame = cam.read()
		if not s:
			print("ERROR: Failed to grab frame from camera, exiting")
			exit(1)
			break
		frame = cv2.imencode(".jpg",frame, [int(cv2.IMWRITE_JPEG_QUALITY), 50])[1].tobytes()
		serverImage = frame
		sleep(1/Framerate) # 1/framerate

def OnSocketConn(accepted):
	print("Client Connected")
	ClientSock = rutil.SimpleSocket(accepted)
	ClientSock.sendall("!{0}".format(0 if serverPassword == None else 1))

	if serverPassword != None:
		attemptedPassword = ClientSock.recvall().decode()
		print(attemptedPassword)
		print(serverPassword)
		if attemptedPassword == serverPassword:
			ClientSock.sendall("1")
		else:
			sleep(1)
			ClientSock.sendall("0")
			ClientSock.close()
			return

	if ClientSock.recvall().decode() != "!":
		print("Handshake Failed")
		exit(1)

	print("Handshake Success")
	while True:
		try:
			ClientSock.sendall(serverImage)
			ClientSock.recvall() # wait for client response before sending another image
		except:
			print("Client disconnected")
			ClientSock.close()
			del ClientSock
			break

def ServerSocketLoop():
	ServerSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	ServerSocket.bind((listenAddr,listenPort))
	ServerSocket.listen(100)
	print("Started socket server at {0}:{1}".format(listenAddr,listenPort))
	while True:
		Accepted, _ = ServerSocket.accept()
		Thread(target = OnSocketConn, args = (Accepted,)).start()

def run(passwd):
	global serverPassword
	if passwd and len(passwd) != 0:
		serverPassword = sha512(str(passwd).encode()).hexdigest()
	Thread(target = ServerImageLoop, args = ()).start()
	ServerSocketLoop()
	exit(0)
