import os
import pandas as pd
import time
import glob
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
PASSWORD = os.getenv("SENHA")

class Link:
    url_eqs = "https://eqs.arenanet.com.br/"
    url_chm = "https://eqs.arenanet.com.br/dist/#/chm/chamado" 

def wait_loading_complete(wait, driver, css_selector=".p-blockui-document.p-blockui.p-component-overlay"):
    try:
        wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, css_selector)))
        print("✅ Loading complete!")
    except Exception as e:
        print(f"❌ Loading timeout: {e}")
        driver.quit()
        exit()

def init_driver():
    download_dir = os.path.join(os.getcwd(), "downloads")
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "plugins.always_open_pdf_externally": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver, download_dir

def access_page(driver, url):
    driver.get(url)
    time.sleep(5)

def fill_login_form(driver):
    wait = WebDriverWait(driver, 10)
    login_input = driver.find_element(By.ID, "login")
    password_input = driver.find_element(By.ID, "senha")
    login_input.send_keys(LOGIN)
    password_input.send_keys(PASSWORD)
    login_button = driver.find_element(By.CLASS_NAME, "p-button-info")
    login_button.click()
    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "layout-tabmenu")))
        print("✅ Login successful!")
        time.sleep(2)
    except:
        print("❌ Login failed! Check credentials or page structure.")
        driver.quit()
        exit()

def navigate_to_report(driver):
    driver.get(Link.url_chm)
    print("✅ Navigating to report page!")
    time.sleep(1)
    wait = WebDriverWait(driver, 30)
    wait_loading_complete(wait, driver)
    time.sleep(1)
    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "card")))
        print("✅ Report page loaded!")
    except Exception as e:
        print(f"❌ Report not found: {e}")
        raise

def click_export_excel(driver):
    wait = WebDriverWait(driver, 10)
    try:
        elements = driver.find_elements(By.CSS_SELECTOR, ".p-d-flex.p-jc-between.p-ai-center")
        if len(elements) >= 2:
            closed_button = elements[2]
            closed_button.click()
            print("✅ 'Closed' button clicked!")
        else:
            print("❌ 'Closed' button not found.")
    except Exception as e:
        print(f"❌ Error clicking closed button: {e}")
        raise
    wait_loading_complete(wait, driver)
    time.sleep(1)
    try:
        export_button = driver.find_element(By.CSS_SELECTOR, ".p-button-outlined.p-button-secondary.p-button.p-component.ng-star-inserted")
        export_button.click()
        print("✅ 'Export Excel' button clicked!")
    except Exception as e:
        print(f"❌ Error clicking export button: {e}")
        raise
    wait_loading_complete(wait, driver)
    
def process_file(file_path):
    cols = ["ID", "TIPO", "ATIVIDADE", "LOCAL", "RESPONSÁVEL", "FECHAMENTO", "DURAÇÃO"]
    try:
        df = pd.read_excel(file_path)
        df = df[cols]
        df.to_excel(file_path, index=False)
        dados_folder = os.path.join(os.getcwd(), "data")
        if not os.path.exists(dados_folder):
            os.makedirs(dados_folder)
        csv_path = os.path.join(dados_folder, "dados.csv")
        df.to_csv(csv_path, index=False)
        print(f"✅ File processed and saved at: {file_path} and CSV updated at: {csv_path}")
        return file_path
    except Exception as e:
        print(f"❌ Error processing file: {e}")
        return None

def wait_for_download_complete(download_dir, timeout=30):
    print("⏳ Waiting for Excel download...")
    data_path = os.path.join(download_dir, "dados.xlsx")
    if os.path.exists(data_path):
        os.remove(data_path)
        print("🗑️ Old 'dados.xlsx' removed.")
    end_time = time.time() + timeout
    while time.time() < end_time:
        files = glob.glob(os.path.join(download_dir, "*.xls*"))
        if files:
            new_file = files[0]
            new_path = os.path.join(download_dir, "dados.xlsx")
            os.rename(new_file, new_path)
            print(f"✅ Download complete and renamed to: {new_path}")
            return new_path
        time.sleep(1)
    print("❌ Timeout! No file was downloaded.")
    return None

def run_bot():
    print("🔹 Starting BOT_CEF...")
    driver, download_dir = init_driver()
    url = Link.url_eqs
    try:
        access_page(driver, url)
        fill_login_form(driver)
        navigate_to_report(driver)
        click_export_excel(driver)
        downloaded_file = wait_for_download_complete(download_dir)
        if downloaded_file:
            print(f"📂 File available at: {downloaded_file}")
            process_file(downloaded_file)
    finally:
        # driver.quit()
        print("✅ Bot finished!")

if __name__ == "__main__":
    run_bot()
