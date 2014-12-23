# Bencode

class BencodeError(Exception):
	def __init__(self, mode, value, data):
		self.mode = mode
		self.value = value
		self.data = data

	def __str__(self):
		return self.mode + self.value + data

def encode_int(data):
	# Int = i+int+e
	if type(data) == int:
		return 'i'+ str(data) + 'e'

def decode_int(data):
	return data[1:-1]

def encode_string(data):
	# String = len(string):string
	if type(data) == str:
		return str(len(data))+':'+data

def decode_string(data):
	return data[2:]

def encode_list(data):
	# Lists = l+(bencoded elements)+e
	if type(data) == list:
		temp = ''.join(encode(x) for x in data)
		return 'l'+temp+'e'

def decode_list(data):
	pass

def encode_dict(data):
	# Dictionaries = d+(bencoded elements)+e. 
	# Keys must be strings and appear in sorted order
	if type(data) == dict:
		temp = [encode_string(key) + encode(data[key]) for key in sorted(data.keys())]
		return 'd'+ ''.join(temp)+'e'

def decode_dict(data):
	pass

encode_functions = {
	int: encode_int,
	str: encode_string,
	list: encode_list,
	dict: encode_dict
}		

decode_functions = {
	'i': decode_int,
	's': decode_string,
	'l': decode_list,
	'd': decode_dict
}
def encode(data):
	try:
		return encode_functions[type(data)](data)
	except KeyError:
		raise BencodeError("Encode", "Unknown data type", data)

def decode(data):
	if data[0].isdigit():
		token = 's'
	else:
		token = data[0]
	try:
		return decode_functions[token](data)
	except KeyError:
		raise BencodeError("Decode", "Unknown data type", data)

encodedInt = encode(5)
encodedString = encode('what')
encodedList = encode(['some', 'things', 5, 7, 8])
encodedDict1 = encode({'four':4, 'six':6, 'eight':8})
encodedDict2 = encode({'spam':['a','b']})

print(decode(encodedString))
print(decode(encodedInt))