import sys
import torrent
import asyncio
import traceback

class Manager():
	def __init__(self, torrent_file):
		self.torrent = torrent.Torrent(torrent_file)
		self.connected_peers = []

	@asyncio.coroutine
	def add_peer(self, peer):
		print('Adding a Peer')
		try:
			result = peer.connect(self.torrent.handshake)
			yield from result
			self.connected_peers.append(peer)
		except Exception as e:
			traceback.print_exc()
			print('peer {} failed to connect. Exception: "{}"'.format(peer, e))

	def remove_peer(self):
		pass

	def main(self):
		loop = asyncio.get_event_loop()
		peer = self.torrent.peers[0]
		for peer in self.torrent.peers:
			loop.create_task(self.add_peer(peer))
		# loop.create_task(self.add_peer(peer))
		loop.run_forever()
		

torrent_file = sys.argv[1]
manager = Manager(torrent_file)
manager.main()
print(len(self.connected_peers))
# manager.add_peer() 

