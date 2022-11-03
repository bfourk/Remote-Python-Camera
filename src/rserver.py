import cv2
import socket
import rutil
from threading import Thread
from pickle import dumps
from time import sleep


listenAddr = "0.0.0.0"
listenPort = 23421

# Do not edit the variables below

serverPassword = None
serverImage = None # image from webcam

"""
Constantly updates the "serverImage" variable with an image from the webcam
This is the picture that is sent to clients when requested
"""
def ServerImageLoop():
	global serverImage
	cam = cv2.VideoCapture(0)

	while True:
		s,frame = cam.read()
		if not s:
			print("ERROR: Failed to grab frame from camera, exiting")
			exit(1)
			break
		frame = cv2.imencode(".jpg",frame, [int(cv2.IMWRITE_JPEG_QUALITY), 50])[1].tobytes()
		serverImage = frame
		sleep(1/20) # 20 fps

def OnSocketConn(accepted):
	print("Client Connected")
	ClientSock = rutil.SimpleSocket(accepted)
	ClientSock.sendall("!{0}".format(0 if serverPassword == None else 1))

	if serverPassword != None:
		attemptedPassword = ClientSock.recvall().decode()
		if attemptedPassword == serverPassword:
			ClientSock.sendall("1")
		else:
			sleep(1)
			ClientSock.sendall("0")

	if ClientSock.recvall().decode() != "!":
		print("Handshake Failed")
		exit(1)

	print("Handshake Success")
	while True:
		ClientSock.sendall(serverImage)
		ClientSock.recvall() # wait for client response before sending another image
		sleep(1/20) # wait 1/20th of a second

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
	serverPassword = passwd
	Thread(target = ServerImageLoop, args = ()).start()
	ServerSocketLoop()
	exit(0)