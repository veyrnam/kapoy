import discord
from discord.ext import commands, tasks
import os
import webserver  # Make sure this is in the same folder

# ==== CONFIGURATION ====
DISCORD_TOKEN = os.environ['discordkey']
GUILD_ID = 1430230064326508618
ROLE_ID = 1430230671707607051
CORRECT_KEY = "ambotunsa"
OWNER_ID = 1160070826276683918
# ========================

# Start Flask keep-alive
webserver.keep_alive()

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.reactions = True  # Needed to track reactions

bot = commands.Bot(command_prefix="!", intents=intents)

verification_message = None
verification_channel_id = None

# ========================
# Setup command
# ========================
@bot.command()
async def setup(ctx):
    global verification_message, verification_channel_id

    if ctx.author.id != OWNER_ID:
        await ctx.reply("You are not allowed to use this command.", delete_after=5)
        return

    embed = discord.Embed(
        title="Verification",
        description="React to this message to verify. You will be prompted to send your key.",
        color=discord.Color.blurple()
    )
    verification_channel_id = ctx.channel.id
    verification_message = await ctx.send(embed=embed)

    # Add a default reaction emoji
    await verification_message.add_reaction("✅")

    try:
        await ctx.message.delete()
    except discord.Forbidden:
        print("Bot missing permissions to delete messages.")

# ========================
# Reaction event
# ========================
@bot.event
async def on_reaction_add(reaction, user):
    global verification_message
    if user.bot:
        return

    if verification_message and reaction.message.id == verification_message.id:
        # Remove reaction so they can react again if needed
        try:
            await reaction.remove(user)
        except discord.Forbidden:
            pass

        # DM the user to send key
        try:
            await user.send("Send your key here if you're ready. Use `!verify <your_key>` in the server.")
        except discord.Forbidden:
            # If DMs blocked, send in the server channel
            channel = bot.get_channel(verification_channel_id)
            if channel:
                await channel.send(f"{user.mention}, send your key here if you're ready using `!verify <key>`.")

# ========================
# Verify command
# ========================
@bot.command(name="verify")  # Keep command name !verify
async def verify_command(ctx, *, key: str):
    if key.strip().lower() == CORRECT_KEY.lower():
        role = ctx.guild.get_role(ROLE_ID)
        if role:
            await ctx.author.add_roles(role)
            await ctx.reply("Verified! ✅", delete_after=10)
        else:
            await ctx.reply("Role not found.", delete_after=10)
    else:
        await ctx.reply("Wrong key! DM/PM jal for the key", delete_after=10)

# ========================
# On ready
# ========================
@bot.event
async def on_ready():
    stream = discord.Streaming(
        name="hi dihren",
        url="https://www.youtube.com/watch?v=-SjPVVeNdKY"
    )
    await bot.change_presence(status=discord.Status.online, activity=stream)
    print(f"Logged in as {bot.user}")

# ========================
# Run bot
# ========================
bot.run(DISCORD_TOKEN)
