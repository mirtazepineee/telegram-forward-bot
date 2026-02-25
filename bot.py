import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import os

# Настройки
OWNER_IDS = [756835347, 7768651103, 1877513295]  # СПИСОК ID владельцев
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8711050834:AAEWbit5d3Y5V9gtycADVFItze71_-3_PHk")

logging.basicConfig(level=logging.ERROR)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Пересылает сообщение всем владельцам"""
    
    if not update or not update.effective_user or not update.message:
        return
    
    user = update.effective_user
    message = update.message
    
    try:
        user_id = user.id if user else "Неизвестно"
        username = user.username if user and user.username else None
        
        if username:
            user_display = f"@{username}"
        else:
            user_display = f"ID: {user_id}"
    except:
        user_display = "Неизвестный пользователь"
    
    try:
        for owner_id in OWNER_IDS:
            try:
                if message.text:
                    await context.bot.send_message(
                        chat_id=owner_id,
                        text=f"{message.text}\n{user_display}"
                    )
                elif message.photo:
                    caption = f"{message.caption if message.caption else ''}\n{user_display}"
                    await context.bot.send_photo(
                        chat_id=owner_id,
                        photo=message.photo[-1].file_id,
                        caption=caption
                    )
                elif message.video:
                    caption = f"{message.caption if message.caption else ''}\n{user_display}"
                    await context.bot.send_video(
                        chat_id=owner_id,
                        video=message.video.file_id,
                        caption=caption
                    )
                elif message.document:
                    caption = f"{message.caption if message.caption else ''}\n{user_display}"
                    await context.bot.send_document(
                        chat_id=owner_id,
                        document=message.document.file_id,
                        caption=caption
                    )
                elif message.voice:
                    await context.bot.send_voice(
                        chat_id=owner_id,
                        voice=message.voice.file_id,
                        caption=user_display
                    )
                elif message.sticker:
                    await context.bot.send_sticker(
                        chat_id=owner_id,
                        sticker=message.sticker.file_id
                    )
                    await context.bot.send_message(
                        chat_id=owner_id,
                        text=user_display
                    )
                else:
                    await context.bot.send_message(
                        chat_id=owner_id,
                        text=f"Сообщение (другой тип)\n{user_display}"
                    )
            except Exception as e:
                continue
        
        await message.reply_text("✅")
    except Exception as e:
        pass

def main():
    print("🚀 Запуск бота...")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    print("✅ Бот успешно запущен!")
    app.run_polling()

if __name__ == '__main__':
    main()
