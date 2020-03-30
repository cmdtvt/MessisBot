''' This file contains some core functions for the bot '''
import glob, os
import asyncio
import json

from datetime import datetime

'''
Function to save bot's storage to data.json file.
'''
def saveData(data):
	#print("Saving started!")
	tempdata = data
	with open('data.json', 'w') as fpp:
		json.dump(tempdata, fpp, sort_keys=True, indent=4)
	fpp.close()
	#print("Saving done!")

'''
Function to load bot's storage to self.servers.
'''
async def loadData():
	try:
		print("Loading started!")
		data = {}
		with open('data.json', 'r') as fp:
			data = json.load(fp)
		fp.close()
		print("Loading done!")
		return data
	except:
		#### If bot fails to load data.json make self.servers an empty dictionary to avoid crashes also disable autosave that all data is not lost in autosave.
		print("[#### WARNING ####]: Bot was unable to load data from storage.")
		self.autosave = False
		return {}

'''
Function to load bad words from given folder.
'''
async def reloadWordDetect():
	### Scan directory for textfiles and load all words from the file to masterlist.
	masterlist = []
	tempList = []
	os.chdir("word-detection/")
	for file in glob.glob("*.txt"):
		with open(file) as f:
			tempList  = f.readlines()
		f.close()
		masterlist = masterlist + tempList
	os.chdir("../")

	### Remove newline marks from each string.
	for i in range(len(masterlist)):
		tempvar = masterlist[i].split("\n")
		masterlist[i] = tempvar[0]

	return masterlist

'''
Function to get current timestamp.
'''
async def getTime():
	#now = datetime.now()
	#year = now.strftime("%Y")
	#month = now.strftime("%m")
	#day = now.strftime("%d")
	#time = now.strftime("%H:%M:%S")
	#date_time = now.strftime("%m/%d/%Y, %H:%M:%S")

	now = datetime.now()
	timestamp = datetime.timestamp(now)
	return timestamp;


async def checkIfUserExsists(storage,serverid,userid):
	if str(userid) in storage[str(serverid)]["storage"]["users"]:
		return True
	else:
		#createNewUser(storage,serverid,userid)
		return False

async def checkIfServerExsists(storage,serverid):
	if str(serverid) in storage:
		return True
	else:
		return False


#### This doesnt work cause it is a big bully ####
async def toggleValue(storage,value):
	print("vallu: "+str(value))
	if value == True:
		value = False
		return False
	else:
		value = True
		return True



async def logNewEvent(storage,guild_id,userid,eventname,data):

	eventlog_ch = storage["eventlog"]
	eventlog_id = storage["eventlog_id"]

	eventlog_ch[str(eventlog_id)] = {
		"eventname":str(eventname),
		"data":data,
		"timestamp":str(await getTime()),
		"userid":str(userid)
	}
	eventlog_id = int(eventlog_id)+1

	storage["eventlog_id"] = int(storage["eventlog_id"])+1
	#print(storage["eventlog_id"])

'''
Function to create new user.
'''
async def createNewUser(storage,server,userid):
	user = server.get_member(userid)
	print("Creating user: "+str(user)+" / "+str(user.status))

	curuser = storage[str(user.guild.id)]["storage"]["users"]
	curuser[str(user.id)] = {
		"storage":{
			"discordname":user.name,
			"status":str(user.status), ### THIS MUST BE str(). If this is not done it adds stuff as list.
			"linked":{},
			"roles":{}
		},
		"settings":{},
		"stats":{
			"swearwords":0,
			"messages-total":0
		}
	}

	#### Adds all user's roles to the storage.
	for role in user.roles:
		curuser[str(user.id)]["storage"]["roles"][str(role.id)] = {
			"name":role.name
		}

'''
This function registers new channel for server.
storage is the full storage file. self.storage
server is the guild object
channel is channel id as int i think.

(Totaly didint waste 1h debugging this)
'''
async def createNewChannel(storage,server,channelid):

	channel = server.get_channel(channelid)
	storage[str(server.id)]["storage"]["channels"][str(channel.id)] = {
		"name":str(channel.name),
		"category":str(channel.category),
		"category_id":str(channel.category_id),
		"type":str(channel.type),
		"archived":str(False),
		"total-messages":0
	}
	




async def setupServer(storage,message,server):
	print(server)
	guild_id = str(message.guild.id)
	guild_id = str(message.guild.id)
	guild_owner = message.guild.owner_id
	guild_name = message.guild.name
	guild_members = message.guild.members
	guild_channels = message.guild.channels

	storage[guild_id] = {
		"serverinfo": {
			"owner":guild_owner,
			"servername":str(guild_name)
		},
		"storage":{
			"eventlog_id":0, #### Current id of event log
			"eventlog":{},
			"badges":{},
			"polls":{},
			"users":{},
			"channels":{},
			"gamerooms":{},
			"twitch_channels":{},
			"total-messages":0
		},
		"settings":{
			"setting_adminrole":0,
			"setting_logchannel":0,
			"setting_swearlogchannel":0,

			"setting_badges":{},
			"settings_censor":{}
		},
	}

	for i in guild_members:
		await createNewUser(storage,server,i.id)

	for i in guild_channels:
		await createNewChannel(storage,server,i.id)

	#return True