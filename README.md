Things I've learned so far:

Sockets: come in client, server, UDP and TCP varieties. I've coded up one of each and hey! Magic! I can send bytes back and forth to myself, or to others!

Unicode/Ascii/Latin-1/UTF-8: History of various forms of encoding, the eventual triumph of unicode, the difference between bytes, code points and characters. UTF-8 is boss, ascii/latin1/other/weird/things/cryllic/greek make really awful bugs. Don't use them.

Bencoding: A simple way to represent nested data structures as a single string. FOLLOW THE SPEC! metainfo files are utf-8 encoded!!!!! latin-1 breaks my bdecoder and makes kittens sad :(

regex: Regular expressions! These were awesome until I realised that there was an easier, more technically correct way to do things (not utf-8 decoding sha1) so I ditched most of the regex stuff, but I'm glad I learned it!

Get requests: 