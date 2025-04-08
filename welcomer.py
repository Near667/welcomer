from keep_alive import keep_alive
import discord
from discord.ext import commands
import os
from PIL import Image, ImageDraw, ImageFont
import io
import aiohttp

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

WELCOME_CHANNEL_ID = 1358579349418414252  # Ton ID de salon
BACKGROUND_IMAGE_PATH = "background.jpg"  # Ton image de fond

@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user}")

async def create_welcome_image(member: discord.Member):
    # Load the background image
    background = Image.open(BACKGROUND_IMAGE_PATH).convert("RGBA")
    background = background.resize((800, 250))

    draw = ImageDraw.Draw(background)

    # Prepare the welcome text
    message = f"Welcome {member.name}!"
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), message, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Position text slightly left to center, leaving space for avatar
    text_x = 50
    text_y = (300 - text_height) // 2
    draw.text((text_x, text_y), message, font=font, fill=(255, 255, 255))

    # Download the avatar
    avatar_asset = member.display_avatar.replace(size=128)
    async with aiohttp.ClientSession() as session:
        async with session.get(str(avatar_asset.url)) as resp:
            avatar_bytes = await resp.read()

    avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
    avatar = avatar.resize((200, 200))

    # Make avatar circular
    mask = Image.new("L", (200, 200), 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.ellipse((0, 0, 200, 200), fill=255)
    avatar.putalpha(mask)

    # Place avatar on the right side (25px padding from right edge)
    avatar_x = 800 - 200 - 25
    avatar_y = 25
    background.paste(avatar, (avatar_x, avatar_y), avatar)

    with io.BytesIO() as image_binary:
        background.save(image_binary, "PNG")
        image_binary.seek(0)
        return discord.File(fp=image_binary, filename="welcome.png")

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        image = await create_welcome_image(member)
        await channel.send(
            content=f"Welcome to ogHannah's Community {member.mention} 🎉 !",
            file=image
        )

keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))