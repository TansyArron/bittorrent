import socket
import sys

class Peer():
	def __init__(self, ip, port):
		self.IP = ip
		self.port = port
		self.messages = [] #choke, unchoke, interested etc
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def connect(self, message):
		self.sock.setblocking(0)
		# print('connecting to %s port %s' % (self.IP, self.port), file=sys.stderr)
		self.sock.connect((self.IP, self.port))
		try:
			# print('sending "%s"' % message, file=sys.stderr)
			self.sock.sendall(message)
			data = self.sock.recv(100)
			print('received "%s"' % data)
		finally:
			# print('closing socket', sys.stderr)
			self.sock.close()
		return data
