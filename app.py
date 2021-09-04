from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup as soup
import pandas as pd
import time
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import jinja2
import os
import shutil
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///CompanyDetails.db'
db = SQLAlchemy(app)


class netInsuranceDbModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Ragione_Sociale = db.Column(db.String(400))
    Natura_Giuridica = db.Column(db.String(400))
    Codice_Fiscale = db.Column(db.String(400))
    PartitaIva = db.Column(db.String(400))
    Indirizzo = db.Column(db.String(400))
    CAP = db.Column(db.String(400))
    Comune = db.Column(db.String(400))
    Provincia = db.Column(db.String(400))
    Parametro_Assuntivo = db.Column(db.String(400))
    Messaggio = db.Column(db.String(400))
    Scrapping_Time = db.Column(db.String(400))


class AFIESCADbModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Business_name = db.Column(db.String(400))
    VAT_number = db.Column(db.String(400))
    Fiscal_Code = db.Column(db.String(400))
    Address = db.Column(db.String(400))
    Date_and_time = db.Column(db.String(400))
    Rea = db.Column(db.String(400))
    Registration_no_reg_businesses = db.Column(db.String(400))
    Prov_reg_businesses = db.Column(db.String(400))
    Legal_form = db.Column(db.String(400))
    Scrapping_Time = db.Column(db.String(400))


today = datetime.now().strftime("{%d-%m-%Y}")
times = datetime.now().strftime("{%I.%M.%p}")
DateTimeStamp = str(str(today)+"__"+str(times))


@app.route('/getCompanyId', methods=['POST', 'GET'])
def getCompanyId():
    try:
        Companies_Id = request.form['ComapnyIdURL'].split("\r\n")
    except:
        return startApplication()
    print(Companies_Id)
    return startScrapingFunctions(Companies_Id)


@app.route("/")
def startApplication():
    return render_template("index.html")


def netInsuranceScraper(Companies_Id):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument("--no-sandbox")
    options.add_argument("--log-level=3")
    options.add_argument("--start-maximized")
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    download_directory = os.path.dirname(os.path.realpath(
        __file__))+"\\Donwloaded_PDF\\"+str(DateTimeStamp)+"\\netInsurance\\"
    if not os.path.exists(download_directory):
        os.makedirs(download_directory)
    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.default_content_setting_values.geolocation": 2,
        "profile.managed_default_content_settings.images": 2,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True,
        "download.default_directory": download_directory,
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument(
        f'user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36')
    options.binary_location = r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    driver = webdriver.Chrome(
        options=options, executable_path="chromedriver.exe")

    driver.command_executor._commands["send_command"] = (
        "POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd': 'Page.setDownloadBehavior', 'params': {
        'behavior': 'allow', 'downloadPath': download_directory}}
    command_result = driver.execute("send_command", params)

    url = "https://arearis.netinsurance.it/Area.aspx"
    driver.get(url.replace(",", "").replace(
        "\n", "").replace("\r", "").strip())
    WebDriverWait(driver, 10).until(
        EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "#username")))
    driver.find_element_by_css_selector(
        '#username').send_keys('maurizio.paolangeli')
    driver.find_element_by_css_selector('#password').send_keys('genial2018')
    driver.find_element_by_css_selector('#password').send_keys(Keys.RETURN)
    WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located(
        (By.CSS_SELECTOR, "#MenuSX > ul > li:nth-child(3) > a")))
    driver.get(
        'https://arearis.netinsurance.it/Area/ConsultazioneAmministrazione.aspx')
    netInsuranceData = []
    for c_id in Companies_Id:
        WebDriverWait(driver, 15).until(EC.visibility_of_all_elements_located(
            (By.CSS_SELECTOR, "#ContentCentrale_txtCodiceFiscaleRicerca")))
        driver.find_element_by_css_selector(
            '#ContentCentrale_txtCodiceFiscaleRicerca').clear()
        driver.find_element_by_css_selector(
            '#ContentCentrale_txtCodiceFiscaleRicerca').send_keys(c_id)
        driver.find_element_by_css_selector(
            '#ContentCentrale_btnRicercaAmministrazione').click()
        time.sleep(2)
        WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located(
            (By.CSS_SELECTOR, "#ContentCentrale_UpdatePanel")))
        time.sleep(2)
        page_soup = soup(driver.page_source, "lxml")
        All_Values = page_soup.findAll("div", {"class": "InternoFieldset"})[
            1].findAll("input")
        All_Values_2 = page_soup.findAll("div", {"class": "InternoFieldset"})[
            2].findAll("input")
        List_ = []
        for a in All_Values:
            try:
                a["value"]
                List_.append(a["value"])
            except:
                List_.append("")
        for a in All_Values_2:
            try:
                a["value"]
                List_.append(a["value"])
            except:
                List_.append("")
        driver.find_element_by_css_selector(
            '#ContentCentrale_pnlAmministrazione > div.Centra > b > a').click()
        time.sleep(8)
        filename = max(
            [download_directory + "\\" + f for f in os.listdir(download_directory)], key=os.path.getctime)
        shutil.move(os.path.join(download_directory, filename),
                    str(os.path.join(download_directory, List_[2]))+".pdf")
        List_.append(DateTimeStamp)
        time.sleep(2)
        netInsuranceData.append(List_)
    driver.quit()
    return netInsuranceData


def AFIESCAScraper(Companies_Id):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument("--no-sandbox")
    options.add_argument("--log-level=3")
    options.add_argument("--start-maximized")
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    download_directory = os.path.dirname(os.path.realpath(
        __file__))+"\\Donwloaded_PDF\\"+str(DateTimeStamp)+"\\AFIESCA\\"
    if not os.path.exists(download_directory):
        os.makedirs(download_directory)
    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.default_content_setting_values.geolocation": 2,
        "profile.managed_default_content_settings.images": 2,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True,
        "download.default_directory": download_directory,
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument(
        f'user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36')
    options.binary_location = r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    driver = webdriver.Chrome(
        options=options, executable_path="chromedriver.exe")
    driver.command_executor._commands["send_command"] = (
        "POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd': 'Page.setDownloadBehavior', 'params': {
        'behavior': 'allow', 'downloadPath': download_directory}}
    command_result = driver.execute("send_command", params)
    url = "https://class-go.class-consulting.it/valutazioni"
    driver.get(url.replace(",", "").replace(
        "\n", "").replace("\r", "").strip())
    WebDriverWait(driver, 10).until(
        EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "#email")))
    driver.find_element_by_css_selector(
        '#email').send_keys('rossella.ippolito@spefin.it')
    driver.find_element_by_css_selector('#password').send_keys('Is2cPmq8')
    driver.find_element_by_css_selector('#password').send_keys(Keys.RETURN)
    time.sleep(2)
    WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located(
        (By.CSS_SELECTOR, "body > app-root > div > app-admin-layout > div > div.main__wrapper > app-valutazioni > div > div.main__wrapper--top > div > a")))
    driver.find_element_by_css_selector(
        'body > app-root > div > app-admin-layout > div > div.main__wrapper > app-valutazioni > div > div.main__wrapper--top > div > a').click()
    AFIESCAData = []
    for c_id in Companies_Id:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "#iva")))
        driver.find_element_by_css_selector('#iva').clear()
        driver.find_element_by_css_selector('#iva').send_keys(c_id)
        time.sleep(3)
        driver.find_element_by_css_selector('#iva').send_keys(Keys.RETURN)
        time.sleep(4)
        WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located(
            (By.CSS_SELECTOR, "body > app-root > div > app-admin-layout > div > div.main__wrapper > app-valutazioni-details > div > div.row.valuate-status-row > div.grid__item.grid--55 > div > div.content.no-padding > div:nth-child(1)")))
        page_soup = soup(driver.page_source, "lxml")
        All_Values = page_soup.findAll("div", {"class": "info col-sm-6"})
        List_ = []
        for a in All_Values:
            try:
                List_.append(a.get_text())
            except:
                List_.append("")
        driver.find_element_by_css_selector(
            'body > app-root > div > app-admin-layout > div > div.main__wrapper > app-valutazioni-details > div > div:nth-child(2) > div > div > div.content.valuate-details-files > ul > li > a').click()
        time.sleep(7)
        filename = max(
            [download_directory + "\\" + f for f in os.listdir(download_directory)], key=os.path.getctime)
        shutil.move(os.path.join(download_directory, filename),
                    str(os.path.join(download_directory, List_[2]))+".pdf")
        List_.append(DateTimeStamp)
        AFIESCAData.append(List_)
        driver.get("https://class-go.class-consulting.it/nuovaValutazioni")
        time.sleep(3)
        WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located(
            (By.CSS_SELECTOR, "body > app-root > div > app-admin-layout > div > div.main__wrapper > app-valutazioni > div > div.main__wrapper--top > div > a")))
        driver.find_element_by_css_selector(
            'body > app-root > div > app-admin-layout > div > div.main__wrapper > app-valutazioni > div > div.main__wrapper--top > div > a').click()
        time.sleep(3)
    driver.quit()
    return AFIESCAData


def startScrapingFunctions(Companies_Id):
    # comment = """
    netInsuranceData = netInsuranceScraper(Companies_Id)
    AFIESCAData = AFIESCAScraper(Companies_Id)

    netInsuranceData_PD = pd.DataFrame(netInsuranceData, columns=['Ragione Sociale', 'Natura Giuridica', 'Codice Fiscale',
                                                                  'PartitaIva', 'Indirizzo', 'CAP', 'Comune', 'Provincia', 'Parametro Assuntivo', 'Messaggio', 'Scrapping Time'])
    AFIESCAData_PD = pd.DataFrame(AFIESCAData, columns=['Business name', 'VAT number', 'Fiscal Code', 'Address',
                                                        'Date and time', 'Rea', 'Registration no. reg. businesses', 'Prov. reg. businesses', 'Legal form', 'Scrapping Time'])
    netInsuranceData_PD.to_sql(
        "netInsuranceDbModel", db.engine, index=False, if_exists='append')
    AFIESCAData_PD.to_sql(
        "AFIESCADbModel", db.engine, index=False, if_exists='append')
    # """
    com = """
    netInsuranceData_PD = pd.read_csv(
        "file.csv", encoding="utf-8", lineterminator='\n', error_bad_lines=False)
    AFIESCAData_PD = pd.read_csv(
        "file.csv", encoding="utf-8", lineterminator='\n', error_bad_lines=False)
    
    """
    return render_template('scrapped-result.html', netInsuranceData_tables=netInsuranceData_PD.values, netInsuranceData_titles=netInsuranceData_PD.columns.values, AFIESCAData_tables=AFIESCAData_PD.values, AFIESCAData_titles=AFIESCAData_PD.columns.values)
    #


if __name__ == "__main__":
    app.run(debug=True)
