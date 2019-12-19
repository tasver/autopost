import os

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')#'sqlite:///' + os.path.join(basedir, 'site.db')
SECRET_KEY = os.environ.get('SECRET_KEY') #'5791628bb0b13ce0c676dfde280ba245'
SQLALCHEMY_TRACK_MODIFICATIONS = True
