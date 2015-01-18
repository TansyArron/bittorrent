import socket
import sys
import asyncio

class Peer():
	def __init__(self, ip, port):
		self.IP = ip
		self.port = port
		self.messages = {'0':'0001', '1':'0001', '2':'0001', '3':'0001', '4':'0005', '5':'0001', '6':'0013', '7':'0009', '8':'0013', '9':'0003'} #choke, unchoke, interested etc
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.handshake_bytes = None
		self.pieces = None
		self.state = {
				'am_choking' : 1,
				'am_interested' : 0,
				'peer_choking' : 1,
				'peer_interested' : 0,
		}

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
			bitfield = self.handshake_bytes[68:]
			bitstring = ''.join('{0:08b}'.format(ord(byte)) for byte in bitfield)
			self.pieces = [int(c) for c in bitstring]
		
	def construct_message(self, message_id):
		'''messages in the protocol take the form of 
		<length prefix><message ID><payload>. The length prefix is a four byte 
		big-endian value. The message ID is a single decimal byte. 
		The payload is message dependent.
		'''
		elements = self.messages[message_id]
		message = ''.join(elements)
		return message

	def send_message_and_update_state(self, message_id):
		# message = self.construct_message(message_id)
		# yield from io_loop.sock_sendall(self.sock, message)
		if message_id == '0':
			self.state['am_choking'] = 1
		elif message_id == '1':
			self.state['am_choking'] = 0
		elif message_id == '2':
			self.state['am_interested'] = 1
		elif message_id == '3':
			self.state['am_interested'] = 0

	def receive_message_and_update_state(self, message_id):
		if message_id == '0':
			self.state['peer_choking'] = 1
		elif message_id == '1':
			self.state['peer_choking'] = 0
		elif message_id == '2':
			self.state['peer_interested'] == 1
		elif message_id == '3':
			self.state['peer_interested'] == 0

new_peer = Peer('ip', 'port')
new_peer.send_message_and_update_state('2')
print(new_peer.state)

