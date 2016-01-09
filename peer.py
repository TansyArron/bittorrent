import socket
from asyncio import get_event_loop, coroutine

class Peer():
	'''	Handles peer connections and related information.

	State interactions and listening for and sending messages.

	MESSAGES:

	keep alive: <len=0000>,
	choke: <len=0001><id=0>, 
	unchoke: <len=0001><id=1>, 
	interested: <len=0001><id=2>, 
	not interested: <len=0001><id=3>, 
	have: <len=0005><id=4><piece index>, 
	bitfield: <len=0001+X><id=5><bitfield>, 
	request: <len=0013><id=6><index><begin><length>, 
	piece: <len=0009+X><id=7><index><begin><block>, 
	cancel: <len=0013><id=8><index><begin><length>, 
	port: <len=0003><id=9><listen-port>
	
	'''	
	def __init__(self, ip, port, torrent_downloader):
		self.IP = ip
		self.port = port
		self.torrent_downloader = torrent_downloader
		self.torrent = torrent_downloader.torrent
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connected = False
		self.handshake_bytes = None
		self.state = {
				'am_choking' : True,
				'am_interested' : False,
				'peer_choking' : True,
				'peer_interested' : False,
		}
		self.message_bytes = None
		self.buffer = b''
		self.io_loop = get_event_loop()
		self.current_piece = b''
		self.piece_length = self.torrent.piece_length

	@coroutine
	def connect(self, message):
		self.message = message
		self.sock.setblocking(0)
		yield from self.io_loop.sock_connect(self.sock, (self.IP, self.port))
		yield from self.io_loop.sock_sendall(self.sock, message)
		while len(self.buffer) < 68:
			message_bytes = yield from self.io_loop.sock_recv(self.sock, 4096)
			if not message_bytes:
				raise Exception("Socket closed unexpectedly while receiving hanshake")
			self.buffer += message_bytes
		self.torrent_downloader.message_handler.check_handshake(self, self.buffer[:68])

	@coroutine
	def listen(self):
		''' Listen for messages from socket
		'''
		while self.connected:
			self.dispatch_messages_from_buffer()
			message_bytes = yield from self.io_loop.sock_recv(self.sock, 4096)
			if not message_bytes:
				raise Exception("Socket closed unexpectedly while receiving message")
				self.sock.close
				self.connected = False
			self.buffer += message_bytes

	def dispatch_messages_from_buffer(self):
		''' First four bytes of each message are an indication of length. 
			Wait until full message has been recieved and then send relevent
			bytes to dispatch_message. If length is 0000, message is "keep alive"
		'''
		while True:
			if len(self.buffer) >= 4:
				message_length = int.from_bytes(self.buffer[:4], byteorder='big')
				if message_length == 0:
					print("KEEP ALIVE")
					self.buffer = self.buffer[4:]
				elif len(self.buffer[4:]) >= message_length:
					message = self.buffer[4:message_length+4]
					self.torrent_downloader.message_handler.dispatch_message(self, message)
					self.buffer = self.buffer[message_length+4:]
				else:
					return self.buffer	
			else:
				return self.buffer

