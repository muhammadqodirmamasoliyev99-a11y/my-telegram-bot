import os
import requests
import telebot
from flask import Flask

# Kalitlar
TELEGRAM_TOKEN = '8942058498:AAFzwPZobu8Vpx1pi3Va766uZCyWjNbGlSs'
YOUTUBE_API_KEY = 'AIzaSyBluXZ_eGGpnDdySO42tcvI9FhMaCRYqwE'

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "YouTube Rasmiy API Boti ishlamoqda!"

def search_youtube(query):
    url = "https://googleapis.com"
    params = {
        'part': 'snippet',
        'q': query,
        'key': YOUTUBE_API_KEY,
        'maxResults': 3,
        'type': 'video'
    }
    try:
        response = requests.get(url, params=params, timeout=10).json()
        videos = []
        
        if 'items' in response:
            for item in response['items']:
                video_id = item['id']['videoId']
                title = item['snippet']['title']
                video_url = f"https://youtube.com{video_id}"
                videos.append(f"🎬 **{title}**\n🔗 {video_url}")
        return videos
    except Exception as e:
        print(f"YouTube API xatoligi: {e}")
        return []

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Salom! Menga kino nomini yozing, YouTube rasmiy tizimidan topib beraman! 🍿")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    query = message.text
    waiting_msg = bot.send_message(message.chat.id, "🔍 *YouTube rasmiy bazasidan qidirilmoqda...*", parse_mode='Markdown')
    
    results = search_youtube(query)
    
    try:
        bot.delete_message(message.chat.id, waiting_msg.message_id)
    except:
        pass
        
    if results:
        for video in results:
            bot.send_message(message.chat.id, video, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, "❌ Kechirasiz, hech narsa topilmadi. Google Cloud Console'da YouTube API v3 yoqilganini tekshiring.")

if __name__ == '__main__':
    import threading
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))).start()
    bot.infinity_polling()
