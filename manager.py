from sys import argv
from torrent import Torrent
from torrent_downloader import Torrent_Downloader
from asyncio import get_event_loop, coroutine
from traceback import print_exc

class Manager():
	def __init__(self, torrent_file):
		self.torrent = Torrent(torrent_file)
		self.torrent_downloader = Torrent_Downloader(self.torrent, self.start_listener_callback)
		self.loop = get_event_loop()
		self.start_loop = self.start_loop()

	@coroutine
	def start_listener_callback(self):
		for peer in self.torrent_downloader.peers:
			if peer.connected:
				yield from peer.listen()

	def remove_peer_callback(self, peer):
		self.torrent_downloader.peer.sock.close()
		self.torrent_downloader.peer_list.remove(peer)
		
	@coroutine
	def connect_peers(self):
		for peer in self.torrent_downloader.peers:
			try:
				print('CONNECTING')
				self.loop.create_task(peer.connect(self.torrent.handshake))
			except Exception as e:
				traceback.print_exc()
				print('peer {} failed to connect. Exception: "{}"'.format(peer, e))
		
	def start_loop(self):
		self.loop.create_task(self.connect_peers())
		self.loop.run_forever()
		
torrent_file = argv[1]
manager = Manager(torrent_file)





