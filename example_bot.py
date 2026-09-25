import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import random

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
LOGS_CHANNEL_ID = os.getenv('LOGS_CHANNEL')
ON_OFF_CHANNEL_ID = os.getenv('ON_OFF_CHANNEL')
ADMIN_ROLE_ID = os.getenv('ADMIN_ROLE')
STAFF_MEMBER_ROLE_ID = os.getenv('STAFF_MEMBER_ROLE')

intents = discord.Intents.default()
intents.message_content = True

# Define a simple persistent View that gives us a counter button
class PersistentCounter(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    # Define the actual button
    # When pressed, this increments the number displayed.
    @discord.ui.button(label='0', style=discord.ButtonStyle.primary,
                       custom_id='persistent_counter:counter')
    async def count(self, interaction: discord.Interaction, button: discord.ui.Button):
        number = int(button.label) if button.label else 0
        button.label = str(number + 1)

        # Update the message with our updated selves
        await interaction.response.edit_message(view=self)

        # Tell user they interacted
        await interaction.followup.send(interaction.user.display_name +
                                                ' counted.', ephemeral=True)

class CustomBot(commands.Bot):
    # Suppress error on the User attribute being None
    user: discord.ClientUser

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def setup_hook(self) -> None:
        # Register the persistent view for listening here
        # This does not send the view to any message.
        # In order to do this, you must first send a message with the View.
        self.add_view(PersistentCounter())
        
    async def on_ready(self):
        print(f'We have logged in as {self.user} (ID: {self.user.id})')
        print('--------')
        global logs_channel
        logs_channel = await bot.fetch_channel(LOGS_CHANNEL_ID)
        global on_off_channel
        on_off_channel = await bot.fetch_channel(ON_OFF_CHANNEL_ID)
        await on_off_channel.send('Sbeve is actively sbeveing.')

    async def close(self):
        await on_off_channel.send('Sbeve ceases to actively sbeve.')
        await super().close()

bot = CustomBot(command_prefix='$', description="sbeve", intents=intents)

@bot.event

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content == "67":
        await message.channel.send(f'<@{message.author.id}>: Your parents don\'t love you.')

    await bot.process_commands(message)

@bot.command()
async def add(ctx, left: int, right: int):
    """Adds two numbers together."""
    await ctx.send(left + right)

@bot.command()
async def joined(ctx, member: discord.Member):
    """Says when a member joined."""
    # Join can be none: handle it.
    if member.joined_at is None:
        await ctx.send(f'{member} has no join date.')
    else:
        await ctx.send(f'{member} joined {discord.utils.format_dt(member.joined_at)}')

@bot.command()
@commands.is_owner()
async def counter(ctx: commands.Context):
    """Starts a counter for pressing."""
    await ctx.send('Number bigger button', view=PersistentCounter())

@bot.command()
async def roll(ctx, dice: str):
    """Rolls a dice in NdN format."""
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await ctx.send('Format must be in NdN boi.')
        return

    if (limit < 1):
        await ctx.send(
                f'Your {limit}-dimensional object vanished into the {limit}th dimension.'
                )
        return

    prefix = '';
    rolls_list = [];
    total = 0;
    for r in range(rolls):
        roll = random.randint(1, limit)
        total += roll
        rolls_list.append(roll)
        prefix = ', ';

    result = f'''{rolls} d{limit}s were rolled and their results were:
{rolls_list}
respectively. Summed together that is {total}.'''
    await ctx.send(result)

@bot.command()
async def send_modmail_embed(ctx):
    if (not isRole(ctx.message.author, STAFF_MEMBER_ROLE_ID)):
        fail_message = (f'send_modmail_embed: ' +
            f'User {ctx.message.author} tried to execute function. Is not staff.')
        print(fail_message)
        await logs_channel.send(fail_message)
        return

    embed = discord.Embed(title="Open a Modmail",
                          description="Click the button below to open a modmail. "
                          "This will add you to a temporary modmail channel where staff "
                          "will be notified.",
                          colour=0x00b0f4)
    await ctx.send(embed=embed)

@bot.command()
async def isAdmin(ctx, member: discord.Member):
    await ctx.send(f'{member.display_name} ' +
    f'{'has' if isRole(member, ADMIN_ROLE_ID) else 'does not have'} ' +
    f'the magical A powers.')

@bot.command()
async def isStaffMember(ctx, member: discord.Member):
    await ctx.send(f'{member.display_name} ' +
    f'{'has' if isRole(member, STAFF_MEMBER_ROLE_ID) else 'does not have'} ' +
    f'the magical Super Mario powers.')

def isRole(member, roleID):
    roles = member.roles
    memberIsRole = False
    for role in roles:
        if str(role.id) == roleID:
            memberIsRole = True

    return memberIsRole

bot.run(BOT_TOKEN)
