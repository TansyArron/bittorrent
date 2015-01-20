import socket
import sys
import asyncio

class Peer():
	def __init__(self, ip, port, number_of_peices):
		self.IP = ip
		self.port = port
		# choke: <len=0001><id=0>, unchoke: <len=0001><id=1>, interested: <len=0001><id=2>, not interested: <len=0001><id=3>, have: <len=0005><id=4><piece index>, bitfield: <len=0001+X><id=5><bitfield>, request: <len=0013><id=6><index><begin><length>, piece: <len=0009+X><id=7><index><begin><block>, cancel: <len=0013><id=8><index><begin><length>, port: <len=0003><id=9><listen-port>
		self.messages = {'0':'0001', '1':'0001', '2':'0001', '3':'0001', '4':'0005', '5':'0001', '6':'0013', '7':'0009', '8':'0013', '9':'0003'} #choke, unchoke, interested etc
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
		self.parse_message(self.message_bytes)
		

	def check_handshake(self):
		
		self.message_bytes = self.handshake_bytes[68:]
		self.parse_message(self.message_bytes)
		
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

'''list of message names/ index in and call "message_name[2](bytes)"???
Might be tidier than this mess. Also helper function for slicing relevent 
bytes from byte SOCK_STREAM'''

	def parse_message(self, message_bytes):
		if message_bytes[:20] == b'\x13BitTorrent protocol':
			print("Checking Handshake")
			if len(self.message_bytes) < 48 or self.message_bytes[28:48] != self.message[28:48]:
				self.sock.close()
				raise Exception('Peer returned invalid info_hash. Closing socket')
			remaining_bytes = message_bytes[68:]
			if len(remaining_bytes) > 0:
				self.parse_message(remaining_bytes)
		message_length = int(''.join(str(byte) for byte in message_bytes[:4]))
		if int(message_length) == 0:
			return 'keep alive' # TODO: update time/state
		message_id = int(message_bytes[4])
		if message_id == 0:
			self.state['peer_choking'] = True 
		elif message_id == 1:
			self.state['peer_choking'] = False
			#unchoke: <len=0001><id=1>,
		elif message_id == 2:
			self.state['peer_interested'] == True
			#interested: <len=0001><id=2>,
		elif message_id == 3:
			self.state['peer_interested'] == False
			#not interested: <len=0001><id=3>, 
		elif message_id == 4:
			#Indexing errors? Dunno what's going on but it doesn't seem
			#to update correctly. Unless I'm only getting "have" messages
			#for piece[0]???
			print(message_bytes[5:])
			piece_index = message_bytes[5]
			print(self.has_pieces[piece_index])
			self.has_pieces[piece_index] = True
			print(self.has_pieces[piece_index])
			remaining_bytes = message_bytes[4+message_length:]
			if len(remaining_bytes) > 0:
				self.parse_message(remaining_bytes)
			#have: <len=0005><id=4><piece index>,
		elif message_id == 5:
			bitfield = message_bytes[5:4 + message_length]
			bitstring = ''.join('{0:08b}'.format(byte) for byte in bitfield)
			self.has_pieces = [bool(int(c)) for c in bitstring]
			print("has_pieces:", self.has_pieces)
			remaining_bytes = message_bytes[4+message_length:]
			if len(remaining_bytes) > 0:
				self.parse_message(remaining_bytes)
			#bitfield: <len=0001+X><id=5><bitfield>,
		elif message_id == 6:
			pass
			#request: <len=0013><id=6><index><begin><length>,
		elif message_id == 7:
			'''TODO:
			THIS ONE NEXT
			'''
			pass
			#piece: <len=0009+X><id=7><index><begin><block>,
		elif message_id == 8:
			pass
			#cancel: <len=0013><id=8><index><begin><length>,
		elif message_id == 9:
			pass
			#port: <len=0003><id=9><listen-port>
		