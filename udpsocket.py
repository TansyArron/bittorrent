import __future__
import socket
import sys

# Create socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ('localhost', 8888)
print >>sys.stderr, "starting up on %s port %s" % server_address
sock.bind(server_address)

while True:
	print >>sys.stderr