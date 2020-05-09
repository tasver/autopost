import boto3
from autopost.settings import S3_BUCKET, S3_KEY, S3_SECRET
from flask import session,Response
import os
import errno
import botocore

from pathlib import Path

def _get_s3_resource():
    if S3_KEY and S3_SECRET:
        return boto3.resource(
            's3',
            aws_access_key_id=S3_KEY,
            aws_secret_access_key=S3_SECRET
        )
    else:
        return boto3.resource('s3')


def get_bucket():
    s3_resource = _get_s3_resource()
    if 'bucket' in session:
        bucket = session['bucket']
    else:
        bucket = S3_BUCKET

    return s3_resource.Bucket(bucket)


def get_buckets_list():
    client = boto3.client('s3')
    return client.list_buckets().get('Buckets')

def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def download(key):

    my_bucket = get_bucket()
    #file_obj = my_bucket.Object(key).get()
    s3 = boto3.client('s3', region_name='us-west-2')
    key_dir,key_name = key.split('/')
    #make_sure_path_exists('autopost/static/'+key_dir)
    #s3 = _get_s3_resource()

    #s3 = boto3.client('s3')
    #s3.download_file(BUCKET_NAME, BUCKET_FILE_NAME, LOCAL_FILE_NAME)

    make_sure_path_exists('tmp/'+key_dir)
    local_path = 'tmp/' + key
    print('local_path')
    print(local_path)
    try:
        #s3.Bucket(S3_BUCKET).download_file(key, local_path)
        s3.download_file(S3_BUCKET, key, local_path)
        print('success download')
    except:
        print("The object does not exist.")

    #s3.download_file(S3_BUCKET, key, local_path)
    #local_path = '/autopost/static/' + key
    #local_path_test = '/static/' + key
    local_path_test = '/tmp/' + key
    #local_path_test = key_name
    templateDir = os.path.dirname(__file__)
    key_name_test = os.path.dirname(key_name)
    print('key_name_test')
    print(key_name_test)
    templateDir=templateDir[:-9]
    print('templateDir')
    print(templateDir)
    last_test = templateDir+local_path_test
    print('last_test')
    print(last_test)
    return last_test
    #my_bucket.download_file(S3_BUCKET, 'admin/55b455a0e864370d76da.png', 'admin/55b455a0e864370d76da.png')
