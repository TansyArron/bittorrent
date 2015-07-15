from hashlib import sha1
from bencoding import decode as bdecode
from random import randrange
from requests import get
from math import ceil
from os import makedirs, path
from json import loads
from asyncio import get_event_loop

class Torrent():
	''' Contains all torrent meta info, constructs handshake.

	'''
	def __init__(self, torrent_file):
		with open(torrent_file, 'rb') as f:
			self.torrent_file = f.read()
		self.meta_info_dict = bdecode(self.torrent_file)
		self.announce = self.meta_info_dict[b'announce'].decode('utf-8')
		self.info_dict = self.meta_info_dict[b'info']
		self.bencoded_info_dict = self.info_dict['ben_string']
		self.filename = self.info_dict[b'name'].decode('utf-8')
		self.path = 'torrents_in_progress'
		self.info_hash = sha1(self.bencoded_info_dict).digest()
		self.peer_id = '-'.join(['','TZ', '0000', str(randrange(10000000000,99999999999))])
		self.ip = self.get_IP_address()
		self.port =  '6881' #TODO: Try ports in range (6881,6889)
		self.length = int(self.info_dict[b'length']) if b'length' in self.info_dict \
				else sum([int((f[b'length'])) for f in self.info_dict[b'files']])
		self.piece_length = int(self.info_dict[b'piece length'])
		self.pieces = self.info_dict[b'pieces']
		self.piece_hashes = [self.pieces[i:i+20] for i in range(0, len(self.pieces), 20)]
		self.number_of_pieces = ceil(self.length/self.piece_length)
		self.downloaded = 0
		self.uploaded = 0
		self.have = [False] * self.number_of_pieces #TODO: pass torrent class a bitfield and handle restarting torrents
		self.complete = False #TODO: Update when self.pieces_needed is empty
		self.io_loop = get_event_loop()
		self.pieces_needed = []

	
	def get_IP_address(self):
		response = get('http://api.ipify.org?format=json')
		ip_object = loads(response.text)
		return ip_object["ip"]

	@property
	def get_directory(self):
		'''TODO: add handling for multiple file torrents
		'''
		if not path.exists(self.path):
			makedirs(self.path)
		return self.path

	@property
	def left(self):
		return int(self.length) - self.downloaded

	@property	
	def handshake(self):
		''' construct handshake bytestring in form:
			<19><'BitTorrent protocol'><00000000><ID>
			Spec here: https://wiki.theory.org/BitTorrentSpecification#Handshake
		'''
		pstrlen = b'\x13'
		pstr = b'BitTorrent protocol'
		reserved = b'\x00\x00\x00\x00\x00\x00\x00\x00'
		parts = [pstrlen, pstr, reserved, self.info_hash, self.peer_id.encode()]
		handshake_string = b''.join(parts)
		return handshake_string
			
	def get_params(self):
		return {
		'info_hash': self.info_hash,
		'event': 'started',
		'downloaded': self.downloaded,
		'uploaded' : self.uploaded,
		'peer_id': self.peer_id,
		'port': self.port,
		'left': self.left,
		# 'compact': '0',
		}


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


	def check_piece_callback(self, piece, piece_index_bytes, peer):
		'''	hash a received piece and check against relevent hash provided in 
			.torrent file. Write the piece to file. Update self.downloaded and
			choose next piece.
			If the hashes do not match, set self.have[piece_index] to False and 
			choose the next piece. 
		'''
		piece_index = int.from_bytes(piece_index_bytes, byteorder='big')
		received_hash = sha1(piece).digest()
		#hash_from_info = self.pieces[piece_index * 20:(1 + piece_index) * 20]
		hash_from_info = self.piece_hashes[piece_index]
		if received_hash == hash_from_info:
			self.write_piece(piece, piece_index)
			self.downloaded += 1
		else:
			print('PIECE AT INDEX {} DOES NOT MATCH HASH'.format(piece_index))
			print('received:', received_hash)
			print('expected:', hash_from_info)
			self.have[piece_index] = False
			self.choose_piece(peer)

	def write_piece(self, piece, piece_index):
		''' write piece to file in the appropriate location. If the file or path do not exist, 
			create them.
		'''
		print('Writing piece {} to file'.format(piece_index))
		offset = piece_index * self.piece_length
		try:
			with open(path.join(self.get_directory, self.filename), 'rb+') as torrent_file:
				torrent_file.seek(offset)
				torrent_file.write(piece)
		except IOError: #file does not exist yet.
			with open(path.join(self.get_directory, self.filename), 'wb') as torrent_file:
				torrent_file.seek(offset)
				torrent_file.write(piece)
			
