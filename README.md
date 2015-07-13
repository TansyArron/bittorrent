BitTorrent Client

Command line bitTorrent client written in Python 3.4. Uses asyncio to handle multiple peer connections. Currently handles single file torrents with no protocol extensions. Does not yet seed.

Usage:

python manager.py /path/to/torrent_file.torrent

TODO:
- Bendecode: handle trailing junk
- Optimize get_next_piece: Currently chooses the lowest indexed piece it needs.
- handle extensions for peer IP/port formatting
- handle extensions for varying hash functions	
- Create bitfield from file/meta_info or use torrent.have
- Construct 'have' messages
- Construct bitfield messages
- Listen for peers
- Respond to piece requests: Given index, length and offset 			within piece, get the requested bytes, form a "piece" 			message and send to peer
- Handle multi-file torrents

TIL:

Sockets: come in client, server, UDP and TCP varieties. I've coded up one of each and hey! Magic! I can send bytes back and forth to myself, or to others!

Unicode/Ascii/Latin-1/UTF-8: History of various forms of encoding, the eventual triumph of unicode, the difference between bytes, code points and characters. UTF-8 is boss, ascii/latin1/other/weird/things/cryllic/greek make really awful bugs. Don't use them.

Bencoding: A simple way to represent nested data structures as a single string. FOLLOW THE SPEC! metainfo files are utf-8 encoded!!!!! latin-1 breaks my bdecoder and makes kittens sad :(

Regex: Regular expressions! These were awesome until I realised that there was an easier, more technically correct way to do things (not utf-8 decoding sha1) so I ditched most of the regex stuff, but I'm glad I learned it!

Get requests/url encoding: the requests library does everything! Though I did originally construct the message myself and use urllibs url encoding. Still trying to get the requests futures to play nicely with asyncio but I think it's a lost cause.

IP address: easy to get your local IP address with ifconfig, getting your external IP requires contacting a website!

Callbacks: A thing that exist! They make the code harder to read but Oh man they're so handy!

Yield and Yield from: learned how to write an equivalent of yield from using yield, next, and send. Really glad I don't have to do that every time I use yield from, but it makes more sense now. Generators are awesome sauce.

Asyncio: Confusing, but it makes all my connections happen super fast. Keeps the code easier to read than endless callbacks!

Read/write: reading and writing to/from files was all new to me a month ago. Seek has been super helpful in getting all the right pieces in all the right places.