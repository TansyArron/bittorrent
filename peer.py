import socket
import sys
import asyncio

class Peer():
	def __init__(self, ip, port):
		self.IP = ip
		self.port = port
		self.messages = [] #choke, unchoke, interested etc
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.handshake_bytes = None
		self.pieces = ''

	@asyncio.coroutine
	def connect(self, message):
		self.message = message
		io_loop = asyncio.get_event_loop()
		self.sock.setblocking(0)
		yield from io_loop.sock_connect(self.sock, (self.IP, self.port))
		yield from io_loop.sock_sendall(self.sock, message)
		self.handshake_bytes = yield from io_loop.sock_recv(self.sock, 500)
		# print('self.handshake_bytes "{}"'.format(self.handshake_bytes))
		self.check_handshake()

	def check_handshake(self):
		if len(self.handshake_bytes) < 48 or self.handshake_bytes[28:48] != self.message[28:48]:
			self.sock.close()
			raise Exception('Peer returned invalid info_hash. Closing socket')
		elif len(self.handshake_bytes) > 68:
			self.peices = self.handshake_bytes[68:]

		
		
		
