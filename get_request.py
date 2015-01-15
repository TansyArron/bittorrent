import sys
import urllib.request
import urllib.parse
import bdecoder as bdecoder
import hashlib as hashlib
import myclient as myclient
import handshake as handshake

'''
Generate working url request
'''

def parse_meta_info():
	meta_info_file = sys.argv[1]
	with open(meta_info_file, 'rb') as f:
		meta_info_dict = bdecoder.bdecoder(f.read())
	return meta_info_dict

def create_tracker_query(meta_info_dict):
	'''TODO: handle multiple file downloads
	'''
	info = meta_info_dict[b'info']
	ben_string = info['ben_string']
	info_hash = hashlib.sha1(ben_string).digest()
	print(info.keys())
	params = {
		'info_hash' : info_hash,
		'event' : "started",	# event- default "started"
		'downloaded' : '0',		# number of bytes downloaded
		'peer_id' : b'-TZ-0000-00000000000',
		'port' : '6881',
		# 'left' : info[b'length'],	# number of bytes left to download, default number of bytes in file
	}
	tracker_url = meta_info_dict[b'announce'].decode('utf-8')
	query = urllib.parse.urlencode(params, doseq=False, safe='', encoding=None, errors=None)
	handshake_string = handshake.handshake(params['peer_id'], info_hash)
	return ('{}?{}'.format(tracker_url, query), handshake_string)

def create_peer_dict(raw_peer_info):
	peer_info = raw_peer_info[b'peers']
	peers = [peer_info[i:i+6] for i in range(0, len(peer_info), 6)]
	peer_dict = {
		'.'.join(str(i) for i in peer[:4]): int.from_bytes(peer[4:], byteorder='big')
		for peer in peers
	}
	return peer_dict

meta_info_dict = parse_meta_info()
tracker_query, handshake_string = create_tracker_query(meta_info_dict)
raw_peer_info = bdecoder.bdecoder(urllib.request.urlopen(tracker_query).read())
peer_dict = create_peer_dict(raw_peer_info)
# for key, value in peer_dict.items():
# 	peer_response = myclient.create_client_socket(key, value, handshake_string)
peer_response = myclient.create_client_socket('96.126.104.219', 63103, handshake_string)
if peer_response[28:48] == handshake_string[28:48]:
	#create peer object
	print("YAY! A PEER!!!")
else:
	print("not a match")
# myclient.create_client_socket('96.126.104.219', 63103, handshake_string)
