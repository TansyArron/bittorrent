from message_handler import MessageHandler
from peer import Peer
from tracker import Tracker
from requests import get
from asyncio import get_event_loop
from json import loads

class Torrent_Downloader():
	''' Manages download logic:
		- Creation and removal of peers. 
		- Book keeping of pieces downloaded and in progress.
		- Checking completed pieces and writing to file.
	'''
	def __init__(self, torrent, start_listener_callback):
		self.torrent = torrent
		self.message_handler = MessageHandler(self.torrent, self)
		self.start_listener_callback = start_listener_callback
		self.ip = self.get_IP_address()
		self.tracker = Tracker(self.torrent.announce, self.torrent.get_params())
		self.peers = self.create_peers()
		self.io_loop = get_event_loop()
		self.index = 0
		self.callback_dict = {
			'check_piece' : self.torrent.check_piece_callback,
			'pieces_changed' : self.pieces_changed_callback,
			'start_listener' : self.start_listener_callback,
		}
		self.pieces_needed = []


	def get_IP_address(self):
		response = get('http://api.ipify.org?format=json')
		ip_object = loads(response.text)
		return ip_object["ip"]

	def create_peers(self):
		peers = []
		for p in self.tracker.parse_peer_address():
			if p[0] == self.ip:
				continue
			peers.append(Peer(p[0], p[1], self))
		return peers

	def pieces_changed_callback(self, peer):
		'''	Check if connected peer has pieces I need. Send interested message.
			Call choose_piece.
			If peer has no pieces I need, disconnect and remove from peers list.
		'''
		self.torrent.update_pieces_needed()
		for i in self.torrent.pieces_needed:
			if peer.has_pieces[i]:
				self.io_loop.create_task(self.message_handler.send_message(peer=peer, message_id=2))
				self.choose_piece(peer=peer)	
				break
			else:
				self.peers.remove(peer)

	def choose_piece(self, peer):
		'''	Finds the next needed piece, updates self.have and self.pieces_needed.
			calls construct_request_payload.
		'''
		piece_index = self.torrent.pieces_needed[0]
		self.torrent.have[piece_index] = True
		self.torrent.update_pieces_needed()
		self.message_handler.construct_request_payload(peer=peer, piece_index=piece_index)



	