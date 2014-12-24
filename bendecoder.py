
import re

def tokenize(data, match=re.compile(r"([idl])|($\d+):|(-?\d+)").match):
	i = 0
	while i < len(data):
		m = match(data, i) 		# Create match object "m" 
		s = m.group(m.lastindex)# index of last matched string
		i = m.end() 			# iterator moves to ending position of the matching string
		if m.lastindex == 2: 	# If the match is a string '(\d+):' :
			yield "s"			# yield the token "s" for string
			yield data[i:i+int(s)] #yield the whole string
			i = i + int(s) 		# increase the iterator by the length of the string
		else:
			yield s 			# yield the last matched string

def decode_item(next, token):
	if token == "i":
		#int: "i" + int + "e"
		data = int(next())
		end = next()
		if end != "e":
			raise ValueError("no closing 'e' on int", end)
	elif token == "s":
		#string: token = "s"
		data = next()
	elif token == "l" or token == "d":
		# container: "l" or "d" values "e"
		data = []
		tok = next()
		while tok != "e":
			data.append(decode_item(next, tok))
			tok = next()
		if token == "d":
			data = dict(zip(data[0::2], data[1::2]))
	else:
		raise ValueError(token)
	return data
def decode_int(byte_string):
	# Where string begins with 'i'
	int_re = re.compile(rb'[i](?P<digits>-?\d+)[e]')
	match = int_re.match(byte_string)
	if not match:
		import pdb; pdb.set_trace()
		raise Exception("Not a match")
	digits = match.group('digits')
	int_len = len(digits)
	int_bytes_start = 1
	int_bytes_end = 1 + int_len
	int_bytes = byte_string[int_bytes_start:int_bytes_end]
	decoded_int = int_bytes.decode("utf-8")
	return (decoded_int, int_bytes_end + 1)

def decode_string(byte_string):
	# where string begins with 'int:' 
	string_re = re.compile(rb'(?P<digits>\d+):')
	match = string_re.match(byte_string)
	if not match:
		# import pdb; pdb.set_trace()
		raise Exception("Not a match")
	digits = match.group('digits')
	str_len = int(digits)
	str_bytes_start = 1+len(digits)
	str_bytes_end = str_bytes_start + str_len + 1
	str_bytes = byte_string[str_bytes_start:str_bytes_end]
	decoded_str = str_bytes.decode("utf-8")
	return (decoded_str, str_bytes_end)

#   def decode(text):
# 	if text[0] == b"d":

# 	elif text[0] == b"l":
# 	elif text[0] == b"i":
# 	else:
# 	try:
# 		src = tokenize(text) #generates tokens/strings/ints in order
# 		data = decode_item(src.__next__, next(src))
# 		# for token in src: #look for more tokens
# 		# 	raise SyntaxError("trailing junk")
# 	except (AttributeError, ValueError, StopIteration) as e:
# 		raise (SyntaxError("syntax error")) from e
# 	return data
i = 'i255e'
print(decode_int(i.encode('utf-8')))

s = ':annoåunce'
print(type(str(len(s.encode('utf-8'))).encode('ascii') + s.encode('utf-8')))
# with open('./flagfromserver.torrent','rb') as f:
# 	flag = f.read()
# 	print(decode(flag))
	# decode(flag)
# print(decode(flag))
# print(decode('i14e'))