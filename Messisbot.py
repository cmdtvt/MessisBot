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
from imageEdit import *



class MyClient(discord.Client):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.prefix = "!m "
		self.servers = {}
		self.badwords = []
		self.botimage = "http://via.placeholder.com/350x350" #### Image for embeds
		self.autosave = True
		self.autosave_frequency = 30 #### How many seconds between autosaves.



	#### Task that runs save every 30sec ####
	async def doSave(self,):
		await self.wait_until_ready()
		while not self.is_closed():
			if self.autosave == True:
				self.saveData()
			await asyncio.sleep(self.autosave_frequency)

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

	#### Creates new empty user to self.servers when member is provided ####
	async def createNewUser(self,i):
		self.servers[guild_id]["storage"]["users"][i.id] = {
			"storage":{
				"discordname":str(i.name),
				"linked":{}
			},
			"settings":{},
			"stats":{
				"swearwords":"0",
				"messages-total":"0"
			}
		}


	async def on_ready(self):
		await self.loadData()
		await self.reloadWordDetect()

		self.saveLoop = self.loop.create_task(self.doSave())
		print(discord.__version__)
		print('Logged on as {0}!'.format(self.user))


	async def on_message(self, message):
		channel = message.channel
		guild_id = str(message.guild.id)
		lowercased_content = message.content.lower();
		logchannel = self.get_channel(self.servers[str(message.author.guild.id)]["settings"]["setting_logchannel"])
		swearlogchannel = self.get_channel(self.servers[str(message.author.guild.id)]["settings"]["setting_swearlogchannel"])

		#### Track user message count ####
		userstats = self.servers[guild_id]["storage"]["users"][str(message.author.id)]["stats"]
		userstats["messages-total"] = int(userstats["messages-total"])+1

		#### Does the greeting thing ###
		if not self.user == message.author:
			greetings = ["moi","hello","hi","sup"]
			if lowercased_content in greetings and not message.author.id == self.botid:
				await channel.send(str(random.choice(greetings)))

		#### Post image if someone mentions the bot ####
		if self.user in message.mentions:
			 await channel.send(file=discord.File('assets/summoned.png'))

		#### Detection for bad words ####
		hasBadWords = False
		foundWords = []
		scannedmessage = message.content.split()
		for i in range(len(self.badwords)):
			if self.badwords[i] in scannedmessage:
				foundWords.append(self.badwords[i])
				hasBadWords = True

		if hasBadWords == True:
			await swearlogchannel.send("> <@&"+str(message.author.id)+"> triggered bad words: "+str(foundWords))
			hasBadWords = False


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
			guild_members = message.guild.members


			#### developer commands ####
			if message.author.id == 125253485322174464:
				if command == "test":
					print(self.servers)
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


						"serverinfo": {
							"owner":guild_owner,
							"servername":str(guild_name)
						},
						"storage":{
							"badges":{},
							"polls":{},
							"users":{}
						},
						"settings":{
							"setting_adminrole":"0",
							"setting_logchannel":"0",
							"setting_swearlogchannel":"0",

							"setting_badges":{},
							"settings_censor":{}
						},

					}



					print(guild_members)
					for i in guild_members:
						await self.createNewUser(i)

					await channel.send("Server setup done! Members: "+str(len(guild_members)))


			#### Commands for admins
			#### Check if person has adminrole on server ####
			if self.servers[guild_id]["settings"]["setting_adminrole"] in [x.id for x in message.author.roles]:
				if command == "setlogchannel":
					self.servers[guild_id]["settings"]["setting_logchannel"] = message.channel.id
					await channel.send("Log channel set!")

				if command == "setswearchannel":
					self.servers[guild_id]["settings"]["setting_swearlogchannel"] = message.channel.id
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
							break #### Must break the loop because we delete stuff from the list we are looping. If not done crashes.

				if command.startswith("createpoll"):
					logchannel = self.get_channel(self.servers[str(message.author.guild.id)]["settings"]["setting_logchannel"])

					temp = command.split(",")
					name = temp[1]
					text = temp[2]
					answers = temp[3]
					answers = answers.strip("(")
					answers = answers.strip(")")
					answers = answers.split(",")

					embed=discord.Embed(title="Kysely: **"+str(name)+"**",description=text, color=0x92e3f1)
					embed.set_author(name="MessisBot",icon_url=self.botimage)

					embed.add_field(name="##################################################", value="**Vaihtoehdot**", inline=False)
					for i in range(20):
						embed.add_field(name="#"+str(i)+" Vaihtoehto", value="Keksit",inline=True)

					#embed.set_thumbnail(url=member.avatar_url)

					embed.add_field(name="##################################################", value="Miten vastaan? Kirjoita !m vote [NUMERO]",inline=False)
					embed.set_footer(text=str(await self.getTime()))

					print(temp)
					print(answers)

					await logchannel.send(embed=embed)

				if command.startswith("vote"):
					temp = command.split(" ")
					
					await channel.send(message.author.name+" Äänesti vaihtoethoa: "+str(temp[1]))


					

			if command.startswith("setadminrole"):
				print(self.servers)
				self.servers[guild_id]["settings"]["setting_adminrole"] = mentioned_roles[0].id
				await channel.send("Updated admin role to: <@&"+str(self.servers[guild_id]["settings"]["setting_adminrole"])+">")

			if command.startswith("profile"):

				#### If user has not mentioned anyone show users own profile.
				if len(mentioned_users) > 0:
					targetuser = mentioned_users[0]
				else:
					targetuser = message.author

				msgtotal = userstats["messages-total"]
				image = targetuser.avatar_url
				name = targetuser.name
				bio = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."


				
				image_editor = ImageEditor(image,name,bio,msgtotal)
				image_editor.createProfile()
				del image_editor

				await channel.send(file=discord.File('assets/image-edit/result.png'))



			elif command.startswith("help"):
				await channel.send("https://github.com/cmdtvt/MessisBot#commands")

	async def on_member_join(self,member):

		await self.createNewUser(self,member)

		joinmessage = "Hei Tervetuloa Messiksen discord serverille! Minä olen "+str(self.user.name)+" ja minä tarkkailen juttuja ympäri messiksen discord serveriä! \n Oletko jo täyttänyt pienen kyselyn? \n https://www.mess.is/liity/"
		logchannel = self.get_channel(self.servers[str(member.guild.id)]["settings"]["setting_logchannel"])

		embed=discord.Embed(description="<@"+str(member.id)+"> Liittyi palvelimelle!", color=0x33c41a)
		embed.set_author(name="MessisBot",icon_url=self.botimage)
		embed.set_thumbnail(url=member.avatar_url)
		embed.set_footer(text=str(await self.getTime()))
		await logchannel.send(embed=embed)
		await member.send(joinmessage)

	async def on_raw_reaction_add(self,payload):

		emoteid = str(payload.emoji.id)
		user = self.get_guild(payload.guild_id).get_member(payload.user_id)

		if emoteid in self.servers[str(payload.guild_id)]["settings"]["setting_badges"]:
			if self.servers[str(payload.guild_id)]["settings"]["setting_badges"][emoteid]["role"] in [str(x.id) for x in user.roles]:

				badgeinfo = self.servers[str(payload.guild_id)]["settings"]["setting_badges"][emoteid]
				badgetype = badgeinfo["badgetype"]




				#### Message Generation and stuff
				channel = self.get_channel(payload.channel_id)
				logchannel = self.get_channel(self.servers[str(payload.guild_id)]["settings"]["setting_logchannel"])
				messageobj = await channel.fetch_message(payload.message_id)
				sender = self.get_guild(payload.guild_id).get_member(payload.user_id)
				link = "https://discordapp.com/channels/"+str(payload.guild_id)+"/"+str(payload.channel_id)+"/"+str(payload.message_id) #### Generate link for the message
				logmessage = link+" \n > <@"+str(sender.id)+"> antoi <@"+str(messageobj.author.id)+"> **"+str(badgetype)+"** badgen! \n ```"+str(messageobj.content)+"```"



				if not str(payload.message_id) in self.servers[str(payload.guild_id)]["storage"]["badges"].keys(): #### Check that the badge has not been added allready


					await logchannel.send(logmessage)
					#### Add message badge info into the servers/badges
					self.servers[str(payload.guild_id)]["storage"]["badges"][str(payload.message_id)] = {
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