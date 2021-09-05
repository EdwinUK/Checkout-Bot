from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
import smtplib
import sys
from random import randint
from time import sleep


headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome'
                         '/89.0.4389.90 Safari/537.36'}
urls = ["", ""]
chromedriver_path = "C:\Program Files (x86)\chromedriver.exe"
chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'


def stock_check():

    while True:
        for url in urls:
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.content, 'html.parser')
            try:
                soup.find('div', {'class': 'relatedProducts'}).decompose()
            except:
                pass
            for each in soup.findAll('div', {'class': 'buyButton medium'}):
                available = each.find('a', {'class', 'btn'}).text
                if available == "Add To Basket":
                    print("Stock Found")
                    url_for_stock = url
                    purchase_stock(url_for_stock)
                    send_email()
                    sys.exit()
            print("No stock available currently")
            sleep(randint(2, 10))


def purchase_stock(url_for_stock):

    # setting up driver
    chrome_options = Options()
    chrome_options.add_argument("user-data-dir=selenium")
    driver = webdriver.Chrome(executable_path=chromedriver_path, options=chrome_options)
    driver.maximize_window()
    driver.get(url_for_stock)

    # automatic clicking
    def auto_clicking(type, name_of_element, time):
        product = WebDriverWait(driver, time).until(
            EC.element_to_be_clickable((type, name_of_element))
        )
        product.click()

    # javascript button clicking
    def js_clicking(type, name_of_element, path, time):
        WebDriverWait(driver, time).until(
            EC.element_to_be_clickable((type, name_of_element))
        )
        button = driver.find_element_by_xpath(path)
        driver.execute_script("arguments[0].click();", button)

    # automatic typing
    def auto_type(name_of_element, text, enter_key=False):
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, name_of_element))
        )
        element.send_keys(text)
        if enter_key:
            element.send_keys(Keys.RETURN)

    # dropdown selection
    def dropdown(name_of_element, value):
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, name_of_element))
        )
        selection = Select(driver.find_element_by_css_selector(name_of_element))
        selection.select_by_visible_text(value)

    # THE ITEM YOU WISH TO BUY
    auto_clicking(By.PARTIAL_LINK_TEXT, "", 30)


    # if fully logged out of account
    try:
        driver.find_element_by_xpath('/html/body/div[2]/header/div/div[3]/div[1]/div[1]/span[2]/a[1]')
        auto_clicking(By.LINK_TEXT, "Login", 10)
        auto_clicking(By.ID, "emailLogin", 10)
        auto_type("emailLogin", "")
        auto_type("passwordLogin", "", True)
        auto_clicking(By.LINK_TEXT, "ADD TO BASKET", 20)
        auto_clicking(By.LINK_TEXT, "CHECKOUT", 20)
        auto_clicking(By.LINK_TEXT, "CHECKOUT NOW", 20)
        try:
            if driver.find_element_by_xpath('//*[@id="scansure"]/div/div/div[2]/div[1]/div/p[2]/button[2]') in driver:
                js_clicking(By.CLASS_NAME, "scansure-select-step",
                            '//*[@id="scansure"]/div/div/div[2]/div[1]/div/p[2]/button[2]',
                            20)
        except:
            pass

    # if logged in but a password confirm
    except NoSuchElementException:
        auto_clicking(By.LINK_TEXT, "ADD TO BASKET", 10)
        auto_clicking(By.LINK_TEXT, "CHECKOUT", 10)
        auto_clicking(By.LINK_TEXT, "CHECKOUT NOW", 10)
        try:
            auto_type("passwordLogin", "", True)
        except:
            pass

    # final checkout page
    finally:
        auto_type("ko-autofill-trigger-id", "")
        auto_type("nameOnCard", "")
        auto_type("cvv", "")
        dropdown('#endMonth', '')
        dropdown('#payment > div > div > div.payment-options > div.payment-carddetails > div > div:nth-child(2) > '
                 'div.col2 > ''div:nth-child(1) > select.year.sessioncamexclude', '2023')

    # auto_clicking(By.PARTIAL_LINK_TEXT, "COMPLETE ORDER WITH", 10)


def send_email():
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    tolist = ['', '']

    server.login('', '')

    subject = "Stock Notification"
    body = "Website Link: "

    msg = f"Subject: {subject}\n\n{body}"

    server.sendmail(
        '',
        tolist,
        msg
    )
    print("Email has been sent!")

    server.quit()


stock_check()
