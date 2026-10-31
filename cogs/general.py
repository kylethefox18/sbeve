import random

import discord
from discord.ext import commands
from discord.utils import get

from config import config

intents = discord.Intents.default()


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    async def add(
        self,
        ctx,
        left: int = commands.parameter(description="One integer to add."),
        right: int = commands.parameter(description="Another integer to add."),
    ):
        """Adds two integers together.

        Example: $add 2 3
        """
        await ctx.send(left + right)

    @commands.hybrid_command()
    async def joined(
        self,
        ctx,
        member: discord.Member = commands.parameter(  # noqa: B008
            description="The member whose join date to check."
        ),
    ):
        """Says when a member joined.

        Member must be a member of the server.
        Example: $joined "{bot_name}"
        """
        # Join can be none: handle it.
        if member.joined_at is None:
            await ctx.send(f"{member} has no join date.")
        else:
            await ctx.send(
                f"{member} joined {discord.utils.format_dt(member.joined_at)}"
            )

    @commands.hybrid_command()
    async def roll(
        self,
        ctx,
        dice: str = commands.parameter(description="The NdN formatted string."),
    ):
        """Rolls dice from input in NdN format.

        The first N is the number of dice, the second N is the side count of the dice.
        Example: $roll 10d6
        """
        try:
            rolls, num_sides = map(int, dice.split("d"))
            if num_sides < 1:
                await ctx.send(
                    f"Your {num_sides}-dimensional object{'' if rolls == 1 else 's'}"
                    f" vanished into the {num_sides}th dimension."
                )
                return

            if num_sides > 999:
                await ctx.send(
                    f"Your {'sphere' if rolls == 1 else 'spheres'} rolled around."
                )
                return

            if rolls > 300:  # otherwise return message gets too long
                await ctx.send(
                    "Hundreds of dice clattered onto the floor, too many to count.\n"
                    "You're gonna have to clean that up."
                )
                return
            if rolls == 0:
                await ctx.send(f"You lamented not having any d{num_sides}s.")
                return

            if rolls < 0:
                rolls_list = [
                    -random.randint(1, num_sides) for _ in range(0, rolls, -1)
                ]
                total = sum(rolls_list)
                await ctx.send(f"""
{-rolls} d{num_sides}{"s" if rolls < -1 else ""} were unrolled and their results were:
{rolls_list}
respectively. Summed together that is {total}.
    """)
                return

            rolls_list = [random.randint(1, num_sides) for _ in range(rolls)]
            total = sum(rolls_list)

            await ctx.send(f"""
{rolls} d{num_sides}{"s" if rolls > 1 else ""} were rolled and their results were:
{rolls_list}
respectively. Summed together that is {total}.
    """)
        except Exception:
            await ctx.send("Format must be in NdN boi.")
            return

    @commands.hybrid_command()
    @commands.check_any(
        commands.has_role(config["staff_member_role_id"]),
        commands.has_guild_permissions(administrator=True),
    )
    async def get_sticker_from_id(
        self,
        ctx,
        sticker_id: str = commands.parameter(
            description="The ID of the sticker to get."
        ),
    ):
        """Gets a sticker given its id.

        In effect: takes in the id and returns:
        https://cdn.discordapp.com/stickers/<sticker-id>.png

        If the sticker is animated, you might need to go to
        https://cdn.discordapp.com/stickers/<sticker-id>.json
        download the file, and go to a site like
        https://lottieto.com/json-to-gif
        and convert the file to a GIF there.
        """

        sticker_id = int(sticker_id)
        await ctx.send(f"https://cdn.discordapp.com/stickers/{sticker_id}.png")

    @commands.hybrid_command()
    async def is_admin(
        self,
        ctx,
        member: discord.Member = commands.parameter(  # noqa: B008
            description="The member to check."
        ),
    ):
        """Checks whether a member is an admin.

        Example: $is_admin {bot_name}"""
        await ctx.send(
            f"{member.display_name} " + f"{
                'has' if get(member.roles, id=config['admin_role_id']) else 'has not'
            } "
            "the magical A powers."
        )

    @commands.hybrid_command()
    async def is_staff_member(
        self,
        ctx,
        member: discord.Member = commands.parameter(  # noqa: B008
            description="The member to check."
        ),
    ):
        """Checks whether a member is a staff member.

        Example: $is_staff_member {bot_name}"""
        await ctx.send(
            f"{member.display_name} " + f"{
                'has'
                if get(member.roles, id=config['staff_member_role_id'])
                else 'has not'
            } "
            "the magical Super Mario powers."
        )

    @commands.hybrid_command()
    @commands.check_any(
        commands.has_role(config["admin_role_id"]),
        commands.has_guild_permissions(administrator=True),
    )
    async def change_nickname(
        self,
        ctx,
        new_nickname: str = commands.parameter(
            description="What to set the nickname to."
        ),
    ):
        bot = ctx.guild.get_member(self.bot.user.id)
        await bot.edit(nick=new_nickname)
        await ctx.send(f"Nickname changed to {new_nickname}", ephemeral=True)


async def setup(bot):
    await bot.add_cog(General(bot))
