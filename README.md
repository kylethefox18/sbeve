# Sbeve: A Discord bot that does stuff mostly
You can try Sbeve out [here](https://discord.gg/RVNBBA3kfY)  
These are some commands Sbeve offers:
test
```
sbeve sbeves.

Counter:
  start_counter       Starts a counter for pressing.
ForbOrBorb:
  send_forbborb_msg   Sends the forb vs borb message.
General:
  add                 Adds two integers together.
  get_sticker_from_id Gets a sticker given its id.
  is_admin            Checks whether a member is an admin.
  is_staff_member     Checks whether a member is a staff member.
  joined              Says when a member joined.
  roll                Rolls dice from input in NdN format.
Greetings:
  hello               Says hello
Modmail:
  close_modmail       Closes the modmail channel it is called in.
  send_modmail_embed  Sends the "Open Modmail" embed.
​No Category:
  help                Shows this message

Type $help command for more info on a command.
Sbeve out.
```
## What is needed to run the code
- A discord bot with Message Content privileged gateway intent
- .env file at root of project, with BOT\_TOKEN = the bot's bot token
- Adjust the example config files to suit your needs
-   NOTE: initial value forbborb_msg_id is arbritrary: send_forbborb_msg sets this
- Remake all directories appended with .example as themselves, without the .example
