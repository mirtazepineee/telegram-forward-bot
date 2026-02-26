import telebot
import os
import threading
import time
from flask import Flask

# Настройки
BOT_TOKEN = "8711050834:AAEWbit5d3Y5V9gtycADVFItze71_-3_PHk"
OWNER_IDS = [756835347, 7768651103, 1877513295]

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Хранилище для групп фото
photo_groups = {}  # media_group_id -> {'files': [], 'caption': '', 'processed': False}
group_timers = {}

polling_started = False

print("🔄 Сброс подключений...")
try:
    bot.remove_webhook()
    time.sleep(1)
    bot_info = bot.get_me()
    print(f"✅ Бот @{bot_info.username} инициализирован")
except Exception as e:
    print(f"⚠️ Ошибка при сбросе: {e}")

def send_album_to_owners(media_group_id):
    """Отправляет собранный альбом всем владельцам"""
    if media_group_id not in photo_groups:
        return
    
    group_data = photo_groups[media_group_id]
    
    # Если уже обработали - выходим
    if group_data['processed']:
        return
    
    file_ids = group_data['files']
    caption = group_data['caption']
    
    print(f"📦 Отправка альбома {media_group_id}: {len(file_ids)} фото, подпись: '{caption}'")
    
    for owner_id in OWNER_IDS:
        try:
            # Создаем медиа-группу
            media = []
            
            # Первое фото с подписью
            media.append(telebot.types.InputMediaPhoto(file_ids[0], caption=caption if caption else None))
            
            # Остальные фото без подписи
            for file_id in file_ids[1:]:
                media.append(telebot.types.InputMediaPhoto(file_id))
            
            # Отправляем альбом
            bot.send_media_group(owner_id, media)
            print(f"✅ Альбом отправлен владельцу {owner_id}")
            
        except Exception as e:
            print(f"❌ Ошибка отправки альбома владельцу {owner_id}: {e}")
    
    # Помечаем как обработанный
    group_data['processed'] = True

# Обработчик для фото
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        # Получаем данные
        file_id = message.photo[-1].file_id
        media_group_id = message.media_group_id
        caption = message.caption if message.caption else ""
        
        print(f"📸 Получено фото, group_id: {media_group_id}")
        
        # Если это одиночное фото
        if not media_group_id:
            print("🖼️ Одиночное фото")
            for owner_id in OWNER_IDS:
                try:
                    if caption:
                        bot.send_photo(owner_id, file_id, caption=caption)
                    else:
                        bot.send_photo(owner_id, file_id)
                except Exception as e:
                    print(f"❌ Ошибка: {e}")
            bot.reply_to(message, "✅")
            return
        
        # Если это альбом
        if media_group_id not in photo_groups:
            photo_groups[media_group_id] = {
                'files': [],
                'caption': caption,
                'processed': False
            }
            print(f"🆕 Создан альбом {media_group_id} с подписью: '{caption}'")
        
        # Добавляем фото, если его ещё нет
        if file_id not in photo_groups[media_group_id]['files']:
            photo_groups[media_group_id]['files'].append(file_id)
            print(f"➕ Добавлено фото в альбом {media_group_id}, всего: {len(photo_groups[media_group_id]['files'])}")
        
        # Отменяем старый таймер
        if media_group_id in group_timers:
            try:
                group_timers[media_group_id].cancel()
            except:
                pass
        
        # Ставим новый таймер на 1.5 секунды (ждём все фото)
        timer = threading.Timer(1.5, send_album_to_owners, args=[media_group_id])
        timer.daemon = True
        timer.start()
        group_timers[media_group_id] = timer
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

# Обработчик для текста
@bot.message_handler(func=lambda message: message.text and not message.text.startswith('/'))
def handle_text(message):
    try:
        text = message.text
        print(f"💬 Получен текст: '{text[:50]}...'")
        
        # Отправляем текст всем владельцам
        for owner_id in OWNER_IDS:
            try:
                bot.send_message(owner_id, text)
                print(f"✅ Текст отправлен владельцу {owner_id}")
            except Exception as e:
                print(f"❌ Ошибка: {e}")
        
        bot.reply_to(message, "✅")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

@app.route('/')
def home():
    return "Бот работает! 🤖 (фото+текст)"

@app.route('/health')
def health():
    return "OK", 200

def start_bot():
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
