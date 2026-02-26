import telebot
import os
import threading
import time
from flask import Flask

# Настройки
BOT_TOKEN = "8711050834:AAEWbit5d3Y5V9gtycADVFItze71_-3_PHk"
OWNER_IDS = [756835347, 7768651103, 1877513295]  # ID владельцев

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Флаг для контроля запуска
polling_started = False

print("🔄 Сброс подключений...")
try:
    bot.remove_webhook()
    time.sleep(1)
    bot_info = bot.get_me()
    print(f"✅ Бот @{bot_info.username} инициализирован")
except Exception as e:
    print(f"⚠️ Ошибка при сбросе: {e}")

# Обработчик для фото
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        user = message.from_user
        username = user.username
        user_id = user.id
        user_display = f"@{username}" if username else f"ID: {user_id}"
        
        # Получаем фото самого высокого качества
        photo = message.photo[-1]
        file_id = photo.file_id
        caption = message.caption if message.caption else ""
        
        print(f"📸 Получено фото от {user_display}")
        
        # Пересылаем всем владельцам
        for owner_id in OWNER_IDS:
            try:
                bot.send_photo(
                    owner_id, 
                    file_id,
                    caption=f"{caption}\n{user_display}" if caption else user_display
                )
                print(f"✅ Фото отправлено владельцу {owner_id}")
            except Exception as e:
                print(f"❌ Ошибка отправки фото владельцу {owner_id}: {e}")
        
        # Отвечаем пользователю
        bot.reply_to(message, "✅ Фото получено!")
        
    except Exception as e:
        print(f"❌ Ошибка обработки фото: {e}")
        bot.reply_to(message, "❌ Ошибка при обработке фото")

# Обработчик для видео
@bot.message_handler(content_types=['video'])
def handle_video(message):
    try:
        user = message.from_user
        username = user.username
        user_id = user.id
        user_display = f"@{username}" if username else f"ID: {user_id}"
        
        video = message.video
        file_id = video.file_id
        caption = message.caption if message.caption else ""
        
        print(f"🎥 Получено видео от {user_display}")
        
        for owner_id in OWNER_IDS:
            try:
                bot.send_video(
                    owner_id, 
                    file_id,
                    caption=f"{caption}\n{user_display}" if caption else user_display
                )
            except Exception as e:
                print(f"❌ Ошибка отправки видео владельцу {owner_id}: {e}")
        
        bot.reply_to(message, "✅ Видео получено!")
        
    except Exception as e:
        print(f"❌ Ошибка обработки видео: {e}")
        bot.reply_to(message, "❌ Ошибка при обработке видео")

# Обработчик для документов
@bot.message_handler(content_types=['document'])
def handle_document(message):
    try:
        user = message.from_user
        username = user.username
        user_id = user.id
        user_display = f"@{username}" if username else f"ID: {user_id}"
        
        document = message.document
        file_id = document.file_id
        caption = message.caption if message.caption else ""
        
        print(f"📄 Получен документ от {user_display}")
        
        for owner_id in OWNER_IDS:
            try:
                bot.send_document(
                    owner_id, 
                    file_id,
                    caption=f"{caption}\n{user_display}" if caption else user_display
                )
            except Exception as e:
                print(f"❌ Ошибка отправки документа владельцу {owner_id}: {e}")
        
        bot.reply_to(message, "✅ Документ получен!")
        
    except Exception as e:
        print(f"❌ Ошибка обработки документа: {e}")
        bot.reply_to(message, "❌ Ошибка при обработке документа")

# Обработчик для голосовых
@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    try:
        user = message.from_user
        username = user.username
        user_id = user.id
        user_display = f"@{username}" if username else f"ID: {user_id}"
        
        voice = message.voice
        file_id = voice.file_id
        
        print(f"🎤 Получено голосовое от {user_display}")
        
        for owner_id in OWNER_IDS:
            try:
                bot.send_voice(owner_id, file_id, caption=user_display)
            except Exception as e:
                print(f"❌ Ошибка отправки голосового владельцу {owner_id}: {e}")
        
        bot.reply_to(message, "✅ Голосовое получено!")
        
    except Exception as e:
        print(f"❌ Ошибка обработки голосового: {e}")
        bot.reply_to(message, "❌ Ошибка при обработке голосового")

# Обработчик для стикеров
@bot.message_handler(content_types=['sticker'])
def handle_sticker(message):
    try:
        user = message.from_user
        username = user.username
        user_id = user.id
        user_display = f"@{username}" if username else f"ID: {user_id}"
        
        sticker = message.sticker
        file_id = sticker.file_id
        
        print(f"😊 Получен стикер от {user_display}")
        
        for owner_id in OWNER_IDS:
            try:
                bot.send_sticker(owner_id, file_id)
                bot.send_message(owner_id, user_display)
            except Exception as e:
                print(f"❌ Ошибка отправки стикера владельцу {owner_id}: {e}")
        
        bot.reply_to(message, "✅ Стикер получен!")
        
    except Exception as e:
        print(f"❌ Ошибка обработки стикера: {e}")
        bot.reply_to(message, "❌ Ошибка при обработке стикера")

# Обработчик для текста и всего остального
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    try:
        user = message.from_user
        username = user.username
        user_id = user.id
        user_display = f"@{username}" if username else f"ID: {user_id}"
        
        text = message.text
        
        print(f"💬 Получен текст от {user_display}: {text[:50]}...")
        
        for owner_id in OWNER_IDS:
            try:
                bot.send_message(owner_id, f"{text}\n{user_display}")
            except Exception as e:
                print(f"❌ Ошибка отправки текста владельцу {owner_id}: {e}")
        
        bot.reply_to(message, "✅")
        
    except Exception as e:
        print(f"❌ Ошибка обработки текста: {e}")
        bot.reply_to(message, "❌ Ошибка")

@app.route('/')
def home():
    return "Бот работает! 🤖"

@app.route('/health')
def health():
    return "OK", 200

def start_bot():
    """Запуск бота с защитой от множественных подключений"""
    global polling_started
    
    if polling_started:
        return
    
    polling_started = True
    print("🚀 Запуск бота...")
    
    while True:
        try:
            bot.remove_webhook()
            time.sleep(1)
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"❌ Ошибка в polling: {e}")
            time.sleep(5)
            continue

if __name__ == '__main__':
    if not polling_started:
        bot_thread = threading.Thread(target=start_bot, daemon=True)
        bot_thread.start()
        time.sleep(2)
    
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
