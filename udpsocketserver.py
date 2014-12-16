import socket
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('localhost', 8888)
print('starting up on %s port %s' % server_address, file=sys.stderr)
sock.bind(server_address)

while True:
	print('waiting to recieve message', file=sys.stderr)
	data, address = sock.recvfrom(4096)

	print('received %s bytes from %s' % (len(data), address), file = sys.stderr)
	print(sys.stderr, data.decode('utf-8'))

	if data:
		sent = sock.sendto(data, address)
		print('sent %s bytes back to %s' % (sent, address), sys.stderr)
