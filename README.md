# Sbeve: A Discord bot that does stuff mostly
You can try Sbeve out [here](https://discord.gg/RVNBBA3kfY)
## What is needed to run the code
- A discord bot with Message Content privileged gateway intent
- .env file at root of project, with BOT\_TOKEN = the bot's bot token
- A config.json file at root of project, in this format:
```json
{
    "ADMIN_ROLE_NAME": "(name of admin role)",
    "MODMAIL_CATEGORY_ID": (category id for modmail),
    "MODMAIL_LOGS_CHANNEL_ID": (channel id for modmail logging),
    "MODMAIL_NEXT_ID": 0,
    "STAFF_MEMBER_ROLE_ID": (id of staff member role),
    "STAFF_MEMBER_ROLE_NAME": "(name of staff role)"
}
```
- Adjust the forb\_or\_borb\_info.json file in cogs:
```json
{
    "borb_role_id": (borb role id),
    "forb_role_id": (forb role id),
    "forbborb_msg_id": (forbborb reaction message id: autoset by $send_forbborb_msg)
}
```
