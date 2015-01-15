import socket
import sys
def create_client_socket(IP, port, message):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_address = (IP, port)
	print(server_address)
	print('connecting to %s port %s' % server_address, file=sys.stderr)
	sock.connect(server_address)

	try:
		print('sending "%s"' % message, file=sys.stderr)
		sock.sendall(message)

		amount_received = 0
		amount_expected = len(message)

		data = sock.recv()
		amount_received += len(data)
		print('received "%s"' % data)

	finally:
		print('closing socket', sys.stderr)
		sock.close()
	return data
# create_client_socket('96.126.104.219', 63103, b'\x13BitTorrent protocol\x00\x00\x00\x00\x00\x00\x00\x00+\x15\xca+\xfdH\xcd\xd7m9\xecU\xa3\xab\x1b\x8aW\x18\n\t-TZ-0000-39576683547')