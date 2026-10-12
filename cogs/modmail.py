import io
import json

import anyio
import discord
from discord.ext import commands

from config import config, config_path


# A simple View for a persistent "Open Modmail" button
class PersistentModmailButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    # Define the Open Modmail button
    # When pressed, this does the following:
    #   Creates a temporary channel
    #   Allows all staff and user who pressed button to see channel
    @discord.ui.button(
        label="Open Modmail",
        style=discord.ButtonStyle.primary,
        custom_id="persistent_modmail_button:open_modmail",
    )
    async def open_modmail(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        # Log button press
        print(
            f"{interaction.user.name} (ID {interaction.user.id}) "
            + "pressed open modmail button."
        )

        # create a new modmail channel
        modmail_channel = await create_modmail_channel(
            interaction.guild,
            interaction.user,
            "Open Modmail button pressed",
        )

        await interaction.response.send_message(
            f"{interaction.user.name}: Modmail opened, in <#{modmail_channel.id}>",
            ephemeral=True,
        )


async def create_modmail_channel(
    guild: discord.Guild,
    user_for: discord.User,
    reason: str,
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
        guild.get_role(config["STAFF_MEMBER_ROLE_ID"]): discord.PermissionOverwrite(
            read_messages=True
        ),
    }

    # make sure we are in a guild
    assert guild is not None

    # create the channel
    new_channel = await guild.create_text_channel(
        name=f"modmail-ticket-{modmail_id}",
        overwrites=overwrites,
        topic=str(user_for.id),
        reason=reason,
        category=guild.get_channel(config["MODMAIL_CATEGORY_ID"]),
    )
    print(f"Modmail channel <#{new_channel.id}> created for <@{user_for.id}>")

    # an id was used. go to the next one
    config["MODMAIL_NEXT_ID"] += 1

    # record that the id was used in config
    async with await anyio.open_file(config_path, "w") as outfile:
        json_string = json.dumps(config, sort_keys=True, indent=4)
        await outfile.write(json_string)

    await new_channel.send(f"Hello <@{user_for.id}>\nWhat can we help you with?")
    return new_channel


class Modmail(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_role(config["STAFF_MEMBER_ROLE_NAME"])
    async def send_modmail_embed(self, ctx):
        """Sends the "Open Modmail" embed."""
        embed = discord.Embed(
            title="Modmail System", description="Welcome to Modmail!", colour=0xFF7800
        )

        embed.set_author(name="Form of Communication")

        embed.add_field(
            name="Purpose",
            value="If you click the button below, you will create a "
            "temporary chat inside of our server which will allow you to "
            "communicate with the staff team! You can voice your concerns, "
            "bring new ideas to the staff team or even ask any question "
            "regarding the server. You can even apply for the artist role "
            "this way!\n\n"
            "This form of communication is to be taken seriously. Misuse or "
            "abuse of this feature will result in consequences.",
            inline=False,
        )

        embed.set_footer(
            text="The Anthro Inn Staff Team", icon_url="https://i.imgur.com/3V1A55G.png"
        )

        await ctx.send(embed=embed, view=PersistentModmailButton())

    @commands.command()
    # requires no privilege checking because everyone who can see the modmail channel
    # should have the right to close it
    async def close_modmail(self, ctx):
        """Closes the modmail channel it is called in."""
        if ctx.channel.name.startswith("modmail-ticket-"):
            await ctx.send("Closing ticket...")

            # get the user for whom the channel is
            user = await self.bot.fetch_user(ctx.channel.topic)
            # retrieve all the messages in the channel
            messages = [
                message
                async for message in ctx.channel.history(limit=None, oldest_first=True)
            ]

            # parse modmail ticket's id and generate file path
            modmail_id = int(ctx.channel.name.split("-")[2])
            log_filename = f"{ctx.channel.name}-{ctx.channel.topic}.md"
            # this relative file path is fine in the cog, as it is relative to the bot
            # wherein the cog runs
            log_filepath = f"modmail-logs/{log_filename}"

            # log that modmail is being closed
            print(f"Closing and archiving modmail #{modmail_id}...")

            # record messages before ones with attachments
            msgs_before_with_attachments = [
                ""
            ]  # init with empty str for smth to append to
            # record messages with attachments
            msgs_with_attachments = []
            # record attachments info messages
            attachments_infos_all = []

            # use a set to only show user IDs the first time
            ids_shown = {
                user.id,
            }  # the user for's id is shown in header

            # read all messages into the file
            with open(log_filepath, "w") as file:
                file.write(
                    f"# Log of Modmail #{modmail_id} for {user.name} "
                    "(ID {user.id})  \n\n"
                )

                # go through all messages
                for message in messages:
                    # create log message with info
                    logged_message = (
                        f"{message.author.name}"
                        f"{
                            ''
                            if message.author.id in ids_shown
                            else f' (id {message.author.id})'
                        }"
                        f" at {message.created_at.strftime('%d %b %H:%M')}"
                        f"{
                            ''
                            if message.edited_at is None
                            else ' (edited '
                            f'{message.edited_at.strftime("%d %b %H:%M")})'
                        }"
                        f": {message.content}  \n"
                    )

                    if len(message.stickers) > 0:  # if the message had stickers
                        logged_message += (
                            "The above message also had the following "
                            + f"sticker{'' if len(message.stickers) == 1 else 's'}:  \n"
                            + "  \n".join(
                                [f"ID: `{sticker.id}`" for sticker in message.stickers]
                            )
                            + "  \n"
                        )

                    ids_shown.add(message.author.id)
                    file.write(logged_message)

                    if len(message.attachments) > 0:  # if msg has attachments
                        # add message to list of messages with attachments
                        msgs_with_attachments.append(message)

                        # move messages before attachment message to next
                        msgs_before_with_attachments.append("")

                        # put all the attachment infos into a list
                        attachments_info_str = []
                        for attachment in message.attachments:
                            # The attachment's media type type (parsed from media type)
                            if attachment.content_type is not None:
                                attachment_type = attachment.content_type.split("/")[0]
                            else:
                                attachment_type = None

                            # append the attachment's information
                            attachments_info_str.append(
                                (
                                    f"{attachment_type} "
                                    f"named {attachment.filename}, "
                                    f"id {attachment.id}"
                                )
                            )

                        # send the attachment info
                        file.write(
                            "The above message also had these attachments:  \n```"
                        )
                        file.write("  \n" + "  \n".join(attachments_info_str) + "  \n")
                        file.write(
                            "```  \nThese attachments have been resent alongside this "
                            "document in the logs channel.  \n\n"
                        )

                        # append the attachments info string
                        attachments_infos_all.append("\n".join(attachments_info_str))

                    else:  # it's a normal message
                        msgs_before_with_attachments[-1] += logged_message

            # send the file to the logs channel
            modmail_logs_channel = self.bot.get_channel(
                config["MODMAIL_LOGS_CHANNEL_ID"]
            )
            with open(log_filepath, "rb") as fp:
                logs_message = await modmail_logs_channel.send(
                    f"Modmail #{modmail_id} for {user.name} closed. Logs attached.",
                    file=discord.File(fp, log_filename),
                )

            # make a thread from the message with the file
            logs_thread = await logs_message.create_thread(
                name=f"Modmail #{modmail_id} for {user.name}"
            )
            # forward all messages with attachments to this thread
            for idx, msg in enumerate(msgs_with_attachments):
                # send all messages without attachments as .md file
                # turn the messages into a buffer
                # header is necessary, otherwise error 418 if two attachments are sent
                # after each other
                buffer_msgs_before = io.BytesIO(
                    (
                        "Messages between attachments:  \n"
                        + msgs_before_with_attachments[idx]
                    ).encode("utf-8")
                )
                # pass it into a discord.File
                file_msgs_before = discord.File(
                    buffer_msgs_before,
                    filename="messages.md",
                )
                # send the discord file
                await logs_thread.send(file=file_msgs_before)

                # forward the attachment and send its info
                await msg.forward(logs_thread)
                await logs_thread.send(
                    "The above message with attachments\n```"
                    f"{attachments_infos_all[idx]}\n```was sent by "
                    f"{msg.author.name} at <t:{int(msg.created_at.timestamp())}> "
                    f"({msg.created_at.strftime('%a %d %b %Y %H:%M')} UTC)."
                )

            # send the messages after the last attachment
            buffer_msgs_before = io.BytesIO(
                (
                    "Messages after last attachment:  \n"
                    + msgs_before_with_attachments[-1]
                ).encode("utf-8")
            )
            # pass it into a discord.File
            file_msgs_before = discord.File(
                buffer_msgs_before,
                filename="messages.md",
            )
            # send the discord file
            await logs_thread.send(file=file_msgs_before)

            print(f"Modmail #{modmail_id} closed and archived: {logs_thread.jump_url}")
            # delete the now completely archived thread
            await ctx.channel.delete(reason="Modmail completely archived.")

        else:
            await ctx.send("This isn't a modmail ticket, silly!")


async def setup(bot):
    await bot.add_cog(Modmail(bot))
    bot.add_view(PersistentModmailButton())
