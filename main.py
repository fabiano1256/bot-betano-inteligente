import os
import time
import random
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

# Horários de postagem (você pode ajustar)
HORARIOS = ["08:00", "12:00", "16:00", "20:00"]

# Inicializa navegador headless para scraping
def iniciar_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

# Calcula a % de confiança com base na odd (fórmula simples)
def calcular_confianca(odd):
    try:
        return round((1 / float(odd)) * 100, 2)
    except:
        return 0.0

# Função que extrai palpites da Betano (exemplo simples)
def gerar_bilhete():
    driver = iniciar_driver()
    driver.get("https://www.betano.com/sport/futebol/brasil/serie-a/10014/")
    time.sleep(5)

    bilhete = "\u26bd PALPITES INTELIGENTES - Betano Hoje\n\n"

    jogos = driver.find_elements(By.CSS_SELECTOR, ".__event__title")[:4]
    odds = driver.find_elements(By.CSS_SELECTOR, ".__markets .option-item")

    if not jogos or not odds:
        driver.quit()
        return "Nenhum jogo encontrado. Tente mais tarde."

    count = 0
    for jogo in jogos:
        try:
            nome = jogo.text
            odd = odds[count].text.split("\n")[-1]
            conf = calcular_confianca(odd)
            bilhete += f"{count+1}\ufe0f\u20e3 {nome} - Odd: {odd} - Confian\u00e7a: {conf}%\n"
            count += 1
        except:
            continue

    driver.quit()
    bilhete += "\n\ud83d\udcca Dados reais da Betano\n\ud83d\udd34 Bot 100% automatizado\n"
    return bilhete

# Envia bilhete
def enviar_bilhete():
    bilhete = gerar_bilhete()
    bot.send_message(chat_id=GRUPO_ID, text=bilhete)

# Agenda automática com base no horário
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
    data = request.get_json()
    return {"status": "ok"}

if __name__ == "__main__":
    threading.Thread(target=agendador).start()
    app.run(host="0.0.0.0", port=10000)
