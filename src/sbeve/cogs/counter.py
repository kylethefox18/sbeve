import discord
from discord.ext import commands


# Define a simple persistent View that gives us a counter button
# note: does not actually persist the count over restarts
class PersistentCounter(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    # Define the actual button
    # When pressed, this increments the number displayed.
    @discord.ui.button(
        label="Start counting!",
        style=discord.ButtonStyle.primary,
        custom_id="persistent_counter:counter",
    )
    async def count(self, interaction: discord.Interaction, button: discord.ui.Button):
        print(button.label)
        try:
            number = int(button.label)
        except ValueError:
            number = 0

        button.label = str(number + 1)
        """Increases count on pressed button by 1."""

        # Update the message with our updated selves

        await interaction.response.edit_message(view=self)

        # Tell user they interacted
        await interaction.followup.send(
            interaction.user.display_name + " counted.", ephemeral=True
        )


class Counter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    @commands.guild_only()
    @commands.check_any(
        commands.is_owner(),
        commands.has_guild_permissions(administrator=True),
    )
    async def start_counter(self, ctx: commands.Context):
        """Starts a counter for pressing."""
        await ctx.send("Number bigger button", view=PersistentCounter())


async def setup(bot):
    await bot.add_cog(Counter(bot))
    bot.add_view(PersistentCounter())
