import socket
import sys
import asyncio

class Peer():
	def __init__(self, ip, port, number_of_peices):
		self.IP = ip
		self.port = port
		# choke: <len=0001><id=0>, unchoke: <len=0001><id=1>, interested: <len=0001><id=2>, not interested: <len=0001><id=3>, have: <len=0005><id=4><piece index>, bitfield: <len=0001+X><id=5><bitfield>, request: <len=0013><id=6><index><begin><length>, piece: <len=0009+X><id=7><index><begin><block>, cancel: <len=0013><id=8><index><begin><length>, port: <len=0003><id=9><listen-port>
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.handshake_bytes = None
		self.has_pieces = [False] * number_of_peices
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

	@asyncio.coroutine
	def connect(self, message):
		self.message = message
		io_loop = asyncio.get_event_loop()
		self.sock.setblocking(0)
		yield from io_loop.sock_connect(self.sock, (self.IP, self.port))
		yield from io_loop.sock_sendall(self.sock, message)
		buf = b''
		while len(buf) < 68:
			message_bytes = yield from io_loop.sock_recv(self.sock, 4096)
			if not message_bytes:
				raise Exception("Socket closed unexpectedly while receiving hanshake")
			buf += message_bytes
		self.check_handshake(buf[:68])
		buf = buf[68:]
		print('buffer:', buf)

		def dispatch_messages_from_buf(buf):
			while True:
				if len(buf) >= 4:
					message_length = int.from_bytes(buf[:4], byteorder='big')
					print('message length:', message_length)
					if message_length == 0:
						self.keep_alive()
						buf = buf[4:]
					elif len(buf[4:]) >= message_length:
						message = buf[4:message_length+4]
						self.dispatch_message(message)
						buf = buf[message_length+4:]
					else:
						return buf	
				else:
					return buf

		while True:
			buf = dispatch_messages_from_buf(buf)
			print('before')
			message_bytes = yield from io_loop.sock_recv(self.sock, 4096)
			print('after')
			if not message_bytes:
				raise Exception("Socket closed unexpectedly while receiving message")
			print('message_bytes, adding to buffer:', message_bytes)
			buf += message_bytes


	def construct_message(self, message_id, payload_bytes=b''):
		'''messages in the protocol take the form of 
		<length prefix><message ID><payload>. The length prefix is a four byte 
		big-endian value. The message ID is a single decimal byte. 
		The payload is message dependent.
		'''
		length_bytes = (1 + len(payload)).to_bytes(4, byteorder='big')
		message_id_bytes = message_id.to_bytes(1, byteorder='big')
		elements = [length_bytes, message_id_bytes, payload_bytes]
		message_bytes = b''.join(elements)
		return message_bytes

	def send_message_and_update_state(self, message_id):
		# message = self.construct_message(message_id)
		# yield from io_loop.sock_sendall(self.sock, message)
		if message_id == '0':
			self.state['am_choking'] = True
		elif message_id == '1':
			self.state['am_choking'] = False
		elif message_id == '2':
			self.state['am_interested'] = True
		elif message_id == '3':
			self.state['am_interested'] = False

	def dispatch_message(self, message_bytes):
		''' 
			Pass all messages to their appropriate functions.
		'''
		message_id = message_bytes[0]
		message_slice = message_bytes[1:]
		self.message_ID_to_func_name[message_id](message_slice)

	def check_handshake(self, handshake_bytes):
		if handshake_bytes[28:48] != self.message[28:48]:
			self.sock.close()
			raise Exception('Peer returned invalid info_hash. Closing socket')
		print('Handshake Bytes:', handshake_bytes)	

	def keep_alive(self):
		# TODO: update time/state
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
		piece_index = int.from_bytes(message_bytes, byteorder='big')
		print('piece_index', piece_index)
		print(self.has_pieces[piece_index])
		self.has_pieces[piece_index] = True
		
	def bitfield(self, message_bytes):
		print("parsing bitfield")
		bitstring = ''.join('{0:08b}'.format(byte) for byte in message_bytes)
		self.has_pieces = [bool(int(c)) for c in bitstring]
		print("has_pieces:", self.has_pieces)
		
	def request(self, message_bytes):
		pass
		
	def piece(self, message_bytes):
		'''TODO:
		THIS ONE NEXT
		'''
		pass
		#piece: <len=0009+X><id=7><index><begin><block>,
	def cancel(self, message_bytes):
		pass
		#cancel: <len=0013><id=8><index><begin><length>,
	def port(self, message_bytes):
		pass
		#port: <len=0003><id=9><listen-port>

	
	