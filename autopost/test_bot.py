#from autopost import app, db, bcrypt,driver
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait,Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.file_detector import *
from selenium.webdriver import ActionChains
from autopost import driver
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import time
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
status_message = 'HI, it is test1.58'
facebook_login = 'bohdannavrotskyi@gmail.com'
facebook_password = 'bodik_18'

#driver = webdriver.Chrome(executable_path='/home/tasver/python/Autopost/autopost/chromedriver', chrome_options=chrome_options)

def get_driver():
    #driver = webdriver.Chrome(executable_path='/home/tasver/python/Autopost/autopost/chromedriver', chrome_options=chrome_options)
    get_driv=driver
    return get_driv

def facebook_create_post(facebook_login,facebook_password,status,url_image=None):
    driver = get_driver()
    facebook_login_fun(driver,facebook_login,facebook_password)
    publish_post(driver,status,url_image=url_image)
    exit_driver(driver)



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
    test_url_image = download(url_image)
    #time.sleep(2)
    WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, "//div[starts-with(@id, 'u_0_')]//textarea[@name='xhpc_message']")))
    url_image_test = "/home/tasver/Pictures/test.png"

    #file_input.send_keys("/home/tasver/Pictures/test.png")
    # Generally it's better to wrap the file path in one of the methods
    # in os.path to return the actual path to support cross OS testing.
    # file_input.send_keys(os.path.abspath("path/to/profilepic.gif"))

    driver.find_element_by_xpath("//div[starts-with(@id, 'u_0_')]//textarea[@name='xhpc_message']").send_keys(status_message)
    time.sleep(1)
    #s3_url = 's3://autopost-dyploma/admin/55b455a0e864370d76da.png'
    if url_image!=None:
        file_test = driver.find_element_by_class_name("fbReactComposerAttachmentSelector_MEDIA")
    #driver.file_detector = LocalFileDetector()
        time.sleep(1)
    #file_test.click()
        test = driver.find_element_by_xpath("//input[@type='file']")
        #print(test)
        time.sleep(2)
        test.send_keys(test_url_image)
        time.sleep(6)
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





#go_to_profile()
#print(get_post(0))
#delete_post(0)
#publish_post_public(url,status_message)
#print(get_all_posts())

#facebook_create_post(facebook_login,facebook_password,status_message,url_image='/home/tasver/python/Autopost/tmp/admin/1ba403b60d77c3033233.png')
