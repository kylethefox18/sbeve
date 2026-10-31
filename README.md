# Sbeve: A Discord bot that does stuff mostly
You can try Sbeve out [here](https://discord.gg/RVNBBA3kfY)  
These are some commands Sbeve offers:
```
sbeve sbeves.

Counter:
  start_counter       Starts a counter for pressing.
ForbOrBorb:
  send_forbborb_msg   Sends the forb vs borb message.
General:
  add                 Adds two integers together.
  change_nickname     
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

Send the command "help command" for more info on a command.
Sbeve out.
```
## Misc notes
"Admin" is distinct from "with administrator priviliges": an admin is a person with 
more power than a plain staff member in a discord server, but not necessarily with 
administrative privileges. Administrative privileges means a role or something a 
person belongs to has the "Administrator" box checked under Advanced Permissions\: 
the most powerful permission there is.
## What is needed to run the code
- The code itself: clone this repository  
- The dependencies: at the root of the project run pip -r install requirements.txt  
(I'd recommend doing the above in a virtual environment to keep system python clean)
- A discord bot with Message Content privileged gateway intent  
- .env file at root of project, with BOT\_TOKEN = the bot's bot token  
- Adjust the example config files to suit your needs
(copy `filename.example.toml` to `filename.toml` and adjust that)  
- Remake all directories appended with .example as themselves, without the .example  
- Add your bot to the desired server  
If everything is now set up correctly, you should be able to run the code with just
`$ python3 main.py` \:)  
## Hiding slash commands for those without privileges  
In order to hide slash commands from those without the permission to perform them, you
must do the following\:  
- Go to Server Settings > Apps > Integrations > Bots and Apps > Manage (for your bot)  
- Set who can see what command (via overrides)  
Commands currently restricted by the bot are:  
`get_sticker_from_id` to staff members  (and people with administrator privileges)  
`start_counter` to bot owner            (and people with administrator privileges)  
`send_forbborb_msg` to bot owner        (and people with administrator privileges)  
`send_modmail_embed` to admins          (and people with administrator privileges)  
`change_nickname` to admins             (and people with administrator privileges)  
You can set overrides as so, or differently if you wish.  
