# Bencode
def encode_int(data):
	# Int = i+int+e
	if type(data) == int:
		return 'i'+ str(data) + 'e'

def encode_string(data):
	# String = len(string):string
	if type(data) == str:
		return str(len(data))+':'+data

def encode_list(data):
	# Lists = l+(bencoded elements)+e
	if type(data) == list:
		temp = ''.join(encode(x) for x in data)
		return 'l'+temp+'e'

def encode_dict(data):
	# Dictionaries = d+(bencoded elements)+e. 
	# Keys must be strings and appear in sorted order
	if type(data) == dict:
		temp = [encode_string(key) + encode(data[key]) for key in sorted(data.keys())]
		return 'd'+ ''.join(temp)+'e'

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

print(encode({'four':4, 'six':6, 'eight':8}))
print(encode({'spam':['a','b']}))