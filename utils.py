import requests
from autopost.test_bot import *

def test_facebook(facebook_login,facebook_password,test_publish,url_image=None):
    facebook_create_post(facebook_login,facebook_password,test_publish,url_image=url_image)
    return str(True)
