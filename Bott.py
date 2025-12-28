import telebot
from telebot import types
import requests
import random
import time
import threading
from collections import Counter
import os

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN, parse_mode='HTML')

API_URL_HISTORY = 'https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json'
API_URL_ISSUE = 'https://api.bdg88zf.com/api/webapi/GetGameIssue'

HEADERS = {
    'Content-Type': 'application/json;charset=UTF-8',
    'Accept': 'application/json, text/plain, */*',
    'User-Agent': 'Mozilla/5.0'
}

# ================= CORE =================
def categorize_number(number):
    return 'Small 🔵' if 0 <= number <= 4 else 'Big 🟠'

def get_latest_data():
    try:
        r = requests.get(API_URL_HISTORY, headers=HEADERS, timeout=5)
        return r.json()['data']['list']
    except:
        return []

def get_game_issue():
    try:
        data = {"typeId": 1, "language": 0}
        r = requests.post(API_URL_ISSUE, headers=HEADERS, json=data, timeout=5)
        return r.json()['data']['issueNumber']
    except:
        return None

# ================= AI ENGINE =================
class V13SmartAnalysis:
    def __init__(self, history):
        self.history = history
        self.numbers = [int(x['number']) for x in history]
        self.cats = [categorize_number(n) for n in self.numbers]

    def get_prediction(self):
        s = self.cats[:10].count('Small 🔵')
        b = self.cats[:10].count('Big 🟠')

        pred = 'Small 🔵' if s >= b else 'Big 🟠'
        pool = [0,1,2,3,4] if pred == 'Small 🔵' else [5,6,7,8,9]

        counts = Counter([n for n in self.numbers[:20] if n in pool])
        n1 = counts.most_common(1)[0][0] if counts else random.choice(pool)
        n2 = random.choice([x for x in pool if x != n1])

        return pred, n1, n2, random.randint(55, 90)

# ================= BOT =================
@bot.message_handler(commands=['start'])
def start(m):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🚀 PREDICT NOW")
    bot.reply_to(m, "🚀 V13 AI BOT READY", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text == "🚀 PREDICT NOW")
def predict(m):
    h = get_latest_data()
    if not h:
        bot.send_message(m.chat.id, "API ERROR")
        return

    issue = get_game_issue()
    engine = V13SmartAnalysis(h)
    pred, n1, n2, conf = engine.get_prediction()

    bot.send_message(
        m.chat.id,
        f"<b>Period:</b> {issue}\n<b>Signal:</b> {pred}\n<b>Numbers:</b> {n1},{n2}\n<b>Conf:</b> {conf}%"
    )

# ================= START =================
print("🚀 BOT STARTED")
bot.infinity_polling()
