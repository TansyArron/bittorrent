# Bencode

class BencodeError(Exception):
	def __init__(self, mode, value, data):
		self.mode = mode
		self.value = value
		self.data = data

	def __str__(self):
		return 'mode: {self.mode}\nvalue: {self.value}\ndata: {self.data}'.format(self=self)

def encode_int(i):
	# Int = i+int+e
	return 'i{}e'.format(i)

def encode_string(s):
	# String = len(string):string
	return '{}:{}'.format(len(s), s)

def encode_list(l):
	# Lists = l+(bencoded elements)+e
	encoded_str = ''.join(encode(x) for x in l)
	return 'l{}e'.format(encoded_str)

def encode_dict(d):
	# Dictionaries = d+(bencoded elements)+e. 
	# Keys must be strings and appear in sorted order
	dictionary = [encode_string(key) + encode(d[key]) for key in sorted(d.keys())]
	return 'd{}e'.format(''.join(dictionary))

encode_functions = {
	int: encode_int,
	str: encode_string,
	list: encode_list,
	dict: encode_dict
}		

def encode(data):
	try:
		return encode_functions[type(data)](data)
	except KeyError:
		raise BencodeError("Encode", "Unknown data type", data)

encodedInt = encode(5)
encodedString = encode('what')
encodedList = encode(['some', 'things', 5, 7, 8])
encodedDict1 = encode({'four':4, 'six':6, 'eight':8})
encodedDict2 = encode({'spam':['a','b']})

print(encodedList)
print(encodedDict1)
print(encodedDict2)
