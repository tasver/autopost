import os


SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') # 'sqlite:///' + os.path.join(basedir, 'site.db')
SECRET_KEY = os.environ.get('SECRET_KEY') #'5791628bb0b13ce0c676dfde280ba245'
SQLALCHEMY_TRACK_MODIFICATIONS = False

S3_BUCKET = os.environ.get('S3_BUCKET')
S3_KEY = os.environ.get('AWS_ACCESS_KEY_ID')
S3_SECRET = os.environ.get('AWS_SECRET_ACCESS_KEY')

REDISTOGO_URL=os.environ.get('REDISTOGO_URL')

CHROMEDRIVER_PATH = os.environ.get('CHROMEDRIVER_PATH')
GOOGLE_CHROME_BIN = os.environ.get('GOOGLE_CHROME_BIN')


#PATH = os.environ.get('PATH')
