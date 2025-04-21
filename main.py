from flask import Flask
from threading import Thread
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta

# === CONFIGURATION TELEGRAM ===
TOKEN = "7737434764:AAHHSIa36lp3ysRqyrQheA4E3DdnChrT0T8"
CHAT_ID = "5355749395"

# === MOTS-CLES A FILTRER ===
KEYWORDS = [
    "junior", "front-end", "développeur", "web", "react", "javascript", "html",
    "css", "typescript", "sass", "bootstrap", "tailwind", "responsive",
    "mobile", "react native", "progressive web app", "integrateur",
    "intégration", "intégrateur web"
]

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Erreur Telegram : {e}")

def is_recent(date_string):
    try:
        jours = ["1", "2", "3", "4", "5"]
        return any(f"{j} jour" in date_string.lower() or f"{j}j" in date_string.lower() for j in jours)
    except:
        return False

# === SCRAPING INDEED ===
def scrape_indeed():
    url = "https://fr.indeed.com/jobs?q=d%C3%A9veloppeur+web+front-end+alternance&sort=date"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        jobs = soup.find_all("a", class_="tapItem")

        for job in jobs:
            title = job.find("h2").text.strip()
            date = job.find("span", class_="date").text.strip()
            if is_recent(date):
                link = "https://fr.indeed.com" + job.get("href")
                send_telegram_message(f"<b>{title}</b>\n{link}")
    except Exception as e:
        send_telegram_message(f"Erreur scraping Indeed : {e}")

# === KEEP ALIVE POUR RENDER ===
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot actif."

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# === LANCEMENT DU BOT ===
keep_alive()

# === LOOP INFINIE SCRAPE PENDANT 2 MINUTES TOUTES LES 30 MINUTES ===
while True:
    send_telegram_message("🟢 Le bot commence à scraper les annonces...")
    start_time = time.time()
    while time.time() - start_time < 120:  # 2 minutes
        scrape_indeed()
        time.sleep(5)
    send_telegram_message("🟡 Le bot est en pause pendant 30 minutes.")
    time.sleep(1800)  # 30 minutes
