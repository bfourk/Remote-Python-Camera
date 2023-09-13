import zlib

# Compression

doCompression = True

def ZLibCompress(data):
	return zlib.compress(data)
def ZLibDecompress(data):
	return zlib.decompress(data)

# Conversions

def IntToByte(i):
	return i.to_bytes(4, "little")

def ByteToInt(b):
	return int.from_bytes(b, "little")

# Sockets

class SimpleSocket:
	sock = None
	def __init__(self, socket):
		self.sock = socket

	def sendall(self,data):
		if not self.sock:
			return
		if type(data) is str:
			data = data.encode()
		if data == None:
			print("Warn: Tried to send no data, ignoring")
			return
		if doCompression:
			data = ZLibCompress(data)
		try:
			self.sock.sendall(IntToByte(len(data))) # tell the other end how big our data is
			self.sock.sendall(data) # send data
		except:
			print("Exception on send")
			exit(1)

	def recvall(self):
		if not self.sock:
			return
		data = b""
		dataLength = ByteToInt(self.sock.recv(4)) # receive the (4 byte) integer
		while True:
			if dataLength-len(data) == 0:
				if doCompression:
					data = ZLibDecompress(data)
				return data
			try:
				recv = self.sock.recv(dataLength-len(data))
				data += recv
			except:
				print("Exception on data receive")
				exit(1)
	def close(self):
		self.sock.close()
		del self.sock

# Input Sanitization

def GetPort(txt, default):
	while True:
		nport = 0
		port = input(txt)

		if port == None or port == "":
			return default

		try:
			nport = int(port)
		except:
			print("Invalid port, input a number")
		finally:
			if nport < 1024 or nport > 65535:
				print("Invalid port, must be between 1024-65535")
			else:
				return nport