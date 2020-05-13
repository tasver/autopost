#from autopost import app, db, bcrypt,driver
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait,Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.file_detector import *
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
#from autopost import driver
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import time

from bs4 import BeautifulSoup
#from autopost.settings import PATH
import os
from autopost.resources import *


chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--no-sandbox")
prefs = {"profile.default_content_setting_values.notifications" : 2}
chrome_options.add_experimental_option("prefs",prefs)

facebook_email = './/*[@id="email"]'
facebook_password_field = './/*[@id="pass"]'
facebook_login_button = './/*[@id="loginbutton"]'

url = 'https://www.facebook.com/Test_dyploma-autopost-105020864533772/?modal=admin_todo_tour'
status_message = 'HI, it is test8.19df'
facebook_login = '380669288859'
facebook_password = 'Kamaro1231'

#driver = webdriver.Chrome(executable_path='/home/tasver/python/Autopost/autopost/chromedriver', chrome_options=chrome_options)

def get_driver():
    driver = webdriver.Chrome(executable_path='/home/tasver/python/Autopost/autopost/chromedriver', options=chrome_options)
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
    time.sleep(3)
    test_frame = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, "//div[starts-with(@id, 'u_0_')]//textarea[@name='xhpc_message']")))

    if url_image!= None:
        sleep(1.5)
        input = driver.find_element_by_xpath("//div[starts-with(@id, 'u_0_')]//textarea[@name='xhpc_message']").send_keys(url_image)
        time.sleep(2)
        elem = driver.switch_to_active_element()
        elem.send_keys(Keys.ENTER)
        elem.send_keys(Keys.ENTER)
        url_image_len2 = len(url_image)
        while url_image_len2>-10:
            try:
                elem.send_keys(Keys.BACKSPACE)
                print('delete')
                url_image_len2 = url_image_len2-1
            except:
                print('Somethi wrong2')
        time.sleep(3)

        #driver.find_element_by_xpath("//div[@aria-label='Відхилити']").click()
        elem.send_keys(status_message)
        print('send message')
        time.sleep(3)
    else:
        ext_to_put_to_clipboard = driver.find_element_by_xpath("//div[starts-with(@id, 'u_0_')]//textarea[@name='xhpc_message']").send_keys(status_message)
    time.sleep(3)
    buttons = driver.find_elements_by_tag_name('button')
    time.sleep(3)
    for button in buttons:
        if button.text=='Опублікувати':
            button.click()
            print('button pressed')
            break
        elif button.text=='Post':
            button.click()
            print('button pressed')
            break
        elif button.text=='Отправить':
            button.click()
            print('button pressed')
            break
    time.sleep(7)
    url = get_post(driver,0)
    time.sleep(2)

    return url

def publish_post_public(driver,url,status_message,url_image=None):
    driver.get(url)
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//div[starts-with(@id, 'u_0_')]//textarea[@name='xhpc_message']")))

    if url_image!= None:
        sleep(1.5)
        input = driver.find_element_by_xpath("//div[starts-with(@id, 'u_0_')]//textarea[@name='xhpc_message']").send_keys(url_image)
        time.sleep(2)
        elem = driver.switch_to_active_element()
        elem.send_keys(Keys.ENTER)
        elem.send_keys(Keys.ENTER)
        url_image_len2 = len(url_image)
        while url_image_len2>-10:
            try:
                elem.send_keys(Keys.BACKSPACE)
                print('delete')
                url_image_len2 = url_image_len2-1
            except:
                print('Somethi wrong2')
        time.sleep(4)

        #driver.find_element_by_xpath("//div[@aria-label='Відхилити']").click()
        elem.send_keys(status_message)
        print('send message')
        time.sleep(5)
    else:
        ext_to_put_to_clipboard = driver.find_element_by_xpath("//div[starts-with(@id, 'u_0_')]//textarea[@name='xhpc_message']").send_keys(status_message)
    time.sleep(7)
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
    time.sleep(7)

    url_ret = get_post_public(driver,0,url)

    return url_ret

def go_to_profile(driver):
    profile = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//a[@accesskey='2']")))
    time.sleep(1)
    profile.click()

def get_post(driver,n):
    go_to_profile(driver)
    time.sleep(4)
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='story-subtitle']")))
    driver.find_elements_by_xpath("//div[@data-testid='story-subtitle']")
    posts = driver.find_elements_by_class_name("timestampContent")
    posts[n].click()
    time.sleep(4)
    url = driver.current_url
    return str(url)

def get_post_public(driver,n,url):
    time.sleep(3)
    driver.get(url)
    time.sleep(4)
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='story-subtitle']")))
    driver.find_elements_by_xpath("//div[@data-testid='story-subtitle']")
    posts = driver.find_elements_by_class_name("timestampContent")
    posts[n].click()
    time.sleep(4)
    url_ret = driver.current_url
    time.sleep(2)
    return str(url_ret)

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
    time.sleep(4)
    url_ret = driver.current_url
    time.sleep(2)
    return str(url_ret)

def get_mobile_post_url(driver,url):
    url2 = url[12:]
    mobile_url = 'https://.m.' + url2
    driver.get(mobile_url)
    time.sleep(2)
    return str(mobile_url)

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

def delete_post(driver,url):
    test = get_mobile_post_url(driver,url)
    time.sleep(3.5)
    driver.find_element_by_xpath('//a[@aria-haspopup="true"]').click()
    time.sleep(3.5)
    WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, '//a[@data-sigil="touchable touchable removeStoryButton enabled_action"]'))).click()
    time.sleep(3)
    buttons = driver.find_elements_by_xpath('//a[@role="button"]')
    #print(buttons)
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


def facebook_create_post(facebook_login,facebook_password,status,url_image=None):
    url = None
    try:
        driver = get_driver()

        try:
            facebook_login_fun(driver,facebook_login,facebook_password)
            print('success login')
        except:
            print('login failed')
        try:
            url = publish_post(driver,status,url_image=url_image)
            print('success publish')
        except:
            print('publish failed')

        exit_driver(driver)
    except:
        print("something went wrong")
            #return False
    return url

def facebook_create_post_public(facebook_login,facebook_password,status,url_image=None,url=None):
    url_ret = None
    try:
        driver = get_driver()
        try:
            facebook_login_fun(driver,facebook_login,facebook_password)
            print('success login')
        except:
            print('login failed')
        try:
            url_ret = publish_post_public(driver,url,status,url_image=url_image)
            url_ret = url_ret[:84]
            print('success publish in public')
        except:
            print('publish public failed')
        exit_driver(driver)
    except:
        print("something went wrong")
            #return False
    return url_ret

def facebook_delete_post(facebook_login,facebook_password,url):
    try:
        driver = get_driver()
        try:
            facebook_login_fun(driver,facebook_login,facebook_password)
            print('success login')
        except:
            print('login failed')
        try:
            delete_post(driver,url)
            print('success delete')
        except:
            print('delete failed')
        exit_driver(driver)
    except:
        print("something went wrong, dont delete")

#def facebook_create_post_to_public(facebook_login,facebook_password,url,status):
#    driver = get_driver()
#    facebook_login_fun(driver,facebook_login,facebook_password)
#    publish_post_public(driver,url,status)
#    exit_driver(driver)

#facebook_create_post(facebook_login,facebook_password,"test333")
#go_to_profile()
#print(get_post(0))
#delete_post(0)
#publish_post_public(url,status_message)
#print(get_all_posts())

#test_ds = facebook_create_post(facebook_login,facebook_password,status_message,url_image='/home/tasver/python/Autopost/tmp/admin/1ba403b60d77c3033233.png')
#print(test_ds)
