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

	@asyncio.coroutine
	def connect(self, message):
		self.message = message
		io_loop = asyncio.get_event_loop()
		self.sock.setblocking(0)
		yield from io_loop.sock_connect(self.sock, (self.IP, self.port))
		yield from io_loop.sock_sendall(self.sock, message)
		self.message_bytes = yield from io_loop.sock_recv(self.sock, 500)
		self.check_handshake(self.message_bytes)
		
	def construct_message(self, message_id, payload=b''):
		'''messages in the protocol take the form of 
		<length prefix><message ID><payload>. The length prefix is a four byte 
		big-endian value. The message ID is a single decimal byte. 
		The payload is message dependent.
		'''
		length = 1 + len(payload)
		elements = [length, message_id, payload]
		message = ''.join(elements)
		return message

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

	def parse_message(self, message_bytes):
		'''Check for handshake and keep alive messages. 
		pass all messages to their appropriate functions.
		'''
		message_length = int(''.join(str(byte) for byte in message_bytes[:4])) #Struct? Helper function?	
		if int(message_length) == 0:
			return keep_alive() 
		print('length:', message_length)
		message_id = int(message_bytes[4])
		print('ID:', message_id)
		message_slice = message_bytes[5:message_length + 4]
		print(message_slice)
		self.message_ID_to_func_name[message_id](self, message_slice)
		# message_func(message_slice)
		remaining_bytes = message_bytes[message_length+4:]
		if len(remaining_bytes) > 4:
			return self.parse_message(remaining_bytes)

	def check_handshake(self, message_bytes):
		if len(self.message_bytes) < 48 or self.message_bytes[28:48] != self.message[28:48]:
			self.sock.close()
			raise Exception('Peer returned invalid info_hash. Closing socket')
		print(message_bytes[68:])
		return self.parse_message(message_bytes[68:])	

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
		#TODO: Indexing errors? Dunno what's going on but it doesn't seem
		#to update correctly. Unless I'm only getting "have" messages
		#for piece[0]???
		piece_index = message_bytes[0]
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

	message_ID_to_func_name = {
		0 : choke,
		1 : unchoke,
		2 : interested,
		3 : not_interested,
		4 : have,
		5 : bitfield,
		6 : request,
		7 : piece,
		8 : cancel, 
		9 : port,
	}
	