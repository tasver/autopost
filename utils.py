import requests
from autopost.test_bot import *
from worker import *

queue = Queue(connection=conn)
def test_facebook(facebook_login,facebook_password,test_publish,url_image=None):
    facebook_create_post(facebook_login,facebook_password,test_publish,url_image=url_image)
    return str(True)
