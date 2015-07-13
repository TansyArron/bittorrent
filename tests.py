import unittest
import message_handler

# # Message Handling



# # Recieve Messages:

# dispatch_messages_from_buffer():
# in: <four bytes bigendian length of message><message>
# call dispatch_message on recieved message and remove message from buffer. (if length == 0 loop not necessary?)

# dispatch_messages(message_bytes):
# in: <id><message>
# out: keep_alive, choke, unchoke etc.

# keep_alive():
class Keep_Alive(unittest.TestCase):
    def test_dispatch_messages(self):
        self.assertEqual(message_handler.keep_alive(), 'KEEP ALIVE')

if __name__ == '__main__':
    unittest.main()
# choke():
# change state

# unchoke:
# change state

# interested()
# change state

# not_interested()
# change state

# have()
# change self.has_piece

# bitfield(message_bytes)
# update self.has_pieces

# request(message_bytes)
# call torrent.get_piece

# piece(message_bytes)
# if piece is complete, call torrent.check_piece_callback, 
# otherwise add to existing piece and continue.

# cancel()

# port()


# # Construct and Send Messages:


# constuct_message(id, payload_bytes)
# test keep alive - piece.

# send_message():
# check message sent, call update_state()

# update_state():
# check state after id's 0-3.



# # Peer Class

# connect(message):
# open socket, send message. 
# close socket on reciept of 0 bytes
# update buffer
# check_handshake()

# check_handshake(handshake_bytes)
# if not match, raise exception
# else update self.connected, update buffer, start io_loop task.

# listen():
# close socket on reciept of 0 bytes, update self.connected.
# otherwise update buffer with new bytes.



