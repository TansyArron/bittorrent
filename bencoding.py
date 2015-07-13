'''Bencoding for BitTorrent.

string:     <integer length><:><string>
integer:    <i><integer><e>
list:       <l><list><e>
dictionary: <d><sorted dictionary><e>

Full spec can be found here:
https://wiki.theory.org/BitTorrentSpecification#Bencoding
'''

class BencodeError(Exception):
    def __init__(self, mode, value, data):
        self.mode = mode
        self.value = value
        self.data = data

    def __str__(self):
        return 'mode: {self.mode}\nvalue: {self.value}\ndata: {self.data}'.format(self=self)


'''ENCODER
'''

def encode_int(i):
    # Int = i+int+e
    return 'i{}e'.format(i)

def encode_string(s):
    # String = len(string):string
    return '{}:{}'.format(len(s), s)

def encode_list(l):
    # Lists = l+(bencoded elements)+e
    encoded_str = ''.join(bencode(x) for x in l)
    return 'l{}e'.format(encoded_str)

def encode_dict(d):
    # Dictionaries = d+(bencoded elements)+e. 
    # Keys must be strings and appear in sorted order
    dictionary = [encode_string(key) + bencode(d[key]) for key in sorted(d.keys())]
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


'''DECODER
'''
import re
import requests

def decode_int(byte_string):
    int_re = re.compile(rb'[i](?P<digits>-?\d+)[e]')
    match = int_re.match(byte_string)
    if not match:
        raise BencodeError("Decode Int", "Expected 'i' <some digits> 'e', received:", byte_string[:10])
    digits = match.group('digits')
    int_len = len(digits)
    int_bytes_start = 1
    int_bytes_end = 1 + int_len
    int_bytes = byte_string[int_bytes_start:int_bytes_end]
    remaining_bytes = byte_string[int_bytes_end + 1:]
    return int_bytes, remaining_bytes

def decode_string(byte_string):
    string_re = re.compile(rb'(?P<digits>\d+):')
    match = string_re.match(byte_string)
    if not match:
        raise BencodeError("Decode String", "Expected <some digits> ':' <some string>, received:", byte_string[:10])
    digits = match.group('digits')
    str_len = int(digits)
    str_bytes_start = 1+len(digits)
    str_bytes_end = str_bytes_start + str_len
    str_bytes = byte_string[str_bytes_start:str_bytes_end]
    remaining_bytes = byte_string[str_bytes_end:]
    return str_bytes, remaining_bytes

def decode_dict(byte_string):
    ''' Decode dictionary and create a key value pair of 'ben_string': encoded dictionary
        for use in Torrent.bencoded_info_dict hash matching
    '''
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
        value, remaining_bytes = type_handler(remaining_bytes)
        this_list.append(value)
    return this_list, remaining_bytes[1:]

def type_handler(byte_string):
    if byte_string[0] == ord(b'd'):
        return decode_dict(byte_string[1:])
    elif byte_string[0] == ord(b'l'):       
        return decode_list(byte_string[1:])
    elif byte_string[0] == ord(b'i'):       
        return decode_int(byte_string)
    elif byte_string[:1] in b'0123456789':                      
        return decode_string(byte_string)
    else:
        raise BencodeError("Type Handler", "Expected d, l, i or int. recieved:", byte_string[:10])

def decode(byte_string):
    dict_check = re.compile(rb'(^d)')
    match = dict_check.match(byte_string)
    if not match:
        raise BencodeError("Decode", "Malformed Data", byte_string)
    return type_handler(byte_string)[0]
