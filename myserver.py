import socket
import sys

HOST = '' # Symbolic name meaning all available interfaces
PORT = 8888 # Arbitrary non-privilaged PORT

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Socket created!'

try:
	s.bind((HOST, PORT))
except socket.error, msg:
	print 'Bind failed. Error Code: ' + str(msg[0]) + ' Message: ' + msg[1]
	sys.exit()

print "Socket bind complete"

s.listen(10)
print 'Socket now listening'

# keep talking to the client
while 1:
	# wait to accept a connection - blocking call
	conn, addr = s.accept()
	print 'Connected with' + addr[0] + ' : ' + str(addr[1])
	data = conn.recv(1024)
	conn.sendall(data)
	reply = 'OK...' + data
	if not data:
		break
	conn.sendall(reply)	

conn.close()
s.close()