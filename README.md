# MessisBot
This is a discordbot for managing discord server. This bot is designed to give server admins more info of what is happening on the server. Bot will have multiple systems to make interacting with server members easier.


# Bot Install / Setup
Download bots files and modify config.py. Add your botkey / token and add yourself to the adminlist. If you have developer mode enabled in your discord you can rightclick your user and copy your id. Paste this id into admins list.
Please make sure that data.json file is also writable. To run the bot run Messisbot.py with python3.

# Server setup.
Things that need to be setup before using the bot.
1. ```!m setup``` Register current server to the bot
2. ```!m setadminrole [MENTION ROLE]``` Set role wich has access to admin commands
3. ```!m setuserrole [MENTION ROLE]``` Set role wich can give badges etc...
4. ```!m setlogchannel``` Run on channel that you want to be used as log channel
5. To use badges make sure that you have a emote on the server with name :juttu:

# Features
This is a list of bot's current and upcoming features.
- [x] Badge system. If user with allowed role gives spesific emote this message is copied and logged for admins to view.
- [x] If user writes some type of greeting the bot responds
- [x] If user mentions the bot it responds with a image
- [ ] System to log bad words to another channel with the info of the user.
- [ ] Poll system.
