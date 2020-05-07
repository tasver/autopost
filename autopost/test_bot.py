#from autopost import app, db, bcrypt,driver
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait,Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from autopost import driver
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import time
from bs4 import BeautifulSoup
#from autopost.settings import PATH
import os

#chrome_options = webdriver.ChromeOptions()
#chrome_options.add_argument("--no-sandbox")
#prefs = {"profile.default_content_setting_values.notifications" : 2}
#chrome_options.add_experimental_option("prefs",prefs)

facebook_email = './/*[@id="email"]'
facebook_password = './/*[@id="pass"]'
facebook_login_button = './/*[@id="loginbutton"]'

url = 'https://www.facebook.com/Test_dyploma-autopost-105020864533772/?modal=admin_todo_tour'
status_message = 'HI, it is test5.21'
facebook_login2 = 'bohdannavrotskyi@gmail.com'
facebook_password2 = 'bodik_18'

#driver = webdriver.Chrome(ChromeDriverManager().install())
#driver = webdriver.Chrome(executable_path='/home/tasver/python/Autopost/autopost/chromedriver', chrome_options=chrome_options)
#driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)

def facebook_login(login,password):
    status = False
    driver.get('https://www.facebook.com')
    facebook_email_element = driver.find_element_by_xpath(facebook_email)
    facebook_email_element.send_keys(facebook_login2)
    time.sleep(2.4)
    facebook_password_element = driver.find_element_by_xpath(facebook_password)
    facebook_password_element.send_keys(facebook_password2)
    time.sleep(2.5)
    facebook_login_element = driver.find_element_by_xpath(facebook_login_button)
    facebook_login_element.click()
    time.sleep(1.3)
    status = True
    return status

def exit_driver():
    time.sleep(1)
    driver.close()


def publish_post(status_message,url_image=None):
    WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.XPATH, "//div[starts-with(@id, 'u_0_')]//textarea[@name='xhpc_message']")))

    driver.find_element_by_xpath("//div[starts-with(@id, 'u_0_')]//textarea[@name='xhpc_message']").send_keys(status_message)
    time.sleep(1)
    buttons = driver.find_elements_by_tag_name('button')
    time.sleep(2)
    for button in buttons:
        if button.text=='Опублікувати':
            button.click()
            break
        elif button.text=='Post':
            button.click()
            break
        elif button.text=='Отправить':
            button.click()
            break
    time.sleep(1)

def publish_post_public(url,status_message):

    driver.get(url)
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//div[starts-with(@id, 'u_0_')]//textarea[@name='xhpc_message']")))

    driver.find_element_by_xpath("//div[starts-with(@id, 'u_0_')]//textarea[@name='xhpc_message']").send_keys(status_message)
    time.sleep(5)
    buttons = driver.find_elements_by_tag_name('button')
    time.sleep(4)
    for button in buttons:
        if button.text=='Опублікувати':
            button.click()
            break
        elif button.text=='Post':
            button.click()
            break
        elif button.text=='Отправить':
            button.click()
            break
    time.sleep(5)


def go_to_profile():
    profile = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//a[@accesskey='2']")))
    time.sleep(1)
    profile.click()

def get_post(n):
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='story-subtitle']")))
    driver.find_elements_by_xpath("//div[@data-testid='story-subtitle']")
    posts = driver.find_elements_by_class_name("timestampContent")
    posts[n].click()
    time.sleep(2)
    url = driver.current_url
    return str(url)

def get_all_posts():
    post_links = []
    n = 0
    temp = True
    while temp:
        try:
            post_links.append(get_post(n))
            time.sleep(2)
            driver.back()
            time.sleep(1)
            n = n + 1
        except:
            "End of list"
            temp = False
    return post_links

def delete_post(n):
    test = get_post(n)
    url = test[12:]
    mobile_url = 'https://.m.' + url
    driver.get(mobile_url)
    driver.find_element_by_xpath('//a[@aria-haspopup="true"]').click()
    time.sleep(1.5)
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//a[@data-sigil="touchable touchable removeStoryButton enabled_action"]'))).click()
    time.sleep(6)
    buttons = driver.find_elements_by_xpath('//a[@role="button"]')
    print(buttons)
    time.sleep(4)
    for button in buttons:
        if button.text=='Видалити':
            button.click()
            break
        elif button.text=='Delete':
            button.click()
            break
        elif button.text=='Удалить':
            button.click()
            break
    time.sleep(5)



#facebook_login(facebook_login2,facebook_password2)
#go_to_profile()
#print(get_post(0))
#delete_post(0)
#publish_post_public(url,status_message)
#print(get_all_posts())
#publish_post("urec oluhec")
#exit_driver()
