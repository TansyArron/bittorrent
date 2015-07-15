import requests
import bencoding

class Tracker():
	''' Handles information from the tracker. Creates a list of peers in the form
		[(ip, port),]
	'''
	def __init__(self, announce, tracker_params):
		self.announce = announce
		self.tracker_params = tracker_params
		self.tracker_info = self.get_info_from_tracker()
		self.peer_info = self.tracker_info[b'peers']
		self.peer_list = self.parse_peer_address()
		self.tracker_id = None

	def get_info_from_tracker(self):
		'''	Construct tracker request and return decoded response.
			Spec here: https://wiki.theory.org/BitTorrentSpecification#Tracker_Request_Parameters
		'''
		tracker_info = requests.get(self.announce, params=self.tracker_params, stream=True).raw.read()
		return bencoding.decode(tracker_info)

	def update_tracker_id(self):
		''' if the tracker sends an ID, update tracker_id. This is used for ongoing communication
			with tracker while seeding.
		'''
		if 'tracker_id' in self.tracker_info:
			self.tracker_id = self.tracker_info['tracker_id']
			
	def parse_peer_address(self):
		''' The tracker response contains the IPs and ports for active peers. 
			These can be in two forms:
			Dictionary model: A list of dictionaries, each with the following keys:
				peer id: peer's self-selected ID, as described above for the tracker request (string)
				ip: peer's IP address either IPv6 (hexed) or IPv4 (dotted quad) or DNS name (string)
				port: peer's port number (integer)
			Binary model: Instead of using the dictionary model described above, the peers value 
				may be a string consisting of multiples of 6 bytes. First 4 bytes are the IP address 
				and last 2 bytes are the port number. All in network (big endian) notation.
		'''		
		peer_list = []
		if isinstance(self.peer_info, list):
			# Dictionary Model
			for peer in self.peer_info:
				peer_list.append(peer_dict[ip], peer_dict[port])
		
		else:
			# Binary Model
			peers = [self.peer_info[i:i+6] for i in range(0, len(self.peer_info), 6)]
			for peer in peers:
				ip = '.'.join(str(i) for i in peer[:4])
				port = int.from_bytes(peer[4:], byteorder='big')
				peer_list.append((ip, port))
		print('peer_list', peer_list)
		return peer_list