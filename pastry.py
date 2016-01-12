#Pastry v0.1
#Written for Python 2.7.5

#Imports
import pyperclip
import time
import socket
import changeDetails #The settings dialog area, only one thing in there right now but that can change
import signal #Handle Ctrl + C
import sys #Exiting
import easygui as eg #Graphics
import json
from multiprocessing import Process
import zlib

#Setup variables
currentClipboard = pyperclip.paste()

#Get the users ID
#Do we have a config file?
try:
	#Yes we do
	open('settings.py')
except:
	#No we don't
	changeDetails.changeDetails()
import settings

#Send out the new clipboard
def sendClipboard(clipboard):
	#Hook up the multicast
	ANY = '0.0.0.0'
	MCAST_ADDR = '224.168.2.9'
	MCAST_PORT = 8946
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
	SENDERPORT=1501
	sock.bind((ANY,SENDERPORT))
	sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 255)

	#Send the clipboard
	copiedText = json.dumps({"id": settings.login['id'], "data": clipboard}).encode("utf-8")
	copiedText = zlib.compress(copiedText, 9)
	try:
		sock.sendto(codecs.encode(copiedText, (MCAST_ADDR,MCAST_PORT)))
	except Exception as e:
		eg.msgbox("There was an error sending this copy across the network.", "Pastry")
		print("Error: %s" % str(e))

	#End the connection
	sock.close()

def listen():
	global currentClipboard
	while 1:
		time.sleep(0.1)
		#Check for external messages
		ANY = '0.0.0.0'
		MCAST_ADDR = '224.168.2.9'
		MCAST_PORT = 8946
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
		sock.bind((ANY,MCAST_PORT))
		sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 255)
		status = sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(MCAST_ADDR)+socket.inet_aton(ANY))

		try:
			data, addr = sock.recvfrom(1024)
		except socket.error:
			pass
		else:
			data = zlib.decompress(data)
			data = json.loads(data)

			#Is this the clipboard we are looking for?
			if data['id'] == settings.login['id']:
				pyperclip.copy(data[''])
				currentClipboard = pyperclip.paste()
				# print(pyperclip.paste())

if __name__ == '__main__':
	#Start the listener
	listenerThread = Process(target=listen, daemon=True)
	listenerThread.start()

#Handle exit
def signal_handler(signal, frame):
	listenerThread.terminate()
	sys.exit()
signal.signal(signal.SIGINT, signal_handler)

while 1:
	#Check for clipboard changes every 100ms
	time.sleep(0.1)

	if pyperclip.paste() != currentClipboard:
		currentClipboard = pyperclip.paste()
		sendClipboard(currentClipboard)