import requests
from bs4 import BeautifulSoup
import time
from flask import Flask
from threading import Thread
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

# === ENVOI DES MESSAGES TELEGRAM ===
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Erreur Telegram : {e}")

# === SCRAPING INDEED AVEC FILTRE DE DATE ===
def scrape_indeed():
    print("Scraping Indeed...")
    url = "https://fr.indeed.com/jobs?q=d%C3%A9veloppeur+web+front-end+alternance&sort=date"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        jobs = soup.find_all("a", class_="tapItem")

        for job in jobs[:10]:  # Vérifie les 10 premières offres
            title = job.find("h2").text.strip()
            date_tag = job.find("span", class_="date")
            if date_tag:
                date_text = date_tag.text.strip().lower()

                # On filtre sur les 5 derniers jours
                if any(jour in date_text for jour in ["aujourd'hui", "1", "2", "3", "4", "5"]):
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

# === LOOP INFINIE AVEC PAUSE DE 30 MIN ===
while True:
    print("Début du scraping...")
    send_telegram_message("🚀 Le bot commence une nouvelle session de recherche.")
    scrape_indeed()
    print("Pause de 30 minutes...")
    send_telegram_message("⏸️ Pause de 30 minutes avant la prochaine vérification.")
    time.sleep(1800)  # 1800 secondes = 30 minutes
