import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import AccessTokenInvalid

# Isme apne main bot ke DB/Config functions import kar lena agar zaroorat ho
# e.g., from database.users_chats_db import db

@Client.on_message(filters.command("clone") & filters.private)
async def clone_bot(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(
            "**⚠️ Usage:**\n`/clone YOUR_BOT_TOKEN`\n\nBotFather se token nikaal kar yahan bhejo."
        )
    
    user_id = message.from_user.id
    user_token = message.text.split(None, 1)[1].strip()
    msg = await message.reply_text("🔄 **Checking Bot Token...**")

    try:
        # Clone bot ko initialize kar rahe hain
        clone_app = Client(
            name=f"clone_{user_id}",
            api_id=client.api_id,
            api_hash=client.api_hash,
            bot_token=user_token,
            plugins=dict(root="plugins")  # Purane plugins clone bot par bhi chalenge
        )
        
        await clone_app.start()
        bot_info = await clone_app.get_me()
        await clone_app.stop()

        # Database me token save karne ka logic yahan aayega
        # await db.add_clone(user_id, user_token, bot_info.username)

        await msg.edit_text(
            f"✅ **Bot Successfully Cloned!**\n\n"
            f"🤖 **Bot Name:** {bot_info.first_name}\n"
            f"👤 **Username:** @{bot_info.username}\n\n"
            f"Aapka clone bot ab ready hai!"
        )

    except AccessTokenInvalid:
        await msg.edit_text("❌ **Invalid Token!** Kripya sahi Bot Token daalein.")
    except Exception as e:
        await msg.edit_text(f"❌ **Error occurred:** `{str(e)}`")

