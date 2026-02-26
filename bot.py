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

# Словарь для хранения временных групп фото
photo_groups = {}
group_timers = {}

# Обработчик для фото
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        print("=" * 50)
        print("📸 ПОЛУЧЕНО ФОТО")
        
        # Получаем данные фото
        file_id = message.photo[-1].file_id
        caption = message.caption if message.caption else ""
        media_group_id = message.media_group_id
        
        print(f"Подпись к фото: '{caption}'")
        
        # Если это одиночное фото
        if not media_group_id:
            print("🖼️ Одиночное фото")
            
            # Отправляем всем владельцам ТОЛЬКО подпись пользователя
            for owner_id in OWNER_IDS:
                try:
                    if caption:
                        # Если есть подпись - отправляем фото с подписью
                        bot.send_photo(owner_id, file_id, caption=caption)
                        print(f"✅ Фото с подписью отправлено владельцу {owner_id}")
                    else:
                        # Если нет подписи - только фото
                        bot.send_photo(owner_id, file_id)
                        print(f"✅ Фото без подписи отправлено владельцу {owner_id}")
                except Exception as e:
                    print(f"❌ Ошибка владельцу {owner_id}: {e}")
            
            # Отвечаем пользователю
            bot.reply_to(message, "✅ Фото получено!")
            
        # Если это альбом (несколько фото)
        else:
            print(f"📚 Фото из альбома {media_group_id}")
            
            # Группируем фото
            if media_group_id not in photo_groups:
                photo_groups[media_group_id] = []
                print(f"🆕 Создан новый альбом {media_group_id}")
            
            if file_id not in photo_groups[media_group_id]:
                photo_groups[media_group_id].append(file_id)
                print(f"➕ Добавлено фото в альбом {media_group_id}, всего: {len(photo_groups[media_group_id])}")
            
            # Отменяем старый таймер
            if media_group_id in group_timers:
                try:
                    group_timers[media_group_id].cancel()
                except:
                    pass
            
            # Ставим новый таймер на 1 секунду
            timer = threading.Timer(1.0, process_album, args=[media_group_id, caption])
            timer.daemon = True
            timer.start()
            group_timers[media_group_id] = timer
            
    except Exception as e:
        print(f"❌ Ошибка обработки фото: {e}")
        import traceback
        traceback.print_exc()

def process_album(media_group_id, caption):
    """Отправляет собранный альбом фото"""
    try:
        print(f"⏰ Отправка альбома {media_group_id}")
        
        if media_group_id not in photo_groups:
            return
        
        file_ids = photo_groups[media_group_id]
        print(f"📦 Альбом содержит {len(file_ids)} фото, подпись: '{caption}'")
        
        # Отправляем каждому владельцу
        for owner_id in OWNER_IDS:
            try:
                # Создаем медиа-группу
                media = []
                
                # Первое фото с подписью (если есть)
                if caption:
                    media.append(telebot.types.InputMediaPhoto(file_ids[0], caption=caption))
                else:
                    media.append(telebot.types.InputMediaPhoto(file_ids[0]))
                
                # Остальные фото без подписи
                for file_id in file_ids[1:]:
                    media.append(telebot.types.InputMediaPhoto(file_id))
                
                # Отправляем одним сообщением
                bot.send_media_group(owner_id, media)
                print(f"✅ Альбом отправлен владельцу {owner_id}")
                
            except Exception as e:
                print(f"❌ Ошибка отправки альбома владельцу {owner_id}: {e}")
                
                # Если не получилось отправить группой - отправляем по одному
                for i, file_id in enumerate(file_ids):
                    try:
                        if i == 0 and caption:
                            bot.send_photo(owner_id, file_id, caption=caption)
                        else:
                            bot.send_photo(owner_id, file_id)
                    except:
                        pass
        
        # Очищаем данные
        del photo_groups[media_group_id]
        if media_group_id in group_timers:
            del group_timers[media_group_id]
            
    except Exception as e:
        print(f"❌ Ошибка в process_album: {e}")

# Обработчик для текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    try:
        # Игнорируем команды
        if message.text and message.text.startswith('/'):
            return
        
        text = message.text if message.text else ""
        print(f"💬 Текст: {text[:50]}...")
        
        # Отправляем текст всем владельцам
        for owner_id in OWNER_IDS:
            try:
                bot.send_message(owner_id, text)
                print(f"✅ Текст отправлен владельцу {owner_id}")
            except Exception as e:
                print(f"❌ Ошибка отправки текста: {e}")
        
        bot.reply_to(message, "✅")
        
    except Exception as e:
        print(f"❌ Ошибка обработки текста: {e}")

@app.route('/')
def home():
    return "Бот работает! 🤖 (без username)"

@app.route('/health')
def health():
    return "OK", 200

def start_bot():
    global polling_started
    if polling_started:
        return
    
    polling_started = True
    print("🚀 Запуск бота...")
    print(f"📋 Отправлять владельцам: {OWNER_IDS}")
    print("✅ Username НЕ добавляются к фото")
    
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
