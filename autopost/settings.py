import os


SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') # 'sqlite:///' + os.path.join(basedir, 'site.db')
SECRET_KEY = os.environ.get('SECRET_KEY') #'5791628bb0b13ce0c676dfde280ba245'
SQLALCHEMY_TRACK_MODIFICATIONS = False

S3_BUCKET = os.environ.get('S3_BUCKET')
aws_access_key_id = os.environ.get('aws_access_key_id')
aws_secret_access_key = os.environ.get('aws_secret_access_key')

CHROMEDRIVER_PATH = os.environ.get('CHROMEDRIVER_PATH')
GOOGLE_CHROME_BIN = os.environ.get('GOOGLE_CHROME_BIN')


#PATH = os.environ.get('PATH')
