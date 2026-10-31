import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from config import config

# root logger
logging.basicConfig(level=logging.INFO)

# handles logging for this code
logger = logging.getLogger(__name__)

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

GUILD = discord.Object(id=config["guild_id"])
print(GUILD)
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
            ignorable = {"__pycache__", "__init__.py"}
            for cog in config["ignored_cogs"]:
                ignorable.add(cog)

            if filename in ignorable:
                pass

            # if it's not a .py cog, why is it here? ignore it and warn
            elif not filename.endswith(".py"):
                logger.warning(f"Skipping file of unexpected type: {filename}")
            else:
                # load the cog
                await self.load_extension(f"cogs.{os.path.splitext(filename)[0]}")

            # format help text for all commands
            for command in bot.walk_commands():
                if command.help:
                    command.help = command.help.format(bot_name=bot.user)

        self.tree.copy_global_to(guild=GUILD)
        await self.tree.sync(guild=GUILD)

    async def on_ready(self):
        logger.info(f"We have logged in as {self.user} (ID: {self.user.id})")
        logger.info("--------")

    async def on_command_error(self, context, exception, /):
        await super().on_command_error(context, exception)

        # tell the user nothing if the reason they can't run is no role
        if isinstance(exception, commands.CheckAnyFailure):
            return

        await context.channel.send(
            f"Error in command {context.command.name}:\n"
            f"Is your input correct? "
            f"Check $help {context.command.name}."
        )


class MyHelpCommand(commands.DefaultHelpCommand):
    def get_ending_note(self):
        return "Type $help command for more info on a command.\nSbeve out."

    def get_command_signature(self, command):
        return super().get_command_signature(command)


help_command = MyHelpCommand()

bot = CustomBot(
    command_prefix="$",
    description="sbeve sbeves.",
    intents=intents,
    help_command=help_command,
)

bot.run(BOT_TOKEN)
