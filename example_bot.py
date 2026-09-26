import random
from datetime import datetime
import os
from dotenv import load_dotenv
import json
import discord
from discord.ext import commands
from discord.utils import get

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

with open('config.json', 'r') as f:
    config = json.load(f)

LOGS_CHANNEL_ID = config['LOGS_CHANNEL_ID']
ON_OFF_CHANNEL_ID = config['ON_OFF_CHANNEL_ID']
ADMIN_ROLE_NAME = config['ADMIN_ROLE_NAME']
STAFF_MEMBER_ROLE_NAME = config['STAFF_MEMBER_ROLE_NAME']

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

# A simple View for a persistent "Open Modmail" button
class PersistentModmailButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    # Define the Open Modmail button
    # When pressed, this does the following:
    #   Creates a temporary channel
    #   Allows all staff and user who pressed button to see channel
    @discord.ui.button(label='Open Modmail', style=discord.ButtonStyle.primary,
                       custom_id='persistent_modmail_button:open_modmail')
    async def open_modmail(self, interaction: discord.Interaction,
                           button: discord.ui.Button):
        # Log button press
        action_msg = (f'{interaction.user.name} (ID {interaction.user.id}) ' +
        f'pressed open modmail button.')
        print(action_msg)
        await logs_channel.send(action_msg)
        # Tell user they interacted
        await interaction.response.send_message(
                f'{interaction.user.name}: Opening modmail...',
                ephemeral=True
                )
        # TODO: add modmail opening code

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
        await message.channel.send(
                f'<@{message.author.id}>: Your parents don\'t love you.'
                )

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
@commands.has_role(STAFF_MEMBER_ROLE_NAME)
async def send_modmail_embed(ctx):
    embed = discord.Embed(title="Modmail System",
                      description="Welcome to Modmail!",
                      colour=0xff7800,
                      timestamp=datetime.now())
    
    embed.set_author(name="Form of Communication")
    
    embed.add_field(name="Purpose",
                    value="If you click the button below, you will create a temporary "
                    "chat inside of our server which will allow you to communicate with "
                    "the staff team! You can voice your concerns, bring new ideas to the "
                    "staff team or even ask any question regarding the server. You can "
                    "even apply for the artist role this way!\n\nThis form of "
                    "communication is to be taken seriously. Misuse or abuse of this "
                    "feature will result in consequences.",
                    inline=False)
    
    embed.set_footer(
        text="The Anthro Inn Staff Team",
        icon_url="https://media.discordapp.net/attachments/806188733514121239/"
        "1553161882205032488/TAIlogo.png?ex=6ab83e39&is=6ab6ecb9&hm=1f4deb524bf933fc528"
        "002b10598046979b2e1a41f36bd5d0c6df7b05ce86dbc&=&format=webp&quality=lossless"
        "&width=1536&height=1067"
        )
    
    await ctx.send(embed=embed, view=PersistentModmailButton())

@bot.command()
async def is_admin(ctx, member: discord.Member):
    await ctx.send(f'{member.display_name} ' +
    f'{'has' if get(member.roles, name = ADMIN_ROLE_NAME) else 'does not have'} ' +
    f'the magical A powers.')

@bot.command()
async def is_staff_member(ctx, member: discord.Member):
    await ctx.send(f'{member.display_name} ' +
    f'{'has' if get(member.roles, name = STAFF_MEMBER_ROLE_NAME) else 'does not have'} ' +
    f'the magical Super Mario powers.')

bot.run(BOT_TOKEN)
