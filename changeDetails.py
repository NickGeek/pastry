import easygui as eg
import sys

def changeDetails():
	id = eg.enterbox("All devices with the same ID share the same clipboard.", "What ID do you want to use?")
	if not id:
		sys.exit()
	login = "dict(id = '"+id+"')"
	settingsFile = open('settings.py', 'w+')
	settingsFile.write("login = "+str(login))
	settingsFile.close()


	#Notify the user
	eg.msgbox("Pastry is now running with the ID: "+id, "Pastry")

if __name__ == '__main__':
	changeDetails()