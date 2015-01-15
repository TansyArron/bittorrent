import sys
import Torrent
import myclient

class Manager():
	def __init__(self, torrent_file):
		self.torrent = Torrent.Torrent(torrent_file)
		self.host = '0.0.0.0' #ifconfig thing. Get my current ip.
		self.port = 6881 # try in range 6881, 6889.
		self.connected_peers = []

	def add_peer(self):
		peer = self.torrent.peers.pop()
		peer.connect(self.torrent.handshake)
		self.connected_peers.append(peer)

	def remove_peer(self):
		pass

	def main(self):
		while len(self.connected_peers) < 10 and self.torrent.peers:
			self.add_peer()

torrent_file = sys.argv[1]
manager = Manager(torrent_file)
