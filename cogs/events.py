from discord.ext import commands


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if message.content == "67":
            await message.channel.send(
                f"<@{message.author.id}>: Your parents don't love you."
            )

async def setup(bot):
    await bot.add_cog(Events(bot))
