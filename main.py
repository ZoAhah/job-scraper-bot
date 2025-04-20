from flask import Flask
from threading import Thread
import requests
from bs4 import BeautifulSoup
import time
import os

# === CONFIGURATION TELEGRAM ===
TOKEN = "7737434764:AAHHSIa36lp3ysRqyrQheA4E3DdnChrT0T8"
CHAT_ID = "5355749395"

# === MOTS-CLÉS A FILTRER ===
KEYWORDS = [
    "junior", "front-end", "développeur", "web", "react", "javascript", "html",
    "css", "typescript", "sass", "bootstrap", "tailwind", "responsive",
    "mobile", "react native", "progressive web app", "intégrateur", "alternance"
]

# === ENVOI DES MESSAGES TELEGRAM ===
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Erreur Telegram : {e}")

# === SCRAPING INDEED (exemple de base) ===
def scrape_indeed():
    print("Scraping Indeed...")
    url = "https://fr.indeed.com/emplois?q=d%C3%A9veloppeur+web+alternance&l=&fromage=1"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        jobs = soup.find_all("a", class_="tapItem")

        for job in jobs[:10]:
            title = job.find("h2").text.strip()
            link = "https://fr.indeed.com" + job.get("href")
            if any(keyword in title.lower() for keyword in KEYWORDS):
                send_telegram_message(f"<b>{title}</b>\n{link}")
    except Exception as e:
        send_telegram_message(f"Erreur scraping Indeed : {e}")

# === FLASK POUR UPTIME ET RENDER ===
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot actif."

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# === LANCEMENT DU BOT ===
keep_alive()

def start_scraping_loop():
    while True:
        send_telegram_message("🚀 Le bot commence à scraper les sites !")
        print("Scraping...")
        start_time = time.time()
        while time.time() - start_time < 120:  # 2 minutes
            scrape_indeed()
            time.sleep(15)  # Pause courte entre les appels
        send_telegram_message("⏸️ Le bot est en pause pour 30 minutes.")
        print("Pause de 30 minutes...")
        time.sleep(1800)  # 30 minutes

start_scraping_loop()
