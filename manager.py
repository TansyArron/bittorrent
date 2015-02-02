import sys
import torrent
import asyncio
import traceback

class Manager():
	def __init__(self, torrent_file):
		self.torrent = torrent.Torrent(torrent_file, self.remove_peer_callback, self.start_listener_callback)
		self.connected_peers = []
		self.loop = asyncio.get_event_loop()
		self.start_loop = self.start_loop()

	@asyncio.coroutine
	def start_listener_callback(self):
		for peer in self.torrent.peers:
			if peer.connected:
				yield from peer.listen()
		

	def remove_peer_callback(self, peer):
		self.torrent.peer.sock.close()
		self.torrent.peer_list.remove(peer)
		self.connected_peers.remove(peer)

	@asyncio.coroutine
	def connect_peers(self):
		for peer in self.torrent.peers:
			try:
				print('CONNECTING')
				self.loop.create_task(peer.connect(self.torrent.handshake))
				self.connected_peers.append(peer)
			except Exception as e:
				traceback.print_exc()
				print('peer {} failed to connect. Exception: "{}"'.format(peer, e))
		
	def start_loop(self):
		
		self.loop.create_task(self.connect_peers())
		self.loop.run_forever()
		
torrent_file = sys.argv[1]
manager = Manager(torrent_file)





