import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import pytesseract
from PIL import Image
import requests
from io import BytesIO

# Load token dari .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
SUBSCRIBER_ROLE_ID = int(os.getenv("SUBSCRIBER_ROLE_ID"))
SERVER_ID = int(os.getenv("SERVER_ID"))
ADMIN_CHANNEL_ID = int(os.getenv("ADMIN_CHANNEL_ID"))

# Konfigurasi intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.dm_messages = True

# Setup bot
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot berhasil login sebagai {bot.user}')

@bot.command()
async def verify(ctx):
    """Meminta user mengirim screenshot ke DM bot."""
    try:
        await ctx.author.send(
            "**🔍 Yo, waktunya verifikasi!**\n\n"
            "Kirim screenshot yang nunjukin kalau kamu udah subscribe ke channel.\n"
            "Pastikan ada tulisan **'Subscribed'** atau **'Disubscribe'** di screenshot.\n\n"
            "📸 **Tunggu sebentar ya, bot bakal cek otomatis!**"
        )
        await ctx.send(f"📩 {ctx.author.mention}, cek DM dari bot buat verifikasi!")
    except discord.Forbidden:
        await ctx.send(f"⚠️ {ctx.author.mention}, bot nggak bisa kirim DM! Cek pengaturan privasi kamu dulu.")

@bot.event
async def on_message(message):
    """Menangani DM user & memeriksa screenshot dengan OCR."""
    if message.guild is None and not message.author.bot:
        if message.attachments:
            attachment = message.attachments[0]
            image_url = attachment.url

            try:
                response = requests.get(image_url, timeout=10)
                response.raise_for_status()
                img = Image.open(BytesIO(response.content))
            except requests.RequestException:
                await message.channel.send("❌ Oops! Gagal ambil gambar, coba kirim lagi ya.")
                return

            # Proses OCR
            text = pytesseract.image_to_string(img, lang='eng+ind').lower()

            if "subscribed" in text or "disubscribe" in text:
                guild = bot.get_guild(SERVER_ID)
                admin_channel = guild.get_channel(ADMIN_CHANNEL_ID)
                role = discord.utils.get(guild.roles, id=SUBSCRIBER_ROLE_ID)
                member = guild.get_member(message.author.id)

                if admin_channel:
                    await admin_channel.send(
                        f"🔥 **Verifikasi Mantap!**\n"
                        f"🎉 {message.author.mention} baru aja diverifikasi sebagai **Crafting Master By Famouzak**!\n"
                        f"📸 Gambar: {attachment.url}"
                    )

                if role and member:
                    try:
                        await member.add_roles(role)
                        await message.channel.send(
                            f"✅ **Yo yo yo, what's up {message.author.mention}!** 🎊\n"
                            "Kamu udah resmi jadi **Crafting Master By Famouzak**!\n"
                            "🎁 **Enjoy spreadsheet-nya, semoga makin cuan di Albion!** 🚀"
                        )
                    except discord.Forbidden:
                        await message.channel.send("⚠️ Bot nggak bisa kasih role! Cek izin dulu ya.")
                else:
                    await message.channel.send("⚠️ Role atau member nggak ditemukan, coba lagi atau hubungi admin.")
            else:
                await message.channel.send(
                    f"❌ **Oops, {message.author.mention}!**\n"
                    "Bot nggak nemu kata **'Subscribed'** atau **'Disubscribe'** di screenshot kamu.\n"
                    "Coba lagi ya, pastiin tulisannya jelas! 📸"
                )

    await bot.process_commands(message)

# Jalankan bot
bot.run(TOKEN)