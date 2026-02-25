import telebot
import os
import time
import threading
from flask import Flask

# Настройки
BOT_TOKEN = "8711050834:AAEWbit5d3Y5V9gtycADVFItze71_-3_PHk"
OWNER_IDS = [756835347, 7768651103, 1877513295]  # ID владельцев

# Создаём бота
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Обработчик всех сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        # Получаем информацию об отправителе
        user = message.from_user
        username = user.username
        user_id = user.id
        
        if username:
            user_display = f"@{username}"
        else:
            user_display = f"ID: {user_id}"
        
        # Пересылаем всем владельцам
        for owner_id in OWNER_IDS:
            try:
                # Текст
                if message.text:
                    bot.send_message(
                        owner_id,
                        f"{message.text}\n{user_display}"
                    )
                # Фото
                elif message.photo:
                    file_id = message.photo[-1].file_id
                    caption = f"{message.caption if message.caption else ''}\n{user_display}"
                    bot.send_photo(owner_id, file_id, caption=caption)
                # Видео
                elif message.video:
                    file_id = message.video.file_id
                    caption = f"{message.caption if message.caption else ''}\n{user_display}"
                    bot.send_video(owner_id, file_id, caption=caption)
                # Документы
                elif message.document:
                    file_id = message.document.file_id
                    caption = f"{message.caption if message.caption else ''}\n{user_display}"
                    bot.send_document(owner_id, file_id, caption=caption)
                # Голосовые
                elif message.voice:
                    file_id = message.voice.file_id
                    bot.send_voice(owner_id, file_id, caption=user_display)
                # Стикеры
                elif message.sticker:
                    file_id = message.sticker.file_id
                    bot.send_sticker(owner_id, file_id)
                    bot.send_message(owner_id, user_display)
                # Остальное
                else:
                    bot.send_message(
                        owner_id,
                        f"Сообщение (другой тип)\n{user_display}"
                    )
            except Exception as e:
                print(f"Ошибка отправки владельцу {owner_id}: {e}")
                continue
        
        # Отвечаем пользователю
        bot.reply_to(message, "✅")
        
    except Exception as e:
        print(f"Общая ошибка: {e}")

@app.route('/')
def home():
    return "Бот работает! 🤖"

def bot_polling():
    """Запуск бота в отдельном потоке"""
    print("🚀 Запуск бота...")
    bot.infinity_polling()

if __name__ == '__main__':
    # Запускаем бота в фоновом потоке
    bot_thread = threading.Thread(target=bot_polling, daemon=True)
    bot_thread.start()
    
    # Запускаем Flask сервер (нужен для Render)
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
