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

		data = sock.recv(146)
		amount_received += len(data)
		print('received "%s"' % data)

	finally:
		print('closing socket', sys.stderr)
		sock.close()
	return data