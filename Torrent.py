import hashlib
import bdecoder
import random
import requests
import peer

class Torrent():
	def __init__(self, torrent_file):
		self.torrent_file = open(torrent_file, 'rb')
		self.meta_info_dict = bdecoder.bdecoder(self.torrent_file.read())
		self.announce = self.meta_info_dict[b'announce'].decode('utf-8')
		self.info_dict = self.meta_info_dict[b'info']
		self.bencoded_info_dict = self.info_dict['ben_string']
		self.info_hash = hashlib.sha1(self.bencoded_info_dict).digest()
		self.downloaded = 0 # TODO: calculate "downloaded"
		self.peer_id = '-'.join(['','TZ', '0000', str(random.randrange(10000000000,99999999999))])
		self.port =  '6881' #TODO: Try ports in range (6881,6889)
		self.length = self.info_dict[b'length'] if b'length' in self.info_dict \
				else sum([int(f[b'length']) for f in self.info_dict[b'files']])
		self.left = int(self.length) - self.downloaded
		self.tracker_info = self.get_info_from_tracker()
		self.handshake = b''.join([chr(19).encode(), 'BitTorrent protocol'.encode(), chr(0).encode()*8, self.info_hash, self.peer_id.encode()])
		self.peer_info = self.tracker_info[b'peers']
		self.peers = self.get_peers()

	def downloaded(self):
		pass
		
	# @property
	# def left(self):
	# 	return self.length - self.downloaded

	def get_params(self):
		return {
		'info_hash': self.info_hash,
		'event' : 'started',
		'downloaded' : self.downloaded,
		'peer_id' : self.peer_id,
		'port' : self.port,
		'left' : self.left
		}

	def get_info_from_tracker(self):
		tracker_info = requests.get(self.announce, params=self.get_params(), stream=True).raw.read()
		return bdecoder.bdecoder(tracker_info)

	def get_peers(self):
		peers = [self.peer_info[i:i+6] for i in range(0, len(self.peer_info), 6)]
		peer_list = [peer.Peer('.'.join(str(i) for i in p[:4]), int.from_bytes(p[4:], byteorder='big')) for p in peers]
		return peer_list

# torrent = Torrent('tristanandisolda16250gut_archive.torrent')
# torrent = Torrent('flagfromserver.torrent')

