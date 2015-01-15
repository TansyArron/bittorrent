'''
Construct a handshake
https://wiki.theory.org/BitTorrentSpecification#Handshake

The handshake is a required message and must be the first message 
transmitted by the client. It is (49+len(pstr)) bytes long.
handshake: <pstrlen><pstr><reserved><info_hash><peer_id>

pstrlen: string length of <pstr>, as a single raw byte
pstr: string identifier of the protocol
reserved: eight (8) reserved bytes. All current implementations 
use all zeroes.
info_hash: 20-byte SHA1 hash of the info key in the metainfo file. 
This is the same info_hash that is transmitted in tracker requests.
peer_id: 20-byte string used as a unique ID for the client. This is 
usually the same peer_id that is transmitted in tracker requests 
(but not always e.g. an anonymity option in Azureus).
In version 1.0 of the BitTorrent protocol, pstrlen = 19, and 
pstr = "BitTorrent protocol".

for flagfromserver.torrent handshake should look like:
'\x13BitTorrent protocol\x00\x00\x00\x00\x00\x00\x00\x00+\x15\xca+\xfdH\xcd\xd7m9\xecU\xa3\xab\x1b\x8aW\x18\n\t-TZ-0000-00000000000'


'''

def handshake(peer_id,
			 info_hash, 
			 pstrlen=b'\x13',
			 pstr=b'BitTorrent protocol',
			 reserved=b'\x00\x00\x00\x00\x00\x00\x00\x00'):
	parts = [pstrlen, pstr, reserved, info_hash, peer_id]
	handshake_string = b''.join(parts)
	return handshake_string

