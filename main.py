import discord
from discord.ext import commands, tasks
import os
import webserver  # Make sure this is in the same folder
import asyncio

# ==== CONFIGURATION ====
DISCORD_TOKEN = os.environ['discordkey']  # Your environment variable on Render
GUILD_ID = 1430230064326508618
ROLE_ID = 1430230671707607051
CORRECT_KEY = "ambotunsa"
OWNER_ID = 1160070826276683918
# ========================

# Start the Flask keep-alive server
webserver.keep_alive()

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Store the last verification message to refresh it
verification_message = None
verification_channel_id = None  # Will store the channel ID where setup was used

# Modal for key input
class VerifyModal(discord.ui.Modal, title="Enter Verification Key"):
    key_input = discord.ui.TextInput(
        label="Enter your key",
        placeholder="Type your key here...",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        if self.key_input.value.strip() == CORRECT_KEY:
            role = interaction.guild.get_role(ROLE_ID)
            if role:
                await interaction.user.add_roles(role)
                await interaction.response.send_message("verified naka wow", ephemeral=True)
            else:
                await interaction.response.send_message("Role not found.", ephemeral=True)
        else:
            await interaction.response.send_message("di mao ang key!", ephemeral=True)

# Dropdown (select menu) for verification
class VerifyDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Click to Verify", description="Open the verification modal")
        ]
        super().__init__(placeholder="Select to verify...", options=options)

    async def callback(self, interaction: discord.Interaction):
        # Open the verification modal when the user selects the option
        await interaction.response.send_modal(VerifyModal())

# View containing the dropdown
class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(VerifyDropdown())

# Setup command
@bot.command()
async def setup(ctx):
    global verification_message, verification_channel_id

    if ctx.author.id != OWNER_ID:
        await ctx.reply("You are not allowed to use this command.", delete_after=5)
        return

    embed = discord.Embed(
        title="Verification",
        description="Use the dropdown below to verify. You will need a key.",
        color=discord.Color.blurple()
    )
    verification_channel_id = ctx.channel.id
    verification_message = await ctx.send(embed=embed, view=VerifyView())

    try:
        await ctx.message.delete()
    except discord.Forbidden:
        print("Bot missing permissions to delete messages.")

# Task to refresh the verification message every 15 minutes
@tasks.loop(minutes=15)
async def refresh_verification_message():
    global verification_message, verification_channel_id
    if verification_message and verification_channel_id:
        channel = bot.get_channel(verification_channel_id)
        if channel:
            try:
                await verification_message.delete()
            except discord.Forbidden:
                pass  # ignore if can't delete
            embed = discord.Embed(
                title="Verification",
                description="Use the dropdown below to verify. You will need a key.",
                color=discord.Color.blurple()
            )
            verification_message = await channel.send(embed=embed, view=VerifyView())

# On ready event
@bot.event
async def on_ready():
    stream = discord.Streaming(
        name="hi dihren",
        url="https://www.youtube.com/watch?v=-SjPVVeNdKY"
    )
    await bot.change_presence(status=discord.Status.online, activity=stream)
    print(f"Logged in as {bot.user}")
    refresh_verification_message.start()  # start the auto-refresh task

# Run bot
bot.run(DISCORD_TOKEN)
