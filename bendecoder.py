
import re

def tokenize(data, match=re.compile("([idel])|(\d+):|(-?\d+)").match):
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
			print("Here!")
			data.append(decode_item(next, tok))
			tok = next()
		if token == "d":
			data = dict(zip(data[0::2], data[1::2]))
	else:
		raise ValueError(token)
	return data

def decode(text):
	# src = tokenize(text)
	# data = decode_item(next(src), next(src))
	try:
		src = tokenize(text) #generates tokens/strings/ints in order
		data = decode_item(src.__next__, next(src))
		# for token in src: #look for more tokens
		# 	raise SyntaxError("trailing junk")
	except (AttributeError, ValueError, StopIteration) as e:
		raise (SyntaxError("syntax error")) from e
	return data

# print(list(tokenize("4:spam")))
# print(list(tokenize("i3e")))
flag = open('./flagfromserver.torrent','r', encoding='latin')
flag = flag.read()
print(decode(flag))
# print(decode('i14e'))