import json
from pathlib import Path

import anyio
import discord
from discord.ext import commands

forbborb_info_path = Path(__file__).resolve().parent / "forb_or_borb_info.json"
with open(forbborb_info_path, "r") as f:
    info = json.load(f)


class ForbOrBorb(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emoji_to_role = {
            discord.PartialEmoji(name="🦊"): info["forb_role_id"],
            discord.PartialEmoji(name="🐦"): info["borb_role_id"],
        }

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """Gives forb role or borb role based on a reaction emoji."""
        # Make sure the message being reacted to is a role-assignment message
        if payload.message_id != info["forbborb_msg_id"]:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            # check we're in a guild and it's cached
            print("ForbOrBorb: guild is none, aborting")
            return

        try:
            role_id = self.emoji_to_role[payload.emoji]
        except KeyError:
            # if we don't care about this emoji, exit
            return

        role = guild.get_role(role_id)
        if role is None:
            print("ForbOrBorb: A role was not found, aborting")
            return

        # make sure we have the member who reacted
        assert payload.member is not None

        # don't add the role if it is the bot's reaction
        if payload.member == self.bot.user:
            return

        # at long last, add the role
        await payload.member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        # Make sure the message being reacted to is a role-assignment message
        if payload.message_id != info["forbborb_msg_id"]:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            # check we're in a guild and it's cached
            print("ForbOrBorb: guild is none, aborting")
            return

        try:
            role_id = self.emoji_to_role[payload.emoji]
        except KeyError:
            # if we don't care about this emoji, exit
            return

        role = guild.get_role(role_id)
        if role is None:
            print("ForbOrBorb: A role was not found, aborting")
            return

        # payload for 'on_raw_reaction_remove' does not provide '.member'
        # so we must get it ourselves from .user_id
        # fetch_ used as get_ quite consistently returns None
        member = await guild.fetch_member(payload.user_id)
        assert member is not None

        # don't remove the role if it is the bot's reaction
        if payload.member == self.bot.user:
            return

        # Finally, remove the role.
        await member.remove_roles(role)

    @commands.command()
    @commands.is_owner()
    async def send_forbborb_msg(self, ctx: commands.Context):
        """Sends the forb vs borb message."""
        forbborb_msg = await ctx.send("FORB OR BORB?")
        info["forbborb_msg_id"] = forbborb_msg.id

        await forbborb_msg.add_reaction(discord.PartialEmoji(name="🦊"))
        await forbborb_msg.add_reaction(discord.PartialEmoji(name="🐦"))

        # record the id change in info json
        async with await anyio.open_file(forbborb_info_path, "w") as outfile:
            json_string = json.dumps(info, sort_keys=True, indent=4)
            await outfile.write(json_string)


async def setup(bot):
    await bot.add_cog(ForbOrBorb(bot))
