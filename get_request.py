import urllib.request
import urllib.parse
import bdecoder as bdecoder
import hashlib as hashlib
'''
Generate working url request
It should look like:
http://thomasballinger.com:6969/announce?uploaded=0&compact=1&info_hash=%2B%15%CA%2B%FDH%CD%D7m9%ECU%A3%AB%1B%8AW%18%0A%09&event=started&downloaded=0&peer_id=1406230005.05tom+cli&port=6881&left=1277987
'''
def get_peer_info():
# text = urllib.request.urlopen('http://thomasballinger.com:6969/announce?uploaded=0&compact=1&info_hash=%2B%15%CA%2B%FDH%CD%D7m9%ECU%A3%AB%1B%8AW%18%0A%09&event=started&downloaded=0&peer_id=1406230005.05tom+cli&port=6881&left=1277987').read()
# print(text)
	with open('flagfromserver.torrent', 'rb') as f:
	# sha1 hash bencoded info dictionary
	# url encoded hash should match: %2B%15%CA%2B%FDH%CD%D7m9%ECU%A3%AB%1B%8AW%18%0A%09
		dictionary = bdecoder.bdecoder(f.read())
		info = dictionary[b'info']
		ben_string = info['ben_string']
		# ben_slice = ben_string[71]
		# print(ben_slice)
		info_hash = hashlib.sha1(ben_string)
		# print(info_hash.digest())
		# print('info_hash', info_hash)
		# print('should be:','info_hash=%2B%15%CA%2B%FDH%CD%D7m9%ECU%A3%AB%1B%8AW%18%0A%09')
		

		params = {
			'info_hash' : '%2B%15%CA%2B%FDH%CD%D7m9%ECU%A3%AB%1B%8AW%18%0A%09',
			'event' : "started",	# event- default "started"
			'downloaded' : '0',		# number of bytes downloaded
			'peer_id' : '-TZ-0000-00000000000',
			'port' : '6881',
			'left' : info[b'length'].decode('utf-8'),	# number of bytes left to download, default number of bytes in file
			}

		tracker_url = dictionary[b'announce'].decode('utf-8') + '?'
		url_elems = []
		for key in params:
			url_elems.append(key + '=' + params[key])
		url_add = '&'.join(url_elems)	
		tracker_url += url_add
		# print(tracker_url)
		peer_info = urllib.request.urlopen(tracker_url).read()
		# print(peer_info)
		return bdecoder.bdecoder(peer_info)

print(get_peer_info())

