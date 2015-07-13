import hashlib
import bencoding
import peer
import tracker
import requests
import asyncio
import math
import os
import json

class Torrent_Downloader():
	''' Manages download logic:
		- Creation and removal of peers. 
		- Book keeping of pieces downloaded and in progress.
		- Checking completed pieces and writing to file.
	'''
	def __init__(self, torrent, start_listener_callback):
		# self.filename = torrent.filename
		# self.path = torrent.path
		# self.tracker_info = self.get_info_from_tracker()
		# self.tracker_id = None
		# self.peer_list = torrent.peer_info
		self.torrent = torrent
		self.start_listener_callback = start_listener_callback
		self.ip = self.get_IP_address()
		self.tracker = tracker.Tracker(self.torrent.announce, self.torrent.get_params())
		# self.peer_list = torrent.peer_list
		self.peers = self.create_peers()
		# self.have = [False] * self.number_of_pieces #TODO: pass torrent class a bitfield and handle restarting torrents
		# self.complete = False #TODO: Update when self.pieces_needed is empty
		self.io_loop = asyncio.get_event_loop()
		self.index = 0
		self.callback_dict = {
			'check_piece' : self.torrent.check_piece_callback,
			'pieces_changed' : self.pieces_changed_callback,
			'start_listener' : self.start_listener_callback,
		}
		self.pieces_needed = []


	def get_IP_address(self):
		response = requests.get('http://api.ipify.org?format=json')
		ip_object = json.loads(response.text)
		return ip_object["ip"]

	def create_peers(self):
		peers = []
		for p in self.tracker.parse_peer_address():
			if p[0] == self.ip:
				continue
			peers.append(peer.Peer(p[0], p[1], self))
		return peers

	# def update_pieces_needed(self):
	# 	'''	Search self.have for pieces not yet recieved and add them to list. 
	# 		If all pieces are accounted for, stop the io_loop and change self.complete
	# 		to True
	# 	'''
	# 	self.pieces_needed = []
	# 	for index, value in enumerate(self.have):
	# 		if not value:
	# 			self.pieces_needed.append(index)
	# 	if not self.pieces_needed:
	# 		self.complete = True
	# 		self.io_loop.stop()
	# 		print("DONE!!!!!")

	def pieces_changed_callback(self, peer):
		'''	Check if connected peer has pieces I need. Send interested message.
			Call choose_piece.
			If peer has no pieces I need, disconnect and remove from peers list.
		'''
		self.torrent.update_pieces_needed()
		for i in self.torrent.pieces_needed:
			if peer.has_pieces[i]:
				self.io_loop.create_task(peer.send_message(2))
				self.choose_piece(peer)	
				break
			else:
				self.peers.remove(peer)
		# TODO except if peer has no needed pieces and disconnect.

	def choose_piece(self, peer):
		'''	Finds the next needed piece, updates self.have and self.pieces_needed.
			calls construct_request_payload.
		'''
		piece_index = self.torrent.pieces_needed[0]
		self.torrent.have[piece_index] = True
		self.torrent.update_pieces_needed()
		self.construct_request_payload(piece_index, peer)

	def construct_request_payload(self, piece_index, peer):
		'''	Constructs the payload of a request message for piece_index.
			Calls peer.send_message to finish construction and send.
		'''
		piece_index_bytes = (piece_index).to_bytes(4, byteorder='big')
		piece_begin = (0).to_bytes(4, byteorder='big')
		piece_length = (16384).to_bytes(4, byteorder='big')
		payload = b''.join([piece_index_bytes, piece_begin, piece_length])
		self.io_loop.create_task(peer.send_message(6, payload))	

	def construct_piece_payload(self, index, offset, length):
		''' Constructs payload of piece requested by peer. 
		'''
		message_id = 8
		start = index* self.piece_length + offset
		with open(os.path.join(self.get_directory, self.filename), 'rb+') as torrent_file:
				torrent_file.seek(start)
				piece = torrent_file.read(length)

	