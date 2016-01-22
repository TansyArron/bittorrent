# Message ID

CHOKE = 0
UNCHOKE = 1
INTERESTED = 2
NOT_INTERESTED = 3
HAVE = 4
BITFIELD = 5
REQUEST = 6
PIECE = 7
CANCEL = 8
PORT = 9

def get_message_name(id):
      return message_names[id]

def get_message_id(name):
      return message_names.index(name)

PIECE_LENGTH = 16384
piece v/s block: In this document, a piece refers to a portion of the downloaded data that is described in the metainfo file, which can be verified by a SHA1 hash. A block is a portion of data that a client may request from at least one peer. Two or more blocks make up a whole piece, which may then be verified.