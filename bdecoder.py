import re

def decode_int(byte_string):
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
	decoded_int = int_bytes#.decode("utf-8")
	remaining_bytes = byte_string[int_bytes_end + 1:]
	return decoded_int, remaining_bytes

def decode_string(byte_string):
	string_re = re.compile(rb'(?P<digits>\d+):')
	match = string_re.match(byte_string)
	if not match:
		raise Exception("Not a match")
	digits = match.group('digits')
	str_len = int(digits)
	str_bytes_start = 1+len(digits)
	str_bytes_end = str_bytes_start + str_len
	str_bytes = byte_string[str_bytes_start:str_bytes_end]
	decoded_str = str_bytes#.decode("utf-8")
	remaining_bytes = byte_string[str_bytes_end:]
	return decoded_str, remaining_bytes

def decode_dict(byte_string):
	key_value_list, remaining_bytes = decode_list(byte_string)
	decoded_dict = dict(zip(key_value_list[0::2], key_value_list[1::2]))
	if len(remaining_bytes) == 0:
		ben_string = b'd' + byte_string
	else:
		ben_string = b'd' + byte_string[:-len(remaining_bytes)]
	decoded_dict['ben_string'] = ben_string
	return decoded_dict, remaining_bytes

def decode_list(byte_string):
	remaining_bytes = byte_string
	this_list = []
	while remaining_bytes[0] != ord(b'e'):
		value, remaining_bytes = decode(remaining_bytes)
		this_list.append(value)
	return this_list, remaining_bytes[1:]

def decode(byte_string):

	if byte_string[0] == ord(b'd'):
		return decode_dict(byte_string[1:])
	elif byte_string[0] == ord(b'l'):		
		return decode_list(byte_string[1:])
	elif byte_string[0] == ord(b'i'):		
		return decode_int(byte_string)
	elif byte_string[:1] in b'123456789':						
		return decode_string(byte_string)
	else:
		raise Exception("Malformed data")

def bdecoder(byte_string):
	dict_check = re.compile(rb'(^d)')
	match = dict_check.match(byte_string)
	if not match:
		raise Exception("File does not start with dictionary")

	return decode(byte_string)[0]

# with open('flagfromserver.torrent', 'rb') as f:
# 	info_dictionary = bdecoder(f.read())
# 	print(info_dictionary['info'])
	
# pudb.set_trace()
# print(bdecoder(b'd4:spaml1:a1:bee'))


