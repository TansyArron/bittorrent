import sys
import torrent
import asyncio
import traceback

class Manager():
	def __init__(self, torrent_file):
		self.torrent = torrent.Torrent(torrent_file, self.remove_peer_callback)
		self.loop = self.start_loop()

	@property
	def connected_peers(self):
		connected_peers = []
		for peer in self.torrent.peers:
			if peer.connected:
				connected_peers.append(peer)
		return connected_peers

	@asyncio.coroutine
	def add_peer(self, peer):
		print('Adding a Peer')
		try:	
			yield from peer.connect(self.torrent.handshake)
			self.connected_peers.append(peer)
		except Exception as e:
			traceback.print_exc()
			print('peer {} failed to connect. Exception: "{}"'.format(peer, e))

	def remove_peer_callback(self, peer):
		torrent.peer.sock.close()
		torrent.peer_list.remove(peer)
		self.connected_peers.remove(peer)

	@asyncio.coroutine
	def connect_peers(self):
		for peer in self.torrent.peers:
			yield from self.add_peer(peer)


	@asyncio.coroutine	
	def scheduler(self):
		yield from self.connect_peers()
		if self.connected_peers:
			for peer in self.connected_peers:
				yield from peer.listen()

	def start_loop(self):
		loop = asyncio.get_event_loop()
		loop.create_task(self.scheduler())
		loop.run_forever()
		

torrent_file = sys.argv[1]
manager = Manager(torrent_file)





