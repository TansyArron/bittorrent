import socket
import sys

#Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('localhost', 8888)
message = "this is the message. It will be repeated"

try:
	# send data
	print('sending %s' % message, file=sys.stderr)
	sent = sock.sendto(message.encode('utf-8'),server_address)

	# receive response
	print('waiting to receive', file=sys.stderr)
	data, server = sock.recvfrom(4096)
	print('received %s' %data.decode('utf-8'), file=sys.stderr)

finally:
	print('closing socket', file=sys.stderr)
	sock.close()
