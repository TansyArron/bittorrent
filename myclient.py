import socket
import sys

# Create a socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('localhost', 8888)
print('connecting to %s port %s' % server_address, file=sys.stderr)
sock.connect(server_address)

try:
	# send data
	message = 'This is the message. It will be repeated'
	print('sending "%s"' % message, file=sys.stderr)
	sock.sendall(message.encode('utf-8'))

	# look for the response
	ammount_received = 0
	ammount_expected = len(message)

	while ammount_received < ammount_expected:
		data = sock.recv(16)
		ammount_received += len(data)
		print('received "%s"' % data, file=sys.stderr)

finally:
	print('closing socket', sys.stderr)
	sock.close()