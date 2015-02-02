import socket
import sys
import asyncio

class Peer():
	'''	Is responisble for handling information about a peer. 
		Handles state interactions- interested, choking, connecting to
		peers, listening for and parsing and acting on messages sent by 
		the peer, and constructing and sending messages.
	'''
	def __init__(self, ip, port, number_of_pieces, pieces_changed_callback, check_piece_callback, start_listener_callback):
		self.IP = ip
		self.port = port
		# choke: <len=0001><id=0>, unchoke: <len=0001><id=1>, interested: <len=0001><id=2>, not interested: <len=0001><id=3>, have: <len=0005><id=4><piece index>, bitfield: <len=0001+X><id=5><bitfield>, request: <len=0013><id=6><index><begin><length>, piece: <len=0009+X><id=7><index><begin><block>, cancel: <len=0013><id=8><index><begin><length>, port: <len=0003><id=9><listen-port>
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connected = False
		self.handshake_bytes = None
		self.has_pieces = [False] * number_of_pieces
		self.state = {
				'am_choking' : True,
				'am_interested' : False,
				'peer_choking' : True,
				'peer_interested' : False,
		}
		self.message_bytes = None
		self.message_ID_to_func_name = {
			0: self.choke,
			1: self.unchoke,
			2: self.interested,
			3: self.not_interested,
			4: self.have,
			5: self.bitfield,
			6: self.request,
			7: self.piece,
			8: self.cancel, 
			9: self.port,
		}
		self.buffer = b''
		self.pieces_changed_callback = pieces_changed_callback
		self.check_piece_callback = check_piece_callback
		self.start_listener_callback = start_listener_callback
		self.io_loop = asyncio.get_event_loop()

	@asyncio.coroutine
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
		self.check_handshake(self.buffer[:68])

	def check_handshake(self, handshake_bytes):
		if handshake_bytes[28:48] != self.message[28:48]:
			self.sock.close()
			raise Exception('Peer returned invalid info_hash. Closing socket')	
			# TODO: remove peer from torrent.peer_list and manager.connected_peers
		else:
			self.connected = True
			self.io_loop.create_task(self.listen())
			self.buffer = self.buffer[68:]

	@asyncio.coroutine
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
					self.keep_alive()
					self.buffer = self.buffer[4:]
				elif len(self.buffer[4:]) >= message_length:
					message = self.buffer[4:message_length+4]
					self.dispatch_message(message)
					self.buffer = self.buffer[message_length+4:]
				else:
					return self.buffer	
			else:
				return self.buffer

	def dispatch_message(self, message_bytes):
		''' 
			Pass all messages to their appropriate functions.
		'''
		message_id = message_bytes[0]
		message_slice = message_bytes[1:]
		# print('RECIEVED MESSAGE TYPE:', self.message_ID_to_func_name[message_id])
		self.message_ID_to_func_name[message_id](message_slice)
	
	def keep_alive(self):
		print('KEEP ALIVE')# TODO: update time/state
		pass

	def choke(self, message_bytes):
		self.state['peer_choking'] = True 
			
	def unchoke(self, message_bytes):
		self.state['peer_choking'] = False
		
	def interested(self, message_bytes):
		self.state['peer_interested'] == True
			
	def not_interested(self, message_bytes):
		self.state['peer_interested'] == False
		
	def have(self, message_bytes):
		'''	Have message is the index of a piece the peer has. Updates
			peer.has_pieces.
		'''
		piece_index = int.from_bytes(message_bytes, byteorder='big')
		# print('PEER HAS PIECE AT INDEX:', piece_index)
		self.has_pieces[piece_index] = True
		
	def bitfield(self, message_bytes):
		''' formats each byte into binary and updates peer.has_pieces list
			appropriately.
		'''
		bitstring = ''.join('{0:08b}'.format(byte) for byte in message_bytes)
		self.has_pieces = [bool(int(c)) for c in bitstring]
		# print('PEER HAS PIECES:', self.has_pieces)
		self.pieces_changed_callback(self)
		
	def request(self, message_bytes):
		pass
		
	def piece(self, message_bytes):
		''' Piece message is constructed:
			<index><offset><piece bytes>
		'''
		piece_index = message_bytes[:4]
		piece_begins = message_bytes[4:8]
		piece = message_bytes[8:]
		print(piece)
		self.check_piece_callback(piece, piece_index, self)
	
		#piece: <len=0009+X><id=7><index><begin><block>,
	def cancel(self, message_bytes):
		pass
		#cancel: <len=0013><id=8><index><begin><length>,
	def port(self, message_bytes):
		pass
		#port: <len=0003><id=9><listen-port>

	def construct_message(self, message_id, payload_bytes=b''):
		'''messages in the protocol take the form of 
		<length prefix><message ID><payload>. The length prefix is a four byte 
		big-endian value. The message ID is a single decimal byte. 
		The payload is message dependent.
		'''
		# print('CONSTRUCTING MESSAGE')
		length_bytes = (1 + len(payload_bytes)).to_bytes(4, byteorder='big')
		message_id_bytes = message_id.to_bytes(1, byteorder='big')
		elements = [length_bytes, message_id_bytes, payload_bytes]
		message_bytes = b''.join(elements)
		return message_bytes

	@asyncio.coroutine
	def send_message(self, message_id, payload_bytes=b''):
		''' Send message and update self.state if necessary
		'''
		# print("SENDING MESSAGE TYPE:", self.message_ID_to_func_name[message_id])
		message = self.construct_message(message_id, payload_bytes)
		yield from self.io_loop.sock_sendall(self.sock, message)
		if message_id in [0,1,2,3]:
			self.update_state(message_id)

	def update_state(self, message_id):
		if message_id == 0:
			self.state['am_choking'] = True
		elif message_id == 1:
			self.state['am_choking'] = False
		elif message_id == 2:
			self.state['am_interested'] = True
		elif message_id == 3:
			self.state['am_interested'] = False
	