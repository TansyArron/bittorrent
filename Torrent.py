import hashlib
import bencode
import random
import requests
import peer
import asyncio
import math

class Torrent():
	def __init__(self, torrent_file):
		with open(torrent_file, 'rb') as f:
			self.torrent_file = f.read()
		self.meta_info_dict = bencode.bdecoder(self.torrent_file)
		self.announce = self.meta_info_dict[b'announce'].decode('utf-8')
		self.info_dict = self.meta_info_dict[b'info']
		self.bencoded_info_dict = self.info_dict['ben_string']
		self.info_hash = hashlib.sha1(self.bencoded_info_dict).digest()
		self.downloaded = 0 # TODO: calculate "downloaded"
		self.peer_id = '-'.join(['','TZ', '0000', str(random.randrange(10000000000,99999999999))])
		self.port =  '6881' #TODO: Try ports in range (6881,6889)
		self.length = int(self.info_dict[b'length']) if b'length' in self.info_dict \
				else sum([int((f[b'length'])) for f in self.info_dict[b'files']])
		self.piece_length = int(self.info_dict[b'piece length'])
		self.pieces = self.info_dict[b'pieces']
		self.number_of_pieces = math.ceil(self.length/self.piece_length)
		self.tracker_info = self.get_info_from_tracker()
		self.peer_info = self.tracker_info[b'peers']
		self.peers = self.get_peers()
		self.tracker_id = None
		self.have = [0] * self.number_of_pieces

	def downloaded(self):
		pass

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
		}

	def get_info_from_tracker(self):
		tracker_info = requests.get(self.announce, params=self.get_params(), stream=True).raw.read()
		return bencode.bdecoder(tracker_info)

	def update_tracker_id(self):
		if 'tracker_id' in self.tracker_info:
			self.tracker_id = self.tracker_info['tracker_id']
			
	def get_peers(self):
		if isinstance(self.peer_info, list):
			peer_list = [peer.Peer(peer_dict[ip], peer_dict[port], self.number_of_pieces)for peer_dict in self.peer_info]
		else:
			peers = [self.peer_info[i:i+6] for i in range(0, len(self.peer_info), 6)]
			peer_list = [peer.Peer('.'.join(str(i) for i in p[:4]), int.from_bytes(p[4:], byteorder='big'), self.number_of_pieces) for p in peers]
		return peer_list

# torrent = Torrent('tristanandisolda16250gut_archive.torrent')
# torrent = Torrent('flagfromserver.torrent')

