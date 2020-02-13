from datetime import datetime
import matplotlib.pyplot as plt
import glob, os
import platform
import re

print(platform.python_version())

import discord
import asyncio
import json
import random

from config import *
from storage import *
from utilities2 import *
from imageEdit import *



class MyClient(discord.Client):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.prefix = "!m "
		self.servers = {}
		self.onlineMessages = {}
		self.adminuser = 125253485322174464
		self.badwords = []
		self.botimage = "http://via.placeholder.com/350x350" #### Image for embeds
		self.autosave = True
		self.autosave_frequency = 30 #### How many seconds between autosaves.


	async def on_ready(self):
		await self.servers = loadData()
		await self.badwords = reloadWordDetect()

		self.saveLoop = self.loop.create_task(self.doSave())
		print(discord.__version__)
		print('Logged on as {0}!'.format(self.user))


	async def on_message(self, message):
		channel = message.channel
		guild_id = str(message.guild.id)
		lowercased_content = message.content.lower();

		if checkIfServerExsists(self.servers,message.guild.id):
			if checkIfUserExsists(self.servers,message.guild.id,message.author.id):


				logchannel = self.get_channel(self.servers[str(message.author.guild.id)]["settings"]["setting_logchannel"])
				swearlogchannel = self.get_channel(self.servers[str(message.author.guild.id)]["settings"]["setting_swearlogchannel"])

				server_storage = self.servers[guild_id]["storage"]
				server_settings = self.servers[guild_id]["settings"]
				userdata = self.servers[guild_id]["storage"]["users"][str(message.author.id)]
				userstats = userdata['stats']

				if message.content.startswith(self.prefix):
					command = message.contnet.strip(self.prefix+" ")

					author = message.author
					mentioned_users = message.mentions
					mentioned_roles = message.role_mentions
					channel_id = message.channel.id
					guild_id = str(message.guild.id)
					guild_owner = message.guild.owner_id
					guild_name = message.guild.name
					guild_members = message.guild.members
					guild_channels = message.guild.channels

					#### Test if user is bot admin ####
					if author.id == self.adminuser:
						if command == "test":
							await channel.send("It seems that the test was successfull.")

						if command == "save":
							await saveData()
							await channel.send("Saving done!")

						if command == "load":
							await loadData()
							await channel.send("Loading done!")

						if command == "reload_word_detect":
							await reloadWordDetect()
							await channel.send("Reloading done!")

					if command == "setup":
						await setupServer(self.servers,guild_id,guild_owner,guild_name,guild_members,guild_channels)
						await channel.send("Server setup done! Members: "+str(len(guild_members)))

					#### Check if person has adminrole on server ####
					if server_settings["setting_adminrole"] in [x.id for x in message.author.roles]:
						if command == "setlogchannel":
							server_settings["setting_logchannel"] = message.channel.id
							await channel.send("Log channel set!")

						if command == "setswearchannel":
							server_settings["setting_swearlogchannel"] = message.channel.id
							await channel.send("Channel set!")

						if command.startswith("createbadge"):
							temp = command.split(" ")
							r = re.match(".*<:(.*):(.*)>",message.content) #### get emote name
							r2 = re.match(".*:(\w*)>.*",message.content) #### get emote id

							if r and r2: #### If emotename and emote id was found 
								server_settings["setting_badges"][str(r2.group(1))] = {
									"emotename":r.group(1),
									"badgetype":temp[2],
									"role":mentioned_roles[0].id,
									"timestamp": await getTime()
								}
								await channel.send("**"+str(temp[2])+"** badge luotu emotelle: "+str(temp[1])+" roolille: <@&"+str(mentioned_roles[0].id)+">")

								data = {
									"badgetype":temp[2],
									"badgemote":r.group(1),
									"role":mentioned_roles[0].id
								}
								#await self.logNewEvent(message.author.guild.id,message.author.id,"createbadge",data)
							else:
								await channel.send("Virhe badgen luomisessa. Onko syntaxi oikein? !m help")

						if command.startswith("listbadges"):

							badges = "Rekisteröidyt Badget \n"
							tempBadge = ""
							badge = server_settings["setting_badges"]
							for x in badge:
								tempBadge = str(badge[str(x)]["badgetype"])+"  :  "+str(badge[str(x)]["emotename"])+"  :  <@&"+str(badge[str(x)]["role"])+">\n"
								badges = badges + tempBadge
							await channel.send(badges)

						if command.startswith("delbadge"):
							badge = server_settings["setting_badges"]
							temp = command.split(" ")
							for i in badge:
								if badge[i]["badgetype"] == temp[1]:
									await channel.send(str(badge[i]["badgetype"])+" badge poistettiin!")
									data = {
										"badgetype":badge[i]["badgetype"],
										"badgemote":badge[i]["emotename"],
										"role":badge[i]["role"]
									}
									#await self.logNewEvent(message.author.guild.id,message.author.id,"deletebadge",data)
									del badge[i]
									break

						if command.startswith("createpoll"):
							
							r = re.match(".*(\(.*?\)).*(\(.*?\)).*(\(.*?\))",message.content)
							if r:
								pollstorage = server_storage["polls"]
								name = r.group(1).strip("(").strip(")")
								text = r.group(2).strip("(").strip(")")
								answers = r.group(3).strip("(").strip(")")
								answers = answers.split(",")
								pollid = random.randrange(1000,10000)

								while(True):
									if str(pollid) in pollstorage:
										pollid = random.randrange(1000,10000) #### Create random id for poll
									else:
										break;

								storage_answer_list = {}
								for i in range(len(answers)):
									storage_answer_list[str(i)] = {
										"name":str(answers[i]),
										"votes-amount":1
									} 

								print(storage_answer_list)


								pollstorage[str(pollid)] = {
									"answers":storage_answer_list,
									"createdby":message.author.id,
									"channel":message.channel.id,
									"pollname":name,
									"polltext":text,
									"pollactive":str(True),
									"votes":{}
								}

								embed=discord.Embed(title="Kysely: **"+str(name)+"**",description=text, color=0x92e3f1)
								embed.set_author(name="MessisBot",icon_url=self.botimage)
								embed.set_thumbnail(url="https://via.placeholder.com/350x350?text="+str(pollid))
								embed.add_field(name="####################################", value="**Vaihtoehdot**", inline=False)
								for i in range(len(answers)):
									embed.add_field(name="#"+str(i)+" Vaihtoehto", value=str(answers[i]),inline=True)

								embed.add_field(name="###################################", value="Miten vastaan? Kirjoita !m vote "+str(pollid)+" [NUMERO]",inline=False)
								embed.set_footer(text=str(await self.getTime()))

								print(answers)
								data = {
									"pollid":pollid,
								}
								#await self.logNewEvent(message.guild.id,message.author.id,"createpoll",data)
								await message.channel.send(embed=embed)
							else:
								await message.channel.send("Virhe pollin luomisessa? Onko syntaxi oikein? !m help")


							if command.startswith("closepoll"):
								pollstorage = server_storage["polls"]
								temp = command.split(" ")
								pollid = str(temp[1])
								if pollid in pollstorage:
									pollstorage[str(pollid)]["pollactive"] = str(False)

								data = {
									"pollid":pollid
								}
								#await self.logNewEvent(message.guild.id,message.author.id,"closepoll",data)
								await channel.send(author.name+" Sulki äänestyksen: "+str(pollid))

							if command.startswith("openpoll"):
								pollstorage = server_storage["polls"]
								temp = command.split(" ")
								pollid = str(temp[1])
								if pollid in pollstorage:
									pollstorage[str(pollid)]["pollactive"] = str(True)

								data = {
									"pollid":pollid
								}
								#await self.logNewEvent(message.guild.id,message.author.id,"openpoll",data)
								await channel.send(author.name+" Avasi äänestyksen: "+str(pollid))

							if command.startswith("polls"):
								temp = []
								temp = command.split(" ")
								openpolls = "Aktiiviset äänestykset\n"
								pollstorage = server_storage["polls"]

								if not len(temp) > 1: #### If nothing is added to the command dont run this one.
									for i in pollstorage:
										if pollstorage[i]["pollactive"] == "True":
											openpolls = openpolls+str(i)+" : "+str(pollstorage[i]["pollname"])+"\n"
								else:
									if temp[1] == "all":
										for i in pollstorage:
											if pollstorage[i]["pollactive"] == "True":
												openpolls = openpolls+str(i)+" : "+str(pollstorage[i]["pollname"])+"\n"

										openpolls = openpolls+"\nSuljetut äänestykset\n"
										for i in pollstorage:
											openpolls = openpolls+str(i)+" : "+str(pollstorage[i]["pollname"])+"\n"

								await channel.send(str(openpolls))



		else:
			if message.content.startswith(self.prefix):
				await channel.send("This server has not been registerd! Commands wont be usable before setup.")


		'''
		Things to run on every message
		'''
		userstats["messages-total"] = int(userstats["messages-total"])+1

		server_storage["total-messages"] = int(server_storage["total-messages"])+1



		#### Does the greeting thing ###
		if not self.user == message.author:
			greetings = ["moi","hello","hi","sup"]
			if lowercased_content in greetings and not message.author.id == self.user.id:
				await channel.send(str(random.choice(greetings)))

		#### Post image if someone mentions the bot ####
		if self.user in message.mentions:
			 await channel.send(file=discord.File('assets/summoned.png'))