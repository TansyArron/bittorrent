from asyncio import get_event_loop, coroutine
from definitions import get_message_id, get_message_name

class MessageHandler():
  def __init__(self, torrent, torrent_downloader):
    self.torrent = torrent
    self.torrent_downloader = torrent_downloader
    self.handshake = self.handshake()
    self.io_loop = get_event_loop()
    self.message_func_name = [
      self.choke,
      self.unchoke,
      self.interested,
      self.not_interested,
      self.have,
      self.bitfield,
      self.request,
      self.piece,
      self.cancel, 
      self.port,
    ]

  def handshake(self):
    ''' construct handshake bytestring in form:
      <19><'BitTorrent protocol'><00000000><ID>
      Spec here: https://wiki.theory.org/BitTorrentSpecification#Handshake
    '''
    pstrlen = b'\x13'
    pstr = b'BitTorrent protocol'
    reserved = b'\x00\x00\x00\x00\x00\x00\x00\x00'
    parts = [pstrlen, pstr, reserved, self.torrent.info_hash, self.torrent.peer_id.encode()]
    handshake_string = b''.join(parts)
    return handshake_string

  def check_handshake(self, peer, handshake_bytes):
    extension = handshake_bytes[20:28]
    if handshake_bytes[28:48] != self.handshake[28:48]:
      peer.sock.close()
      raise Exception('Peer returned invalid info_hash. Closing socket')  
      # TODO: remove peer from torrent.peer_list and manager.connected_peers
    else:
      peer.connected = True
      peer.io_loop.create_task(peer.listen())
      peer.buffer = peer.buffer[68:]

  def dispatch_message(self, peer, message_bytes):
    ''' 
      Pass all messages to their appropriate functions.
    '''
    message_id = message_bytes[0]
    message_slice = message_bytes[1:]
    print("Received Message: ", message_id)
    self.message_func_name[message_id](peer, message_slice)

  def choke(self, peer, message_bytes):
    '''choke: <len=0001><id=0>
    ''' 
    peer.state['peer_choking'] = True 
      
  def unchoke(self, peer, message_bytes):
    ''' unchoke: <len=0001><id=1>
    ''' 
    peer.state['peer_choking'] = False
    
  def interested(self, peer, message_bytes):
    ''' interested: <len=0001><id=2>
    '''
    peer.state['peer_interested'] = True
      
  def not_interested(self, peer, message_bytes):
    ''' not interested: <len=0001><id=3>
    '''
    peer.state['peer_interested'] = False
    
  def have(self, peer, message_bytes):
    ''' Have message is the index of a piece the peer has. Updates
      peer.has_pieces.
      have: <len=0005><id=4><piece index>
    '''
    piece_index = int.from_bytes(message_bytes, byteorder='big')
    peer.has_pieces[piece_index] = True
    
  def bitfield(self, peer, message_bytes):
    ''' formats each byte into binary and updates peer.has_pieces list
      appropriately.
    '''
    bitstring = ''.join('{0:08b}'.format(byte) for byte in message_bytes)
    peer.has_pieces = [bool(int(c)) for c in bitstring]
    self.torrent_downloader.pieces_changed_callback(peer)
    
  def request(self, peer, message_bytes):
    ''' <len=0013><id=6><index><offset><length>
      Calls torrent.get_piece() and sends relevent piece to peer.
    '''
    index = message_bytes[:4]
    piece_offset = message_bytes[4:8]
    length = message_bytes[8:]
    payload_bytes = self.torrent_downloader.construct_request_payload(index, offset, length, peer)
    
  def piece(self, peer, message_bytes):
    ''' Piece message is constructed:
      <len=9 + X><id=8><index><offset><piece bytes>
    '''
    piece_index = message_bytes[:4]
    piece_begins = message_bytes[4:8]
    piece = message_bytes[8:]
    self.torrent.check_piece_callback(piece, piece_index, peer)
    self.torrent_downloader.choose_piece(peer)
    

  def cancel(self, peer, message_bytes):
    '''cancel: <len=0013><id=8><index><begin><length>
    '''
    pass

  def port(self, peer, message_bytes):
    ''' port: <len=0003><id=9><listen-port>
    '''
    pass

  def construct_request_payload(self, peer, piece_index, piece_offset=0, piece_length=16384):
    ''' Constructs the payload of a request message for piece_index.
      Calls peer.send_message to finish construction and send.
    '''
    piece_index_bytes = piece_index.to_bytes(4, byteorder='big')
    piece_begin = piece_offset.to_bytes(4, byteorder='big')
    piece_length = piece_length.to_bytes(4, byteorder='big')
    payload = b''.join([piece_index_bytes, piece_begin, piece_length])
    self.io_loop.create_task(self.send_message(peer, 6, payload))

  @coroutine
  def send_message(self, peer, message_id, payload_bytes=b''):
    ''' Send message and update self.state if necessary
    
    messages in the protocol take the form of 
    <length prefix><message ID><payload>. The length prefix is a four byte 
    big-endian value. The message ID is a single decimal byte. 
    The payload is message dependent.
    '''
    print("Sending message: ", message_id)
    length_bytes = (1 + len(payload_bytes)).to_bytes(4, byteorder='big')
    message_id_bytes = message_id.to_bytes(1, byteorder='big')
    elements = [length_bytes, message_id_bytes, payload_bytes]
    message_bytes = b''.join(elements)
    yield from peer.io_loop.sock_sendall(peer.sock, message_bytes)
    if message_id in [0,1,2,3]:
      self.update_state(peer, message_id)

  def update_state(self, peer, message_id):
    if message_id == 0:
      peer.state['am_choking'] = True
    elif message_id == 1:
      peer.state['am_choking'] = False
    elif message_id == 2:
      peer.state['am_interested'] = True
    elif message_id == 3:
      peer.state['am_interested'] = False
  