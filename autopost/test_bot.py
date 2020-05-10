#from autopost import app, db, bcrypt,driver
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait,Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.file_detector import *
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from autopost import driver
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import time
import pyperclip
import clipboard
from tkinter import *
import xerox

from bs4 import BeautifulSoup
#from autopost.settings import PATH
import os
from autopost.resources import *


#chrome_options = webdriver.ChromeOptions()
#chrome_options.add_argument("--no-sandbox")
#prefs = {"profile.default_content_setting_values.notifications" : 2}
#chrome_options.add_experimental_option("prefs",prefs)

facebook_email = './/*[@id="email"]'
facebook_password_field = './/*[@id="pass"]'
facebook_login_button = './/*[@id="loginbutton"]'

url = 'https://www.facebook.com/Test_dyploma-autopost-105020864533772/?modal=admin_todo_tour'
status_message = 'HI, it is test8.19df'
facebook_login = '380669288859'
facebook_password = 'Kamaro1231'

#driver = webdriver.Chrome(executable_path='/home/tasver/python/Autopost/autopost/chromedriver', chrome_options=chrome_options)

def get_driver():
    #driver = webdriver.Chrome(executable_path='/home/tasver/python/Autopost/autopost/chromedriver', options=chrome_options)
    get_driv=driver
    return get_driv

def facebook_login_fun(driver,login,password):
    status = False
    driver.get('https://www.facebook.com')
    facebook_email_element = driver.find_element_by_xpath(facebook_email)
    facebook_email_element.send_keys(facebook_login)
    time.sleep(1.5)
    facebook_password_element = driver.find_element_by_xpath(facebook_password_field)
    facebook_password_element.send_keys(facebook_password)
    time.sleep(1.5)
    facebook_login_element = driver.find_element_by_xpath(facebook_login_button)
    facebook_login_element.click()
    time.sleep(1.5)
    status = True
    return status

def exit_driver(driver):
    time.sleep(1)
    driver.quit()

def publish_post(driver,status_message,url_image=None):
    time.sleep(2)
    time.sleep(1.5)
    WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, "//div[starts-with(@id, 'u_0_')]//textarea[@name='xhpc_message']")))
    print('still working before pyperclip')
    if url_image!= None:
        sleep(1.5)
        input = driver.find_element_by_xpath("//div[starts-with(@id, 'u_0_')]//textarea[@name='xhpc_message']")
        time.sleep(2)
        input.send_keys(url_image)
        time.sleep(3)
        xerox.copy(url_image)
        #Thing_you_want_to_copy|xclip -selection c
        elem = driver.switch_to_active_element()
        #elem.send_keys(Keys.CONTROL + "a")
        #time.sleep(3)
        #actions = ActionChains(elem)
        #actions.key_down(Keys.CONTROL)
        #actions.send_keys("c")
        #actions.key_up(Keys.CONTROL)

        """
        #new_link = elem.send_keys(Keys.CONTROL + "c")
        #rint(new_link)
        time.sleep(2)
        url_image_len1 = len(url_image)
        while url_image_len1>-1:
            try:
                elem.send_keys(Keys.BACKSPACE)
                print('delete')
                url_image_len1 = url_image_len1-1
            except:
                print('Somethi wrong1')
        time.sleep(3)
        """
        elem.send_keys(status_message)
        time.sleep(3)

        elem.send_keys(Keys.ENTER)
        elem.send_keys(Keys.ENTER)
        time.sleep(1.5)
        #elem.send_keys(xerox.paste())
        elem.send_keys(Keys.CONTROL + "v")
        time.sleep(5)
        url_image_len = len(url_image)
        while url_image_len>-1:
            try:
                elem.send_keys(Keys.BACKSPACE)
                print('delete')
                url_image_len = url_image_len-1
            except:
                print('Somethi wrong2')
        time.sleep(3)
        time.sleep(3)
        time.sleep(4)
    else:
        ext_to_put_to_clipboard = driver.find_element_by_xpath("//div[starts-with(@id, 'u_0_')]//textarea[@name='xhpc_message']").send_keys(status_message)
    time.sleep(2)
    buttons = driver.find_elements_by_tag_name('button')
    time.sleep(1)
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
    return True

def publish_post_public(driver,url,status_message):

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

def go_to_profile(driver):
    profile = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//a[@accesskey='2']")))
    time.sleep(1)
    profile.click()

def get_post(driver,n):
    go_to_profile(driver)
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='story-subtitle']")))
    driver.find_elements_by_xpath("//div[@data-testid='story-subtitle']")
    posts = driver.find_elements_by_class_name("timestampContent")
    posts[n].click()
    time.sleep(2)
    url = driver.current_url
    return str(url)

def get_mobile_post(driver,n):
    go_to_profile(driver)
    url = driver.current_url
    url2 = url[12:]
    mobile_url = 'https://.m.' + url2
    driver.get(mobile_url)

    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//div[@data-sigil='m-feed-voice-subtitle']")))
    driver.find_elements_by_xpath("//div[@data-sigil='m-feed-voice-subtitle']")
    posts = driver.find_elements_by_tag_name("abbr")
    posts[n].click()
    time.sleep(2)

    return str(url)

def get_all_posts(driver):
    post_links = []
    n = 0
    temp = True
    while temp:
        try:
            post_links.append(get_post(driver,n))
            time.sleep(2)
            driver.back()
            time.sleep(1)
            n = n + 1
        except:
            "End of list"
            temp = False
    return post_links

def delete_post(driver,n):
    test = get_mobile_post(driver,n)
    time.sleep(1.5)
    driver.find_element_by_xpath('//a[@aria-haspopup="true"]').click()
    time.sleep(1.5)
    WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, '//a[@data-sigil="touchable touchable removeStoryButton enabled_action"]'))).click()
    time.sleep(3)
    buttons = driver.find_elements_by_xpath('//a[@role="button"]')
    #print(buttons)
    time.sleep(2)
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
    time.sleep(3)


def facebook_create_post(facebook_login,facebook_password,status,url_image=None):
    #try:
    driver = get_driver()
    #try:
    facebook_login_fun(driver,facebook_login,facebook_password)
    print('success login')
# except:
    print('login failed')
#try:
    publish_post(driver,status,url_image=url_image)
    print('success publish')
#except:
    print('publish failed')
    exit_driver(driver)
#except:
    print("something went wrong")
        #return False
    #return True

def facebook_delete_post(facebook_login,facebook_password,n):
    driver = get_driver()
    facebook_login_fun(driver,facebook_login,facebook_password)
    delete_post(driver,n)
    exit_driver(driver)

def facebook_create_post_to_public(facebook_login,facebook_password,url,status):
    driver = get_driver()
    facebook_login_fun(driver,facebook_login,facebook_password)
    publish_post_public(driver,url,status)
    exit_driver(driver)

#facebook_create_post(facebook_login,facebook_password,"test333")
#go_to_profile()
#print(get_post(0))
#delete_post(0)
#publish_post_public(url,status_message)
#print(get_all_posts())

#test_ds = facebook_create_post(facebook_login,facebook_password,status_message,url_image='/home/tasver/python/Autopost/tmp/admin/1ba403b60d77c3033233.png')
#print(test_ds)
