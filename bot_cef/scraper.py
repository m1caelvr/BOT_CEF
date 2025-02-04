import os
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

if os.getenv("GITHUB_ACTIONS") is None:
    load_dotenv()

LOGIN = os.getenv("LOGIN")
SENHA = os.getenv("SENHA")


def run_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def acess_page(driver, url):
    driver.get(url)
    time.sleep(2)


def fill_login_form(driver):
    login_input = driver.find_element(By.ID, "login")
    senha_input = driver.find_element(By.ID, "senha")

    login_input.send_keys(LOGIN)
    senha_input.send_keys(SENHA)
    senha_input.send_keys(Keys.RETURN)
    time.sleep(3)


def extrair_dados(driver):
    time.sleep(3)

    # 🔹 Simulando a extração de dados fictícios
    dados = [
        {
            "Prazo": "2025-02-10",
            "Unidade": "Filial RJ",
            "Valor": 1500,
            "Status": "Aprovado",
        },
        {
            "Prazo": "2025-02-15",
            "Unidade": "Filial SP",
            "Valor": 2300,
            "Status": "Pendente",
        },
        {
            "Prazo": "2025-02-20",
            "Unidade": "Filial MG",
            "Valor": 1750,
            "Status": "Rejeitado",
        },
    ]

    df = pd.DataFrame(dados)

    path = os.path.join(os.getcwd(), "data", "dados.csv")
    df.to_csv(path, index=False)
    print(f"📂 Dados extraídos e salvos em '{path}'")


def run_bot():
    print("🔹 Iniciando BOT_CEF...")
    driver = run_driver()
    try:
        acess_page(driver, "https://eqs.arenanet.com.br/")
        fill_login_form(driver)
        extrair_dados(driver)
    finally:
        driver.quit()
        print("✅ Bot finalizado!")
