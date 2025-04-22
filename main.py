from flask import Flask
from threading import Thread
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# === CONFIGURATION TELEGRAM ===
TOKEN = "7737434764:AAHHSIa36lp3ysRqyrQheA4E3DdnChrT0T8"
CHAT_ID = "5355749395"

# === MOTS-CLÉS À FILTRER ===
KEYWORDS = [
    "junior", "front-end", "développeur", "web", "react", "javascript", "html",
    "css", "typescript", "sass", "bootstrap", "tailwind", "responsive",
    "mobile", "react native", "progressive web app", "integrateur",
    "intégration", "intégrateur web"
]

# === ENVOI DE MESSAGE TELEGRAM ===
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Erreur Telegram : {e}")

# === FILTRER PAR DATE (5 JOURS) ===
def is_recent(posted_date_text):
    jours = re.findall(r"\d+", posted_date_text)
    if "aujourd" in posted_date_text.lower() or "1 jour" in posted_date_text:
        return True
    if jours and int(jours[0]) <= 5:
        return True
    return False

# === SCRAPING INDEED AVEC SELENIUM ===
def scrape_indeed():
    print("Scraping Indeed avec Selenium...")

    urls = [
        "https://fr.indeed.com/jobs?q=d%C3%A9veloppeur+web+front-end+alternance&sort=date",
        "https://fr.indeed.com/jobs?q=integrateur+web+alternance&sort=date"
    ]

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    for url in urls:
        try:
            driver.get(url)
            time.sleep(2)
            jobs = driver.find_elements(By.CLASS_NAME, "tapItem")
            count = 0

            for job in jobs[:10]:
                try:
                    title = job.find_element(By.TAG_NAME, "h2").text.strip()
                    link = job.get_attribute("href")
                    date_elem = job.find_element(By.CLASS_NAME, "date").text.strip()
                    if is_recent(date_elem):
                        send_telegram_message(f"<b>{title}</b>\n{link}")
                        count += 1
                except Exception as e:
                    continue

            print(f"Indeed : {count} annonces envoyées pour {url}")
        except Exception as e:
            send_telegram_message(f"Erreur Indeed : {e}")

    driver.quit()

# === SCRAPING WTTJ ===
def scrape_wttj():
    print("Scraping Welcome to the Jungle...")
    urls = [
        "https://www.welcometothejungle.com/fr/jobs?query=développeur%20web%20front-end%20alternance",
        "https://www.welcometothejungle.com/fr/jobs?query=integrateur%20web%20alternance"
    ]
    headers = {"User-Agent": "Mozilla/5.0"}

    for url in urls:
        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
            offers = soup.find_all("div", class_="ais-Hits-item")

            for offer in offers[:10]:
                title = offer.find("span", class_="sc-8c27c2a1-0").text.strip()
                link = "https://www.welcometothejungle.com" + offer.find("a").get("href")
                send_telegram_message(f"<b>{title}</b>\n{link}")

        except Exception as e:
            send_telegram_message(f"Erreur WTTJ : {e}")

# === SCRAPING MONSTER ===
def scrape_monster():
    print("Scraping Monster...")
    urls = [
        "https://www.monster.fr/emploi/recherche/?q=developpeur-web-front-end-alternance",
        "https://www.monster.fr/emploi/recherche/?q=integrateur-web-alternance"
    ]
    headers = {"User-Agent": "Mozilla/5.0"}

    for url in urls:
        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
            offers = soup.find_all("section", class_="card-content")

            for offer in offers[:10]:
                title_elem = offer.find("h2")
                if title_elem:
                    title = title_elem.text.strip()
                    link = title_elem.find("a").get("href")
                    send_telegram_message(f"<b>{title}</b>\n{link}")

        except Exception as e:
            send_telegram_message(f"Erreur Monster : {e}")

# === SCRAPING HELLOWORK ===
def scrape_hellowork():
    print("Scraping HelloWork...")
    urls = [
        "https://www.hellowork.com/fr-fr/emploi/recherche.html?k=developpeur+web+front-end+alternance",
        "https://www.hellowork.com/fr-fr/emploi/recherche.html?k=integrateur+web+alternance"
    ]
    headers = {"User-Agent": "Mozilla/5.0"}

    for url in urls:
        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
            offers = soup.find_all("div", class_="job-title")

            for offer in offers[:10]:
                a_tag = offer.find("a")
                if a_tag:
                    title = a_tag.text.strip()
                    link = a_tag.get("href")
                    send_telegram_message(f"<b>{title}</b>\n{link}")

        except Exception as e:
            send_telegram_message(f"Erreur HelloWork : {e}")

# === FLASK KEEP-ALIVE POUR RENDER ===
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot actif sur Render."

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# === LANCEMENT DU BOT ===
keep_alive()

while True:
    send_telegram_message("🔍 Le bot commence une nouvelle recherche d'offres.")
    scrape_indeed()
    scrape_wttj()
    scrape_monster()
    scrape_hellowork()
    send_telegram_message("⏸️ Pause de 30 minutes.")
    time.sleep(1800)
