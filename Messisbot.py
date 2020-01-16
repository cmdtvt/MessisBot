from datetime import datetime
import glob, os
import platform
import re
print(platform.python_version())

import discord
import asyncio
import json
import random
'''
Bot's other files...
'''
from config import *
from storage import *
from utilities import *



class MyClient(discord.Client):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.servers = {}
		self.badwords = []
		self.botimage = "http://via.placeholder.com/350x350" #### Image for embeds
		self.autosave = True



	#### Task that runs save every 30sec ####
	async def doSave(self,):
		await self.wait_until_ready()
		while not self.is_closed():
			if self.autosave == True:
				self.saveData()
			await asyncio.sleep(30)

	#### Saves data from self.servers to data.json ####
	def saveData(self,):
		print("Saving started!")
		tempdata = self.servers
		with open('data.json', 'w') as fpp:
			json.dump(tempdata, fpp, sort_keys=True, indent=4)

		fpp.close()
		print("Saving done!")

	#### Loads data from data.json and saves it to self.servers ####
	async def loadData(self):
		try:
			print("Loading started!")
			data = {}
			with open('data.json', 'r') as fp:
				data = json.load(fp)
			self.servers = data
			fp.close()
			print("Loading done!")

		except:
			#### If bot fails to load data.json make self.servers an empty dictionary to avoid crashes also disable autosave that all data is not lost in autosave.
			print("[#### WARNING ####]: Bot was unable to load data from storage.")
			self.autosave = False
			self.servers = {}

	#### Load bad words to the bot ####
	async def reloadWordDetect(self,):
		### Scan directory for textfiles and load all words from the file to masterlist
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

		self.badwords = masterlist

	#### Function for getting a timestamp ####
	async def getTime(self,):
		now = datetime.now()
		year = now.strftime("%Y")
		month = now.strftime("%m")
		day = now.strftime("%d")
		time = now.strftime("%H:%M:%S")
		date_time = now.strftime("%m/%d/%Y, %H:%M:%S")

		return date_time;

	async def on_ready(self):
		self.prefix = "!m "
		await self.loadData()
		await self.reloadWordDetect()

		self.saveLoop = self.loop.create_task(self.doSave())
		print(discord.__version__)
		print('Logged on as {0}!'.format(self.user))


	async def on_message(self, message):
		channel = message.channel
		lowercased_content = message.content.lower();


		#### Does the greeting thing ###
		if not self.user == message.author:
			greetings = ["moi","hello","hi","sup"]
			if lowercased_content in greetings and not message.author.id == self.botid:
				await channel.send(str(random.choice(greetings)))

		#### Post image if someone mentions the bot ####
		if self.user in message.mentions:
			 await channel.send(file=discord.File('assets/summoned.png'))

		#### Detection for bad words ####
		scannedmessage = message.content.split()
		for i in range(len(self.badwords)):
			if self.badwords[i] in scannedmessage:
				await channel.send("BAD BOI")

		print(scannedmessage)


		#### Checks if message has wanted prefix so its detected to be a command ####
		if message.content.startswith(self.prefix):
			command = message.content.strip(self.prefix+" ")
			author = message.author
			mentioned_users = message.mentions
			mentioned_roles = message.role_mentions
			channel_id = message.channel.id
			guild_id = str(message.guild.id)
			guild_owner = message.guild.owner_id
			guild_name = message.guild.name
			print(guild_name)


			#### developer commands ####
			if message.author.id == 125253485322174464:
				if command == "test":
					await channel.send("It seems that the test was successfull.")

				if command == "save":
					self.saveData()
					await channel.send("Saving done!")

				if command == "load":
					await self.loadData()
					await channel.send("Loading done!")

				if command == "reload_word_detect":
					await self.reloadWordDetect()
					await channel.send("Reloading done!")


				if command == "setup":
					self.servers[guild_id] = {
					"owner":guild_owner,
					"servername":str(guild_name),
					"adminrole":"0",
					"userrole":"0",
					"badges":{},
					"polls":{},
					"users":{},
					"settings":{
						"setting_badges":{},
						"settings_censor":{}
					},
					"logchannel":"0",
					"cspychannel":"0" #### Channel info where bad words are logged.
					}

					#for x in server.Server.members:


					await channel.send("Server setup done: "+str(self.servers[str(guild_id)]))


			#### Commands for admins
			#### Check if person has adminrole on server ####
			if self.servers[guild_id]["adminrole"] in [x.id for x in message.author.roles]:
				if command == "setlogchannel":
					self.servers[guild_id]["logchannel"] = message.channel.id
					await channel.send("Log channel set!")

				if command == "setswearchannel":
					self.servers[guild_id]["cspychannel"] = message.channel.id
					await channel.send("Channel set!")


				if command.startswith("createbadge"):

					temp = command.split(" ")

					r = re.match(".*<:(.*):(.*)>",message.content) #### get emote name
					r2 = re.match(".*:(\w*)>.*",message.content) #### get emote id

					if r and r2: #### If emotename and emote id was found 
						self.servers[str(guild_id)]["settings"]["setting_badges"][str(r2.group(1))] = {
							"emotename":str(r.group(1)),
							"badgetype":str(temp[2]),
							"role":str(mentioned_roles[0].id),
							"timestamp": str(await self.getTime())
						}
						await channel.send("**"+str(temp[2])+"** badge luotu emotelle: :"+str(temp[1])+": roolille: <@&"+str(mentioned_roles[0].id)+">")
					else:
						await channel.send("Virhe badgen luomisessa. Onko syntaxi oikein? !m help")

				if command.startswith("listbadges"):

					badges = "Rekisteröidyt Badget \n"
					tempBadge = ""
					badge = self.servers[str(guild_id)]["settings"]["setting_badges"]
					for x in badge:
						print("x: "+str(x))
						tempBadge = str(badge[str(x)]["badgetype"])+"  :  "+str(badge[str(x)]["emotename"])+"  :  <@&"+str(badge[str(x)]["role"])+">\n"
						badges = badges + tempBadge
					await channel.send(badges)

				if command.startswith("delbadge"):
					badge = self.servers[str(guild_id)]["settings"]["setting_badges"]
					temp = command.split(" ")
					for i in badge:
						if badge[i]["badgetype"] == temp[1]:
							await channel.send(str(badge[i]["badgetype"])+" badge poistettiin!")
							del badge[i]
							break


					

			if command.startswith("setadminrole"):
				print(self.servers)
				self.servers[guild_id]["adminrole"] = mentioned_roles[0].id
				await channel.send("Updated admin role to: <@&"+str(self.servers[guild_id]["adminrole"])+">")

			elif command.startswith("setuserrole"):
				print(self.servers)	
				self.servers[guild_id]["userrole"] = mentioned_roles[0].id
				await channel.send("Updated user role to: <@&"+str(self.servers[guild_id]["userrole"])+">")

			elif command.startswith("help"):
				await channel.send("https://github.com/cmdtvt/MessisBot")

	async def on_member_join(self,member):
		joinmessage = "Hei Tervetuloa Messiksen discord serverille! Minä olen "+str(self.user.name)+" ja minä tarkkailen juttuja ympäri messiksen discord serveriä! \n Oletko jo täyttänyt pienen kyselyn? \n https://www.mess.is/liity/"
		logchannel = self.get_channel(self.servers[str(member.guild.id)]["logchannel"])

		embed=discord.Embed(description="<@"+str(member.id)+"> Liittyi palvelimelle!", color=0x33c41a)
		embed.set_author(name="MessisBot",icon_url=self.botimage)
		embed.set_thumbnail(url=member.avatar_url)
		embed.set_footer(text=str(await self.getTime()))
		await logchannel.send(embed=embed)
		await member.send(joinmessage)

	async def on_raw_reaction_add(self,payload):

		##### This is the code for the badge system. This code checks if user has permission to use certain badge
		for i in self.get_guild(payload.guild_id).get_member(payload.user_id).roles: #### Run for each role in user
			for x in self.servers[str(payload.guild_id)]["settings"]["setting_badges"]: #### Run for each added badge

				badgeinfo = self.servers[str(payload.guild_id)]["settings"]["setting_badges"][str(x)]
				badgetype = badgeinfo["badgetype"]

				#### Message Generation and stuff
				channel = self.get_channel(payload.channel_id)
				logchannel = self.get_channel(self.servers[str(payload.guild_id)]["logchannel"])
				messageobj = await channel.fetch_message(payload.message_id)
				sender = self.get_guild(payload.guild_id).get_member(payload.user_id)
				link = "https://discordapp.com/channels/"+str(payload.guild_id)+"/"+str(payload.channel_id)+"/"+str(payload.message_id) #### Generate link for the message
				logmessage = link+" \n > <@"+str(sender.id)+"> antoi <@"+str(messageobj.author.id)+"> **"+str(badgetype)+"** badgen! \n ```"+str(messageobj.content)+"```"






				if badgeinfo["role"] == str(i.id): #### Check if users role matches the role in badge
					if str(badgeinfo["emotename"]) == str(payload.emoji.name): #### Check that its the correct badge.

						if not str(payload.message_id) in self.servers[str(payload.guild_id)]["badges"].keys(): #### Check that the badge has not been added allready
							await logchannel.send(logmessage)

							#### Add message badge info into the servers/badges
							self.servers[str(payload.guild_id)]["badges"][str(payload.message_id)] = {
								"message":str(messageobj.content),
								"messagelink":str(link),
								"messageownername":str(messageobj.author.name),
								"messageownerid":str(messageobj.author.id),
								"usergavename":str(self.get_guild(payload.guild_id).get_member(payload.user_id).name),
								"usergaveid":str(payload.user_id),
								"channelid":str(payload.channel_id),
								"channelname":str(channel.name),
								"type":str(badgetype),
								"timestamp": str(await self.getTime())
							}





client = MyClient()
client.run(botkey)