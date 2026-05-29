import os
import re
import urllib.parse
import requests
import telebot
from flask import Flask

# Sizning Telegram Bot Tokeningiz
TELEGRAM_TOKEN = '8942058498:AAFzwPZobu8Vpx1pi3Va766uZCyWjNbGlSs'
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Render serveri uxlab qolmasligi uchun Flask veb-server qo'shamiz
app = Flask(__name__)

@app.route('/')
def home():
    return "Kino qidiruv boti muvaffaqiyatli ishlamoqda!"

def search_youtube_via_duck(query):
    try:
        # YouTube qidiruv so'rovini DuckDuckGo orqali yuboramiz
        search_query = f"{query} site:youtube.com"
        encoded_query = urllib.parse.quote(search_query)
        url = f"https://duckduckgo.com{encoded_query}"
        
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=15)
        
        # HTML matn ichidan YouTube video ID-larini qidirib topish
        video_ids = re.findall(r"v=([a-zA-Z0-9_-]{11})", response.text)
        
        videos = []
        if video_ids:
            # Bir xil bo'lmagan dastlabki 3 ta videoni saralab olamiz
            unique_ids = list(dict.fromkeys(video_ids))[:3]
            for v_id in unique_ids:
                video_url = f"https://youtube.com{v_id}"
                videos.append(f"🎬 **Siz qidirgan video topildi:**\n🔗 {video_url}")
        return videos
    except Exception as e:
        print(f"Qidiruvda xatolik yuz berdi: {e}")
        return []

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "👋 **Assalomu alaykum! Men YouTube kino qidiruv botiman.**\n\n"
        "Menga istalgan kino, serial yoki video nomini yozing. "
        "Men uni YouTube'dan topib, sizga havola (link) ko'rinishida yuboraman! 🍿"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    query = message.text
    waiting_msg = bot.send_message(message.chat.id, "🔍 *YouTube tizimidan qidirilmoqda, iltimos kuting...*", parse_mode='Markdown')
    
    results = search_youtube_via_duck(query)
    
    # "Kutilmoqda" degan xabarni o'chirib tashlash
    try:
        bot.delete_message(message.chat.id, waiting_msg.message_id)
    except:
        pass
        
    if results:
        for video in results:
            bot.send_message(message.chat.id, video, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, "❌ Kechirasiz, hech narsa topilmadi. Qidiruv so'zini aniqroq yozib ko'ring.")

if __name__ == '__main__':
    import threading
    # Veb-serverni alohida oqimda (thread) ishga tushiramiz
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))).start()
    print("🚀 Bot muvaffaqiyatli ishga tushdi...")
    bot.infinity_polling()
