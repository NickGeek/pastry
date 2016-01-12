#Pastry v1.0
#Written for Python 3

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

ANY = '0.0.0.0'
MCAST_ADDR = '224.1.1.1'
MCAST_PORT = 2679
listenSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
listenSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listenSock.bind(('', MCAST_PORT))
listenSock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 255)
listenSock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(MCAST_ADDR)+socket.inet_aton(ANY))

#Send out the new clipboard
def sendClipboard(clipboard):
	#Hook up the multicast
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
	sock.bind(('', 2678))
	sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)

	#Send the clipboard
	try:
		if isinstance(clipboard, bytes):
			clipboard = clipboard.decode('utf-8')
		copiedText = json.dumps({"id": settings.login['id'], "data": clipboard}).encode("utf-8")
		copiedText = zlib.compress(copiedText, 9)
		
		#Make sure we don't send more than the buffer
		if sys.getsizeof(copiedText) < 10240:
			sock.sendto(copiedText, (MCAST_ADDR,MCAST_PORT))
		else:
			eg.msgbox("Pastry can't send that much data. Try sending the text in segments.", "Pastry")
	except Exception as e:
		eg.msgbox("There was an error sending your copy. {0}".format(e), "Pastry")

	#End the connection
	sock.close()

def listen():
	global currentClipboard
	global listenSock
	while 1:
		time.sleep(0.1)
		try:
			data = listenSock.recvfrom(10240)[0]
		except socket.error:
			pass
		else:
			try:
				data = zlib.decompress(data).decode("utf-8")
				data = json.loads(data)
				# print(data)

				#Is this the clipboard we are looking for?
				if data['id'] == settings.login['id']:
					pyperclip.copy(data['data'])
					currentClipboard = pyperclip.paste()
					# print(pyperclip.paste())
			except Exception as e:
				print("Listening Error: %s" % str(e))

if __name__ == '__main__':
	#Start the listener
	listenerThread = Process(target=listen, daemon=True)
	listenerThread.start()

#Handle exit
def signal_handler(signal, frame):
	global listenSock
	listenSock.close()
	listenerThread.terminate()
	sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

while 1:
	#Check for clipboard changes every 100ms
	time.sleep(0.1)

	if pyperclip.paste() != currentClipboard:
		currentClipboard = pyperclip.paste()
		sendClipboard(currentClipboard)
