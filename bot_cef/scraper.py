from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def iniciar_driver():
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


def acessar_pagina(driver, url):
    try:
        driver.get(url)
        print("Título da página:", driver.title)
    except Exception as e:
        print("Erro ao acessar a página:", e)


def run_bot():
    print("Iniciando BOT_CEF...")
    driver = iniciar_driver()
    try:
        acessar_pagina(driver, "https://eqs.arenanet.com.br/")
    finally:
        driver.quit()
        print("Bot finalizado!")
