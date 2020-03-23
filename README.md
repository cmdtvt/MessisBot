# MessisBot
This is a discordbot for managing discord server. This bot is designed to give server admins more info of what is happening on the server. Bot will have multiple systems to make interacting with server members easier.


# Bot Install / Setup
Download bots files and modify config.py. Add your botkey / token and add yourself to the adminlist. If you have developer mode enabled in your discord you can rightclick your user and copy your id. Paste this id into admins list.
Please make sure that data.json file is also writable. To run the bot run Messisbot.py with python3.

# Server setup.
Things that need to be setup before using the bot.
1. ```!m setup``` Register current server to the bot.
2. ```!m setadminrole [MENTION ROLE]``` Set role wich has access to admin commands.
3. ```!m setlogchannel``` Run on channel that you want to be used as log channel.
4. ```!m setswearchannel``` When ran on channel starts to log swearing people there.

# Commands

### Bot Owner
1. ```!m test```
2. ```!m save```
3. ```!m load ```
4. ```!m reload_word_detect```

### Server Owner
1. ```!m setup``` Register current server to the bot.
2. ```!m setadminrole [MENTION ROLE]``` Set role wich has access to admin commands.

### Admins / Server owner
1. ```!m createbadge [EMOTE] [NAME] [ROLE]``` Create new badge wich can be used be spefic role.
2. ```!m listbadges``` Lists all badges.
3. ```!m delbadge [NAME]``` Deletes badge from server.
4. ```!m setlogchannel``` Run on channel that you want to be used as log channel.
5. ```!m setswearchannel``` When ran on channel starts to log swearing people there.

6. ```!m createpoll ([POLL NAME]) ([POLL TEXT]) ([POLL ANSWERS])``` Creates a new poll. Answers should be devided by ```,``` for example ```(answer1,answer2,answer3)```
7. ```!m polls``` Lists active polls. If you wanna see all the polls you can use ```!m polls all```.
8. ```!m closepoll [POLL ID]``` Closes poll so users cant vote on it.
10. ```!m openpoll [POLL ID]``` Opens poll so users can vote on it again.
11. ```!m pollinfo [POLL ID]``` Get graph of the poll.

### Everyone
1. ```!m vote [POLL ID] [VOTED ANSWERS NUMBER]``` Vote on poll.
2. ```!m profile``` Generates an image wich has all user info.
3. ```!m help``` Gives help to commands.


# Features
This is a list of bot's current and upcoming features.
- [x] Badge system. If user with allowed role gives spesific emote this message is copied and logged for admins to view.
- [x] Custom badges.
- [x] If user writes some type of greeting the bot responds
- [x] If user mentions the bot it responds with a image
- [x] System to log events that happen on server.
- [x] Generate custom image about users profile information.
- [x] Track amount of messages and swearwords.
- [ ] System to log bad words to another channel with the info of the user.
- [ ] Poll system.

# Events
This bot logs multiple different events.
This is handled by ```logNewEvent()``` function. With this function its possible to add new events to storage. This function takes arguments ```guild_id,userid,eventname,data``` data is usually a dictionary that contains more information about the event.
Here is a list of actions and events what bot logs.
- Creation and deletion of badges.
- If a new poll is created.
- Deleted messages. (Message is stored).
- Edited messages. ( new message is logged).
- User comes or leaves the server.
- Role is given or taken away from user.
