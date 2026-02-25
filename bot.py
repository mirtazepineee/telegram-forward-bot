import os
import requests
import time
import threading
from flask import Flask

app = Flask(__name__)

# Конфигурация
BOT_TOKEN = "8711050834:AAEWbit5d3Y5V9gtycADVFItze71_-3_PHk"
OWNER_IDS = [756835347, 7768651103, 1877513295]
last_update_id = 0

def send_message(chat_id, text):
    """Отправка сообщения через Telegram API"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text})
    except:
        pass

def handle_update(update):
    """Обработка одного обновления"""
    global last_update_id
    
    if "message" not in update:
        return
    
    msg = update["message"]
    chat_id = msg["chat"]["id"]
    text = msg.get("text", "")
    
    # Информация об отправителе
    user = msg.get("from", {})
    username = user.get("username")
    user_id = user.get("id")
    user_display = f"@{username}" if username else f"ID: {user_id}"
    
    # Пересылаем владельцам
    for owner_id in OWNER_IDS:
        send_message(owner_id, f"{text}\n{user_display}")
    
    # Отвечаем пользователю
    send_message(chat_id, "✅")

def polling_worker():
    """Фоновая задача для получения обновлений"""
    global last_update_id
    
    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
            params = {
                "offset": last_update_id + 1,
                "timeout": 30
            }
            
            response = requests.get(url, params=params, timeout=35)
            data = response.json()
            
            if data.get("ok"):
                for update in data.get("result", []):
                    if update["update_id"] > last_update_id:
                        last_update_id = update["update_id"]
                        handle_update(update)
                        
        except Exception as e:
            print(f"Polling error: {e}")
            time.sleep(3)

@app.route('/')
def home():
    return "Бот работает! 🚀"

@app.route('/health')
def health():
    return "OK", 200

if __name__ == '__main__':
    # Запускаем polling в отдельном потоке
    thread = threading.Thread(target=polling_worker, daemon=True)
    thread.start()
    
    # Запускаем веб-сервер
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
