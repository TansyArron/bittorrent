import sys
import urllib.request
import urllib.parse
import bdecoder as bdecoder
import hashlib as hashlib
import myclient as myclient

'''
Generate working url request
'''

def get_peer_info():
	meta_info_file = sys.argv[1]
	with open(meta_info_file, 'rb') as f:
		meta_info_dict = bdecoder.bdecoder(f.read())
	return meta_info_dict

def create_tracker_query(meta_info_dict):
	info = meta_info_dict[b'info']
	ben_string = info['ben_string']
	info_hash = hashlib.sha1(ben_string).digest()
	params = {
		'info_hash' : info_hash,
		'event' : "started",	# event- default "started"
		'downloaded' : '0',		# number of bytes downloaded
		'peer_id' : '-TZ-0000-00000000000',
		'port' : '6881',
		'left' : info[b'length'],	# number of bytes left to download, default number of bytes in file
	}
	tracker_url = meta_info_dict[b'announce'].decode('utf-8')
	query = urllib.parse.urlencode(params, doseq=False, safe='', encoding=None, errors=None)
	return '{}?{}'.format(meta_info_dict[b'announce'].decode('utf-8'), query)

def create_peer_dict(raw_peer_info):
	peer_info = raw_peer_info[b'peers']
	peers = [peer_info[i:i+6] for i in range(0, len(peer_info), 6)]
	peer_dict = {
		'.'.join(str(i) for i in peer[:4]): int.from_bytes(peer[4:], byteorder='big')
		for peer in peers
	}
	return peer_dict

meta_info_dict = get_peer_info()
tracker_query = create_tracker_query(meta_info_dict)
raw_peer_info = bdecoder.bdecoder(urllib.request.urlopen(tracker_query).read())
peer_dict = create_peer_dict(raw_peer_info)
for key, value in peer_dict.items():
	myclient.create_client_socket(key, value)






