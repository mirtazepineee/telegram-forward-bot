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

# СПЕЦИАЛЬНЫЙ ОБРАБОТЧИК ТОЛЬКО ДЛЯ ФОТО
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        print("=" * 50)
        print("📸 ПОЛУЧЕНО ФОТО!")
        
        # Информация об отправителе
        user = message.from_user
        user_id = user.id
        username = user.username
        user_display = f"@{username}" if username else f"ID: {user_id}"
        print(f"Отправитель: {user_display}")
        
        # Информация о чате
        chat_id = message.chat.id
        chat_type = message.chat.type
        print(f"Чат ID: {chat_id}, тип: {chat_type}")
        
        # Получаем фото
        photos = message.photo
        print(f"Количество фото в сообщении: {len(photos)}")
        
        # Берем самое качественное фото (последнее в списке)
        best_photo = photos[-1]
        file_id = best_photo.file_id
        file_size = best_photo.file_size
        file_width = best_photo.width
        file_height = best_photo.height
        
        print(f"Фото: file_id={file_id}, размер={file_size}, {file_width}x{file_height}")
        
        # Получаем подпись к фото
        caption = message.caption if message.caption else ""
        print(f"Подпись: '{caption}'")
        
        # Пересылаем каждому владельцу
        for owner_id in OWNER_IDS:
            try:
                print(f"🔄 Отправка фото владельцу {owner_id}...")
                
                # Формируем подпись
                final_caption = f"{caption}\n{user_display}" if caption else user_display
                
                # Отправляем фото
                sent_msg = bot.send_photo(
                    chat_id=owner_id,
                    photo=file_id,
                    caption=final_caption
                )
                print(f"✅ Фото успешно отправлено владельцу {owner_id}")
                
            except Exception as e:
                print(f"❌ Ошибка отправки владельцу {owner_id}: {type(e).__name__}: {e}")
        
        # Отвечаем пользователю
        bot.reply_to(message, "✅ Фото получено и отправлено!")
        print("✅ Ответ пользователю отправлен")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА В ОБРАБОТКЕ ФОТО: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        try:
            bot.reply_to(message, "❌ Ошибка при обработке фото")
        except:
            pass

# Обработчик для текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    try:
        # Игнорируем команды
        if message.text and message.text.startswith('/'):
            return
            
        print("💬 ПОЛУЧЕН ТЕКСТ")
        
        user = message.from_user
        username = user.username
        user_id = user.id
        user_display = f"@{username}" if username else f"ID: {user_id}"
        
        text = message.text if message.text else "[не текстовое сообщение]"
        print(f"Текст: {text[:100]}...")
        
        for owner_id in OWNER_IDS:
            try:
                bot.send_message(owner_id, f"{text}\n{user_display}")
                print(f"✅ Текст отправлен владельцу {owner_id}")
            except Exception as e:
                print(f"❌ Ошибка отправки текста владельцу {owner_id}: {e}")
        
        bot.reply_to(message, "✅")
        print("✅ Ответ пользователю отправлен")
        
    except Exception as e:
        print(f"❌ Ошибка обработки текста: {e}")

@app.route('/')
def home():
    return "Бот работает! 🤖 (фото+текст)"

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
    print(f"📋 Отправлять фото владельцам: {OWNER_IDS}")
    
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
