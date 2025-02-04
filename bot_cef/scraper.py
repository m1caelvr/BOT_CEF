import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time

if os.getenv("GITHUB_ACTIONS") is None:
    load_dotenv()

LOGIN = os.getenv("LOGIN")
SENHA = os.getenv("SENHA")


def run_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--disable-logging")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def acess_page(driver, url):
    try:
        driver.get(url)
        print("Título da página:", driver.title)
    except Exception as e:
        print("Erro ao acessar a página:", e)


def fill_login_form(driver):
    try:
        time.sleep(2)
        login_input = driver.find_element(By.ID, "login")
        senha_input = driver.find_element(By.ID, "senha")

        login_input.send_keys(LOGIN)
        senha_input.send_keys(SENHA)
        senha_input.send_keys(Keys.RETURN)

        print("Credenciais inseridas com sucesso!")
    except Exception as e:
        print("Erro ao preencher o formulário:", e)


def run_bot():
    print("Iniciando BOT_CEF...")
    driver = run_driver()
    try:
        acess_page(driver, "https://eqs.arenanet.com.br/")
        fill_login_form(driver)
    finally:
        driver.quit()
        print("Bot finalizado!")
