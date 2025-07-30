import os
import time
import threading
from flask import Flask, request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GRUPO_ID = os.getenv("ID_DO_GRUPO")
URL_WEBHOOK = os.getenv("URL_RENDERIZACAO")

bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)

HORARIOS = ["08:00", "12:00", "16:00", "20:00"]

def iniciar_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def calcular_confianca(odd):
    try:
        return round((1 / float(odd)) * 100, 2)
    except:
        return 0.0

def gerar_bilhete():
    driver = iniciar_driver()
    driver.get("https://www.betano.com/sport/futebol/brasil/serie-a/10014/")
    time.sleep(5)

    bilhete = "⚽ PALPITES INTELIGENTES - Betano Hoje\n\n"
    jogos = driver.find_elements(By.CSS_SELECTOR, ".__event__title")[:4]
    odds = driver.find_elements(By.CSS_SELECTOR, ".__markets .option-item")

    if not jogos or not odds:
        driver.quit()
        return "Nenhum jogo encontrado. Tente mais tarde."

    for idx, jogo in enumerate(jogos):
        try:
            nome = jogo.text
            odd = odds[idx].text.split("\n")[-1]
            conf = calcular_confianca(odd)
            bilhete += f"{idx+1}️⃣ {nome} - Odd: {odd} - Confiança: {conf}%\n"
        except:
            continue

    driver.quit()
    bilhete += "\n📊 Dados reais da Betano\n🔴 Bot 100% automatizado\n"
    return bilhete

def enviar_bilhete():
    bilhete = gerar_bilhete()
    bot.send_message(chat_id=GRUPO_ID, text=bilhete)

def agendador():
    while True:
        agora = time.strftime("%H:%M")
        if agora in HORARIOS:
            enviar_bilhete()
            time.sleep(60)
        time.sleep(20)

@app.route("/")
def home():
    return "Bot Betano Inteligente ON"

@app.route("/webhook", methods=["POST"])
def webhook():
    return {"status": "ok"}

if __name__ == "__main__":
    threading.Thread(target=agendador).start()
    app.run(host="0.0.0.0", port=10000)
