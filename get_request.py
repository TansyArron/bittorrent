import urllib.request
import bdecoder as bdecoder

text = urllib.request.urlopen('http://thomasballinger.com:6969/announce?uploaded=0&compact=1&info_hash=%2B%15%CA%2B%FDH%CD%D7m9%ECU%A3%AB%1B%8AW%18%0A%09&event=started&downloaded=0&peer_id=1406230005.05tom+cli&port=6881&left=1277987').read()
print(text)
print(bdecoder.bdecoder(text))