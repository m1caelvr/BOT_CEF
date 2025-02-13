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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
    time.sleep(5)


def navigation_to_report(driver):
    driver.get("https://eqs.arenanet.com.br/dist/#/chm/chamado")
    print("✅ Navegando para a página de chamado!")

    time.sleep(2)

    wait = WebDriverWait(driver, 30)
    try:
        wait.until(
            EC.invisibility_of_element_located(
                (
                    By.CSS_SELECTOR,
                    ".p-blockui-document.p-blockui.p-component-overlay",
                )
            )
        )
        print("✅ Carregamento concluído!")
    except Exception as e:
        print(f"❌ Tempo de espera esgotado, o carregamento não foi concluído. {e}")
        driver.quit()
        exit()

    time.sleep(3)

    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "card")))
        print("✅ Estou na página de relatório!")
    except Exception as e:
        print(f"❌ Falha ao achar o relatório: {e}")
        raise


def fill_login_form(driver):
    wait = WebDriverWait(driver, 10)

    login_input = driver.find_element(By.ID, "login")
    senha_input = driver.find_element(By.ID, "senha")

    login_input.send_keys(LOGIN)
    senha_input.send_keys(SENHA)

    botao_login = driver.find_element(By.CLASS_NAME, "p-button-info")
    botao_login.click()

    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "layout-tabmenu")))
        print("✅ Login realizado com sucesso!")
        time.sleep(2)

    except:
        print("❌ Falha no login! Verifique as credenciais ou a estrutura da página.")
        driver.quit()
        exit()


def extrair_dados(driver):
    wait = WebDriverWait(driver, 30)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table[role='grid']")))

    try:
        wait = WebDriverWait(driver, 10)
        button_fechados = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//span[text()='Fechados:']/ancestor::button")
            )
        )
        button_fechados.click()
        print("✅ Clicado no botão 'Fechados' com sucesso!")
    except Exception as e:
        print(f"❌ Não foi possível clicar no botão 'Fechados': {e}")
        driver.quit()
        exit()

    tabela = driver.find_element(By.CSS_SELECTOR, "table[role='grid']")
    linhas = tabela.find_elements(By.TAG_NAME, "tr")

    data = []
    for linha in linhas[1:]:
        colunas = linha.find_elements(By.TAG_NAME, "td")
        if len(colunas) > 1:
            data.append(
                {
                    "Ação": [
                        button.text
                        for button in colunas[0].find_elements(By.TAG_NAME, "button")
                    ],
                    "ID": colunas[1].text.strip(),
                    "Cód Cliente": colunas[2].text.strip(),
                    "Tipo": colunas[3].text.strip(),
                    "Atividade": colunas[4].text.strip(),
                    "Contrato": colunas[5].text.strip(),
                    "Macroarea": colunas[6].text.strip(),
                    "Local": colunas[7].text.strip(),
                    "Responsável": colunas[8].text.strip(),
                    "Ocorrência": colunas[9].text.strip(),
                    "Prazo": colunas[10].text.strip(),
                    "Início": colunas[11].text.strip(),
                    "Fechamento": colunas[12].text.strip(),
                    "Prioridade": colunas[13].text.strip(),
                    "Situação": colunas[14].text.strip(),
                }
            )

    df = pd.DataFrame(data)

    print(df)

    path = os.path.join(os.getcwd(), "data", "relatorio.csv")
    df.to_csv(path, index=False)
    print(f"📂 Dados extraídos e salvos em '{path}'")
    time.sleep(3)


def run_bot():
    print("🔹 Iniciando BOT_CEF...")
    driver = run_driver()

    url = "https://eqs.arenanet.com.br/"

    try:
        acess_page(driver, url)
        fill_login_form(driver)
        navigation_to_report(driver)
        extrair_dados(driver)
    finally:
        # driver.quit()
        print("✅ Bot finalizado!")


if __name__ == "__main__":
    run_bot()
