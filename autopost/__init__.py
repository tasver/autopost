from flask import Flask, request, jsonify, make_response
import uuid

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
import os
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_ckeditor import CKEditor
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

config_file='settings.py'
app = Flask(__name__)
#basedir = os.path.abspath(os.path.dirname(__file__))'
"""
options = Options()
options.add_argument("start-maximized"
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")


options.binary_location = os.environ.get('GOOGLE_CHROME_BIN')

options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--remote-debugging-port=9222')
options.add_argument('--proxy-server='+proxy)

webdriver.Chrome(executable_path=str(os.environ.get('CHROMEDRIVER_PATH')), chrome_options=options)
"""

chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
prefs = {"profile.default_content_setting_values.notifications" : 2}
chrome_options.add_experimental_option("prefs",prefs)
driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)


app.config.from_pyfile(config_file)
db = SQLAlchemy(app)

migrate = Migrate(app,db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

app.config['CKEDITOR_PKG_TYPE'] = 'basic'
ckeditor = CKEditor(app)


import autopost.forms as views
admin = Admin(app, index_view=views.MyAdminIndexView())
admin.add_view(views.UserAdminView(views.User, db.session))
admin.add_view(views.PostAdminView(views.Post, db.session))
admin.add_view(views.ProjectAdminView(views.Project, db.session))
admin.add_view(views.SocialAdminView(views.Social, db.session))



from autopost import routes

