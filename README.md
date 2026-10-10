# What is needed to run the code
- A discord bot with Message Content privileged gateway intent
- .env file at root of project, with BOT\_TOKEN = the bot's bot token
- A config.json file at root of project, in this format:
```json
{
    "ADMIN_ROLE_NAME": "admin", (name of admin role)
    "BOT_LOGS_CHANNEL_ID": [channel id for bot logging],
    "MODMAIL_CATEGORY_ID": [category (channel) id for modmail category],
    "MODMAIL_LOGS_CHANNEL_ID": [channel id for modmail archival],
    "MODMAIL_NEXT_ID": 0, (number that uniquely identifies each modmail ticket)
    "STAFF_MEMBER_ROLE_ID": [id of staff member role],
    "STAFF_MEMBER_ROLE_NAME": "staff-member" (name of staff member role)
}
```
