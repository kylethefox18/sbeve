import json
import os
import random

import anyio
import discord
from discord.ext import commands
from discord.utils import get
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

with open('config.json', 'r') as f:
    config = json.load(f)

BOT_LOGS_CHANNEL_ID = config['BOT_LOGS_CHANNEL_ID']
MODMAIL_CATEGORY_ID = config['MODMAIL_CATEGORY_ID']
MODMAIL_LOGS_CHANNEL_ID = config['MODMAIL_LOGS_CHANNEL_ID']
ARCHIVE_CATEGORY_ID = config['ARCHIVE_CATEGORY_ID']
ADMIN_ROLE_NAME = config['ADMIN_ROLE_NAME']
STAFF_MEMBER_ROLE_NAME = config['STAFF_MEMBER_ROLE_NAME']
STAFF_MEMBER_ROLE_ID = config['STAFF_MEMBER_ROLE_ID']

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
    async def count(
            self, interaction: discord.Interaction, button: discord.ui.Button):
        number = int(button.label) if button.label else 0
        button.label = str(number + 1)
        """Increases count on pressed button by 1."""

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
                      'pressed open modmail button.')
        print(action_msg)
        await logs_channel.send(action_msg)

        # create a new modmail channel
        modmail_channel = await create_modmail_channel(
                interaction.guild,
                interaction.user,
                "Open Modmail button pressed")

        await interaction.response.send_message(
                f'{interaction.user.name}: '
                f'Modmail opened, in <#{modmail_channel.id}>',
                ephemeral=True
                )

async def create_modmail_channel(
    guild: discord.Guild,
    user_for: discord.User,
    reason: str
    ):
    """Creates a temporary modmail channel.

    This is a helper function for use with the 'open modmail button'.
    Keyword arguments:
    guild -- the guild in which to create the channel
    user_for -- the member for which to create the channel
    reason -- the reason for creating the channel
    """
    modmail_id = config["MODMAIL_NEXT_ID"]
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True),
        user_for: discord.PermissionOverwrite(read_messages=True),
        guild.get_role(STAFF_MEMBER_ROLE_ID):
            discord.PermissionOverwrite(read_messages=True),
    }

    # make sure we are in a guild
    assert guild is not None

    # create the channel
    new_channel = await guild.create_text_channel(
        name=f'modmail-ticket-{modmail_id}',
        overwrites=overwrites,
        topic=str(user_for.id),
        reason=reason,
        category=guild.get_channel(MODMAIL_CATEGORY_ID)
    )
    await logs_channel.send(
            f'Modmail channel <#{new_channel.id}> created for <@{user_for.id}>')

    # an id was used. go to the next one
    config["MODMAIL_NEXT_ID"] += 1

    # record that the id was used in config
    async with await anyio.open_file('config.json', 'w') as outfile:
        json_string = json.dumps(config, sort_keys=True, indent=4)
        await outfile.write(json_string)

    await new_channel.send(f'Hello <@{user_for.id}>\n'
                           'What can we help you with?')
    return new_channel

class CustomBot(commands.Bot):
    # Suppress error on the User attribute being None
    user: discord.ClientUser

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def setup_hook(self) -> None:
        # Register the persistent views for listening here
        # This does not send the view to any message.
        # In order to do this, you must first send a message with the View.
        self.add_view(PersistentCounter())
        self.add_view(PersistentModmailButton())

    async def on_ready(self):
        print(f'We have logged in as {self.user} (ID: {self.user.id})')
        print('--------')
        global logs_channel
        logs_channel = await bot.fetch_channel(BOT_LOGS_CHANNEL_ID)

    async def on_command_error(self, context, exception, /):
        await super().on_command_error(context, exception)
        await context.channel.send(f'Error in command {context.command.name}:\n'
                                   f'Is your input correct? '
                                   f'Check $help {context.command.name}.')

class MyHelpCommand(commands.DefaultHelpCommand):
    def get_ending_note(self):
        return 'Type $help command for more info on a command.\nSbeve out.'

help_command = MyHelpCommand(
    no_category="Commands"
)

bot = CustomBot(
    command_prefix='$',
    description="sbeve sbeves.",
    intents=intents,
    help_command = help_command
)

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
async def add(
    ctx,
    left: int = commands.parameter(description="One integer to add."),
    right: int = commands.parameter(description="Another integer to add.")
    ):
    """Adds two integers together.

Example: $add 2 3
    """
    await ctx.send(left + right)

@bot.command()
async def joined(
    ctx,
    member: discord.Member = commands.parameter( # noqa: B008
        description="The member whose join date to check."
        )
    ):
    """Says when a member joined.

Member must be a member of the server.
Example: $joined Sbeve#6493
    """
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
async def roll(
    ctx,
    dice: str = commands.parameter(description="The NdN formatted string.")
    ):
    """Rolls dice from input in NdN format.

The first N is the number of dice, the second N is the side count of the dice.
Example: $roll 10d6
    """
    try:
        rolls, num_sides = map(int, dice.split('d'))
        if (num_sides < 1):
            await ctx.send(
                f'Your {num_sides}-dimensional object{'' if rolls == 1 else 's'}'
                f' vanished into the {num_sides}th dimension.'
            )
            return

        if (num_sides > 999):
            await ctx.send(
                f'Your {'sphere' if rolls == 1 else 'spheres'} rolled around.'
            )
            return

        if (rolls > 300): # otherwise return message gets too long
            await ctx.send(
                'Hundreds of dice clattered onto the floor, too many to count.\n'
                'You\'re gonna have to clean that up.'
            )
            return
        if (rolls == 0):
            await ctx.send(
                f'You lamented not having any d{num_sides}s.'
            )
            return

        if (rolls < 0):
            rolls_list = [-random.randint(1, num_sides) for _ in range(0, rolls, -1)]
            total = sum(rolls_list)
            await ctx.send(f'''
{-rolls} d{num_sides}{'s' if rolls < -1 else ''} were unrolled and their results were:
{rolls_list}
respectively. Summed together that is {total}.
''')
            return

        rolls_list = [random.randint(1, num_sides) for _ in range(rolls)]
        total = sum(rolls_list)

        await ctx.send(f'''
{rolls} d{num_sides}{'s' if rolls > 1 else ''} were rolled and their results were:
{rolls_list}
respectively. Summed together that is {total}.
''')
    except Exception:
        await ctx.send('Format must be in NdN boi.')
        return

@bot.command()
@commands.has_role(STAFF_MEMBER_ROLE_NAME)
async def send_modmail_embed(ctx):
    """Sends the "Open Modmail" embed."""
    embed = discord.Embed(title="Modmail System",
                      description="Welcome to Modmail!",
                      colour=0xff7800)

    embed.set_author(name="Form of Communication")

    embed.add_field(name="Purpose",
                    value="If you click the button below, you will create a "
                    "temporary chat inside of our server which will allow you to "
                    "communicate with the staff team! You can voice your concerns, "
                    "bring new ideas to the staff team or even ask any question "
                    "regarding the server. You can even apply for the artist role "
                    "this way!\n\n"
                    "This form of communication is to be taken seriously. Misuse or "
                    "abuse of this feature will result in consequences.",
                    inline=False)

    embed.set_footer(
        text="The Anthro Inn Staff Team",
        icon_url="https://i.imgur.com/3V1A55G.png"
        )

    await ctx.send(embed=embed, view=PersistentModmailButton())

@bot.command()
async def close_modmail(ctx):
    """Closes the modmail channel it is called in."""
    if ctx.channel.name.startswith("modmail-ticket-"):
        await ctx.send('Closing ticket...')

        # get the user for whom the channel is
        user = await bot.fetch_user(ctx.channel.topic)
        # retrieve all the messages in the channel
        messages = [ message async for message in
                    ctx.channel.history(limit=None, oldest_first=True)]

        # parse modmail ticket's id and generate file path
        modmail_id = int(ctx.channel.name.split('-')[2])
        filename = f"{ctx.channel.name}-{ctx.channel.topic}.md"
        filepath = f"modmail-logs/{filename}"

        # use a set to only show user IDs the first time
        ids_shown = {user.id,} # the user for's id is shown in header

        # read all messages into the file
        with open(filepath, "w") as file:
            file.write(f"# Log of Modmail #{modmail_id} for {user.name} "
                       f"(ID {user.id})  \n\n")
            for message in messages:
                file.write(f"{message.author.name}"
                    f"{'' if message.author.id in ids_shown
                           else f" (id {message.author.id})"
                    }: {message.content}  \n")
                ids_shown.add(message.author.id)

        # send the file to the logs channel
        modmail_logs_channel = bot.get_channel(MODMAIL_LOGS_CHANNEL_ID)
        with open(filepath, 'rb') as fp:
            await modmail_logs_channel.send(f"Modmail #{modmail_id} for {user.name} "
                "closed. Logs attached.",
                file=discord.File(fp, filename)
            )

    else:
        await ctx.send('This isn\'t a modmail ticket, silly!')

@bot.command()
async def is_admin(
        ctx,
        member: discord.Member = commands.parameter( # noqa: B008
            description="The member to check."
            )
    ):
    """Checks whether a member is an admin.

    Example: $is_admin Sbeve#6493"""
    await ctx.send(f'{member.display_name} ' +
    f'{'has' if get(member.roles, name = ADMIN_ROLE_NAME) else 'has not'} '
    'the magical A powers.')

@bot.command()
async def is_staff_member(
        ctx,
        member: discord.Member = commands.parameter( # noqa: B008
            description="The member to check."
        )
    ):
    """Checks whether a member is a staff member.

    Example: $is_admin Sbeve#6493"""
    await ctx.send(f'{member.display_name} ' +
    f'{'has' if get(member.roles, name = STAFF_MEMBER_ROLE_NAME) else 'has not'} '
    'the magical Super Mario powers.')

bot.run(BOT_TOKEN)
