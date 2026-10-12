import os
import warnings

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()

intents.message_content = True


class CustomBot(commands.Bot):
    # Suppress error on the User attribute being None
    user: discord.ClientUser

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def setup_hook(self) -> None:
        # load extensions/cogs
        cogs_dir = os.fsencode("cogs")
        for file in os.listdir(cogs_dir):
            filename = os.fsdecode(file)

            # list of known ignorable files
            ignorable = {"__pycache__", "__init__.py", "forb_or_borb_info.json"}
            if filename in ignorable:
                pass

            # if it's not a .py cog, why is it here? ignore it and warn
            elif not filename.endswith(".py"):
                warnings.warn(f"Skipping file of unexpected type: {filename}")
            else:
                # load the cog
                await self.load_extension(f"cogs.{os.path.splitext(filename)[0]}")

    async def on_ready(self):
        print(f"We have logged in as {self.user} (ID: {self.user.id})")
        print("--------")

    async def on_command_error(self, context, exception, /):
        await super().on_command_error(context, exception)
        await context.channel.send(
            f"Error in command {context.command.name}:\n"
            f"Is your input correct? "
            f"Check $help {context.command.name}."
        )


class MyHelpCommand(commands.DefaultHelpCommand):
    def get_ending_note(self):
        return "Type $help command for more info on a command.\nSbeve out."

    def get_command_signature(self, command):
        if command.help:
            command.help = command.help.format(bot_name=bot.user)

        return super().get_command_signature(command)


help_command = MyHelpCommand()

bot = CustomBot(
    command_prefix="$",
    description="sbeve sbeves.",
    intents=intents,
    help_command=help_command,
)

bot.run(BOT_TOKEN)
