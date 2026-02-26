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
photo_groups = {}  # media_group_id -> {'files': [], 'caption': '', 'timer': None, 'chat_id': None, 'message_id': None}
group_locks = {}   # для синхронизации

polling_started = False

print("🔄 Сброс подключений...")
try:
    bot.remove_webhook()
    time.sleep(1)
    bot_info = bot.get_me()
    print(f"✅ Бот @{bot_info.username} инициализирован")
except Exception as e:
    print(f"⚠️ Ошибка при сбросе: {e}")

def send_album(media_group_id):
    """Отправляет альбом всем владельцам и отвечает пользователю"""
    try:
        if media_group_id not in photo_groups:
            return
        
        group_data = photo_groups[media_group_id]
        files = group_data['files']
        caption = group_data['caption']
        chat_id = group_data['chat_id']
        message_id = group_data['message_id']
        
        # Если нет фото - выходим
        if not files:
            return
        
        print(f"\n📦 ОТПРАВКА АЛЬБОМА {media_group_id}")
        print(f"   Фото: {len(files)} шт")
        print(f"   Текст: '{caption}'")
        print(f"   Chat ID: {chat_id}")
        
        # Отправляем каждому владельцу
        for owner_id in OWNER_IDS:
            try:
                # Создаем медиа-группу
                media = []
                
                # Первое фото с текстом (если он есть)
                if caption:
                    media.append(telebot.types.InputMediaPhoto(files[0], caption=caption))
                else:
                    media.append(telebot.types.InputMediaPhoto(files[0]))
                
                # Остальные фото без текста
                for file_id in files[1:]:
                    media.append(telebot.types.InputMediaPhoto(file_id))
                
                # Отправляем одним сообщением
                bot.send_media_group(owner_id, media)
                print(f"   ✅ Альбом отправлен владельцу {owner_id}")
                
            except Exception as e:
                print(f"   ❌ Ошибка владельцу {owner_id}: {e}")
                
                # Если альбом не отправился - отправляем по одному
                try:
                    for i, file_id in enumerate(files):
                        if i == 0 and caption:
                            bot.send_photo(owner_id, file_id, caption=caption)
                        else:
                            bot.send_photo(owner_id, file_id)
                except:
                    pass
        
        # ОТВЕЧАЕМ ПОЛЬЗОВАТЕЛЮ ГАЛОЧКОЙ
        try:
            bot.send_message(chat_id, "✅", reply_to_message_id=message_id)
            print(f"   ✅ Ответ пользователю отправлен")
        except Exception as e:
            print(f"   ❌ Ошибка при ответе пользователю: {e}")
        
        # Удаляем данные
        if media_group_id in photo_groups:
            del photo_groups[media_group_id]
        if media_group_id in group_locks:
            del group_locks[media_group_id]
            
    except Exception as e:
        print(f"❌ Ошибка в send_album: {e}")
        import traceback
        traceback.print_exc()

# Обработчик для фото
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        # Получаем данные
        file_id = message.photo[-1].file_id
        media_group_id = message.media_group_id
        caption = message.caption if message.caption else ""
        chat_id = message.chat.id
        message_id = message.message_id
        
        print(f"\n📸 ПОЛУЧЕНО ФОТО")
        print(f"   Group ID: {media_group_id}")
        print(f"   Текст: '{caption}'")
        print(f"   Chat ID: {chat_id}")
        print(f"   Message ID: {message_id}")
        
        # Если это одиночное фото
        if not media_group_id:
            print("   🖼️ Одиночное фото")
            
            for owner_id in OWNER_IDS:
                try:
                    if caption:
                        bot.send_photo(owner_id, file_id, caption=caption)
                        print(f"   ✅ Фото с текстом отправлено {owner_id}")
                    else:
                        bot.send_photo(owner_id, file_id)
                        print(f"   ✅ Фото отправлено {owner_id}")
                except Exception as e:
                    print(f"   ❌ Ошибка: {e}")
            
            # ОТВЕЧАЕМ ПОЛЬЗОВАТЕЛЮ ГАЛОЧКОЙ
            try:
                bot.reply_to(message, "✅")
                print(f"   ✅ Ответ пользователю отправлен")
            except Exception as e:
                print(f"   ❌ Ошибка при ответе: {e}")
                
            return
        
        # ЕСЛИ ЭТО АЛЬБОМ (несколько фото)
        
        # Создаем запись для новой группы
        if media_group_id not in photo_groups:
            photo_groups[media_group_id] = {
                'files': [],
                'caption': caption,
                'timer': None,
                'chat_id': chat_id,
                'message_id': message_id
            }
            print(f"   🆕 Новая группа {media_group_id}")
        
        # Добавляем фото
        group = photo_groups[media_group_id]
        if file_id not in group['files']:
            group['files'].append(file_id)
            print(f"   ➕ Добавлено фото {len(group['files'])}")
        
        # Сохраняем текст (берём из первого фото)
        if caption and not group['caption']:
            group['caption'] = caption
            print(f"   📝 Сохранён текст: '{caption}'")
        
        # Отменяем старый таймер
        if group['timer']:
            try:
                group['timer'].cancel()
            except:
                pass
        
        # Создаём новый таймер на 2 секунды
        timer = threading.Timer(2.0, send_album, args=[media_group_id])
        timer.daemon = True
        timer.start()
        group['timer'] = timer
        print(f"   ⏰ Таймер установлен на 2 сек")
        
    except Exception as e:
        print(f"❌ Ошибка в handle_photo: {e}")
        import traceback
        traceback.print_exc()
        # Пытаемся ответить даже при ошибке
        try:
            bot.reply_to(message, "❌")
        except:
            pass

# Обработчик для текста
@bot.message_handler(func=lambda message: message.text and not message.text.startswith('/'))
def handle_text(message):
    try:
        text = message.text
        print(f"\n💬 ПОЛУЧЕН ТЕКСТ: '{text}'")
        
        for owner_id in OWNER_IDS:
            try:
                bot.send_message(owner_id, text)
                print(f"   ✅ Текст отправлен {owner_id}")
            except Exception as e:
                print(f"   ❌ Ошибка: {e}")
        
        # ОТВЕЧАЕМ ПОЛЬЗОВАТЕЛЮ ГАЛОЧКОЙ
        try:
            bot.reply_to(message, "✅")
            print(f"   ✅ Ответ пользователю отправлен")
        except Exception as e:
            print(f"   ❌ Ошибка при ответе: {e}")
        
    except Exception as e:
        print(f"❌ Ошибка в handle_text: {e}")
        try:
            bot.reply_to(message, "❌")
        except:
            pass

@app.route('/')
def home():
    return "Бот работает! 🤖 (с галочками)"

@app.route('/health')
def health():
    return "OK", 200

def start_bot():
    global polling_started
    if polling_started:
        return
    
    polling_started = True
    print("🚀 ЗАПУСК БОТА...")
    print(f"📋 Владельцы: {OWNER_IDS}")
    
    while True:
        try:
            bot.remove_webhook()
            time.sleep(1)
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"❌ Ошибка polling: {e}")
            time.sleep(5)

if __name__ == '__main__':
    if not polling_started:
        bot_thread = threading.Thread(target=start_bot, daemon=True)
        bot_thread.start()
        time.sleep(2)
    
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
