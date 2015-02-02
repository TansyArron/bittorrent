import hashlib
import bencoding
import peer
import random
import requests
import asyncio
import math
import os
import json

class Torrent():
	def __init__(self, torrent_file, remove_peer_callback, start_listener_callback):
		with open(torrent_file, 'rb') as f:
			self.torrent_file = f.read()
		self.start_listener_callback = start_listener_callback
		self.meta_info_dict = bencoding.decode(self.torrent_file)
		self.announce = self.meta_info_dict[b'announce'].decode('utf-8')
		self.info_dict = self.meta_info_dict[b'info']
		self.bencoded_info_dict = self.info_dict['ben_string']
		self.filename = self.info_dict[b'name'].decode('utf-8')
		self.path = 'torrents_in_progress'
		self.info_hash = hashlib.sha1(self.bencoded_info_dict).digest()
		self.peer_id = '-'.join(['','TZ', '0000', str(random.randrange(10000000000,99999999999))])
		self.ip = self.get_IP_address()
		self.port =  '6881' #TODO: Try ports in range (6881,6889)
		self.length = int(self.info_dict[b'length']) if b'length' in self.info_dict \
				else sum([int((f[b'length'])) for f in self.info_dict[b'files']])
		self.piece_length = int(self.info_dict[b'piece length'])
		self.pieces = self.info_dict[b'pieces']
		self.number_of_pieces = math.ceil(self.length/self.piece_length)
		self.downloaded = 0
		self.have = [False] * self.number_of_pieces #TODO: pass torrent class a bitfield and handle restarting torrents
		self.tracker_info = self.get_info_from_tracker()
		self.peer_info = self.tracker_info[b'peers']
		self.peers = self.create_peers()
		self.tracker_id = None
		self.complete = False #TODO: Update when self.pieces_needed is empty
		self.io_loop = asyncio.get_event_loop()
		self.index = 0
		self.remove_peer_callback = remove_peer_callback
		self.callback_dict = {
			'check_piece' : self.check_piece_callback,
			'pieces_changed' : self.pieces_changed_callback,
		}
		self.pieces_needed = []

	
	def get_IP_address(self):
		response = requests.get('http://api.ipify.org?format=json')
		ip_object = json.loads(response.text)
		return ip_object["ip"]

	@property
	def get_directory(self):
		'''TODO: add handling for multiple file torrents
		'''
		if not os.path.exists(self.path):
			os.makedirs(self.path)
		return self.path

	@property	
	def handshake(self):
		pstrlen = b'\x13'
		pstr = b'BitTorrent protocol'
		reserved = b'\x00\x00\x00\x00\x00\x00\x00\x00'
		parts = [pstrlen, pstr, reserved, self.info_hash, self.peer_id.encode()]
		handshake_string = b''.join(parts)
		return handshake_string
			
	@property
	def left(self):
		return int(self.length) - self.downloaded

	def get_params(self):
		return {
		'info_hash': self.info_hash,
		'event': 'started',
		'downloaded': self.downloaded,
		'peer_id': self.peer_id,
		'port': self.port,
		'left': self.left,
		'compact': '0',
		}

	def get_info_from_tracker(self):
		tracker_info = requests.get(self.announce, params=self.get_params(), stream=True).raw.read()
		print(tracker_info)
		return bencoding.decode(tracker_info)

	def update_tracker_id(self):
		if 'tracker_id' in self.tracker_info:
			self.tracker_id = self.tracker_info['tracker_id']
			
	def get_peer_address(self):
		peer_list = []
		if isinstance(self.peer_info, list):
			for peer in self.peer_info:
				peer_list.append(peer_dict[ip], peer_dict[port])
		
		else:
			peers = [self.peer_info[i:i+6] for i in range(0, len(self.peer_info), 6)]
			for peer in peers:
				ip = '.'.join(str(i) for i in peer[:4])
				port = int.from_bytes(peer[4:], byteorder='big')
				peer_list.append((ip, port))
		return peer_list

	def create_peers(self):
		peers = []
		for p in self.get_peer_address():
			if p[0] == self.ip:
				continue
			peers.append(peer.Peer(p[0], p[1], self.number_of_pieces, self.pieces_changed_callback, self.check_piece_callback, self.start_listener_callback))
		return peers

	def update_pieces_needed(self):
		'''	Search self.have for pieces not yet recieved and add them to list. 
			If all pieces are accounted for, stop the io_loop and change self.complete
			to True
		'''
		self.pieces_needed = []
		for index, value in enumerate(self.have):
			if not value:
				self.pieces_needed.append(index)
		if not self.pieces_needed:
			self.complete = True
			self.io_loop.stop()
			print("DONE!!!!!")

	def pieces_changed_callback(self, peer):
		'''	Check if connected peer has pieces I need. Send interested message.
			Call choose_piece.
			If peer has no pieces I need, disconnect and remove from peers list.
		'''
		self.update_pieces_needed()
		for i in self.pieces_needed:
			if peer.has_pieces[i]:
				self.io_loop.create_task(peer.send_message(2))
				self.choose_piece(peer)	
				break
			else:
				self.remove_peer_callback(peer)
		# TODO except if peer has no needed pieces and disconnect.

	def choose_piece(self, peer):
		next_piece_index = self.pieces_needed[0]
		piece_index_bytes = (next_piece_index).to_bytes(4, byteorder='big')
		self.have[next_piece_index] = True
		self.update_pieces_needed()
		piece_begin = (0).to_bytes(4, byteorder='big')
		piece_length = (16384).to_bytes(4, byteorder='big')
		piece_id = b''.join([piece_index_bytes, piece_begin, piece_length])
		self.io_loop.create_task(peer.send_message(6, piece_id))	
			
	def check_piece_callback(self, piece, piece_index, peer):
		self.check_piece(piece, piece_index, peer)

	def check_piece(self, piece, piece_index_bytes, peer):
		'''	hash a received piece and check against relevent hash provided in 
			.torrent file. Write the piece to file. Update self.downloaded.
			call choose_piece
			else, set self.have[piece_index] to False and choose the next piece. 
		'''
		piece_index = int.from_bytes(piece_index_bytes, byteorder='big')
		received_hash = hashlib.sha1(piece).digest()
		hash_from_info = self.pieces[piece_index * 20:(1 + piece_index) * 20]
		if received_hash == hash_from_info:
			self.write_piece(piece, piece_index)
			self.downloaded += 1
			self.choose_piece(peer)
		else:
			print('PIECE AT INDEX {} DOES NOT MATCH HASH'.format(piece_index))
			self.have[piece_index] = False
			self.choose_piece(peer)

	def write_piece(self, piece, piece_index):
		print('Writing piece {} to file'.format(piece_index))
		offset = piece_index * self.piece_length
		try:
			with open(os.path.join(self.get_directory, self.filename), 'rb+') as torrent_file:
				torrent_file.seek(offset)
				torrent_file.write(piece)
		except IOError: #file does not exist yet.
			with open(os.path.join(self.get_directory, self.filename), 'wb') as torrent_file:
				torrent_file.seek(offset)
				torrent_file.write(piece)
			
