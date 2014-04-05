#Pastry v0.1
#Written for Python 2.7.5

#Imports
import pyperclip #Awesome library for cross-platform copy/paste
import time #I love importing time. It sounds very fancy
import socket #Networking so the clipboard can be multicast
import changeDetails #The settings dialog area, only one thing in there right now but that can change
import threading #Multithreading
import signal #Handle Ctrl + C
import sys #Exiting

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
	sock.sendto(settings.login['id']+"##"+clipboard, (MCAST_ADDR,MCAST_PORT))

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
		except socket.error, e:
			pass
		else:
			data = data.split("##")

			#Is this the clipboard we are looking for?
			if data[0] == settings.login['id']:
				pyperclip.copy(data[1])
				currentClipboard = pyperclip.paste()
				#print(pyperclip.paste())

#Start the listener
listenerThread = threading.Thread(target=listen)
listenerThread.isDaemon()
listenerThread.start()

#Handle exit
def signal_handler(signal, frame):
	listenerThread._Thread__stop()
	sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

while 1:
	#Check for clipboard changes every 100ms
	time.sleep(0.1)

	if pyperclip.paste() != currentClipboard:
		currentClipboard = pyperclip.paste()
		sendClipboard(currentClipboard)