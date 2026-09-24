import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import random

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', description="sbeve", intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

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

bot.run(BOT_TOKEN)
