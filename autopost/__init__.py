from flask import Flask, request, jsonify, make_response
import uuid
#import json, facebook
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
import os
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_ckeditor import CKEditor


config_file='settings.py'
app = Flask(__name__)
#basedir = os.path.abspath(os.path.dirname(__file__))

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

#token = {"EAALXfsrsP9IBAHx6ynvs54cMyZAQPrEnUraLGZBo1i6z73gcbRvFGcegQq2GYmRkVrEyeziZBS5PsBZB8NYLHPl5v2wdRd7jwFOabmDMuwka1rzpeqhWhSLhmczAGdMjjH3W6oE97DgD69hG9ivSyjZBkkLWMUWRyp4sbCtmMwYpQ7xSS5AE3aPrwmybRGpFlyqfU121uxKc8mBy7RTYuyZB6Oa0sNB0dMuTcN9QxN5BKdE2nu0cTg"}
#graph = facebook.GraphAPI(token)

#fields = ['email, name']
#profile = graph.get_object('me',fields=fields)
#print(json.dumps(profile,indent=4))


from autopost import routes

