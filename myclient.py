import socket
import sys
def create_client_socket(IP, port):
	# Create a socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Connect the socket to the port where the server is listening
	server_address = (IP, port)
	print(server_address)
	print('connecting to %s port %s' % server_address, file=sys.stderr)
	sock.connect(server_address)

	try:
		# send data
		message = 'This is the message. It will be repeated'
		print('sending "%s"' % message, file=sys.stderr)
		sock.sendall(message.encode('utf-8'))

		# look for the response
		amount_received = 0
		amount_expected = len(message)

		# while amount_received < amount_expected:
		data = sock.recv(16)
		amount_received += len(data)
		print('received "%s"' % len(data))#data.decode('utf-8'), file=sys.stderr)

	finally:
		print('closing socket', sys.stderr)
		sock.close()