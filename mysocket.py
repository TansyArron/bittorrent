import socket
import sys
# Create a socket with:
# Address Family: AF_INET (IPv4)
# Type: SOCK_STREAM (connection oriented TCP protocal)
try:
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error, msg:
	print 'Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1] 
	sys.exit()

print 'Socket Created!'

host = 'www.google.com'
port = 80

try:
	remote_ip = socket.gethostbyname( host )

except socket.gaierror:
	print 'Hostname could not be resolved. Exiting'
	sys.exit()

print 'Ip address of ' + host + ' is ' + remote_ip

s.connect((remote_ip, port))

print 'Socket connected to ' + host + ' on ip ' + remote_ip