from flask import json,jsonify, render_template,url_for, flash, redirect, request,abort, session,Response
from autopost import app, db, bcrypt
from PIL import Image
import json, facebook
from autopost.forms import AddProject,AddSocial, AdminUserCreateForm, RegistrationForm, LoginForm, UpdateAccountForm, AddTask
from autopost.models import User, Post, Project, Social
from flask_login import login_user, current_user, logout_user,login_required
import os
import secrets
import errno
from datetime import datetime
import shutil
from functools import wraps
from flask_admin import BaseView, expose
import uuid
import boto3
#from autopost.settings import S3_BUCKET,S3_KEY,S3_SECRET
from botocore.exceptions import ClientError
import logging
from autopost.resources import *
from pathlib import Path
from time import sleep
import time
from autopost.test_bot import *

#from autopost import driver
from worker import *
from utils import *

@app.route("/")
@app.route("/home")
def home():
    #user = User.query.all()
    username = current_user.username
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.id.desc()).paginate(page, 10, False)
    return render_template('home.html', user=user, posts=posts)
    #user = User.query.filter_by(email=form.email.data).first()
    #user = User.query.filter_by(username=username).first()
    #page = request.args.get('page', 1,type=int)
    #posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page = 10)
    #return render_template('home.html',posts=posts, user = user)




@app.route("/about")
def about():
    return render_template('about.html', title='About')




@app.route("/add_task", methods=['GET', 'POST'])
@login_required
def add_task():
    form = AddTask()
    if form.validate_on_submit():
        if form.image_file.data:
            file = request.files['image_file']
            nameee = request.files['image_file'].filename
            extensions = Path(nameee).suffixes
            ext = "".join(extensions)
            random_hex = str(secrets.token_hex(10))
            usern = str(current_user.username)
            name_file = usern + "/"+ random_hex + ext

            my_bucket = get_bucket()
            my_bucket.Object(name_file).put(ACL='public-read', Body=file,ContentType ='image/png')

            #file_path = name_file
            #file_path_2 = "https://s3.console.aws.amazon.com/s3/object/autopost-dyploma/" + name_file
            file_path_3 = 'https://dyploma-autopost2.s3-us-west-2.amazonaws.com/' + name_file

        else:
            file_path_3 = "no file"

        post = Post(title = form.title.data, content = form.content.data, \
                    author= current_user, date_posted = form.date_posted.data, \
                    image_file = file_path_3, tags = form.tags.data, \
                    already_posted = form.already_posted.data,\
                    )
        db.session.add(post)
        db.session.commit()
        test_publish = post.title + '\n\n'+ post.content + '\n\n'+post.tags
        #test_publish = post.content
        test = None
        if post.image_file!=None and post.image_file!="no file":
            key = post.image_file
            test = file_path_3
            print(test)
        else:
            test = None

        test_datetime = post.date_posted
        print(test_datetime)

        take_day,take_time = str(test_datetime).split(' ')
        print(take_day)
        print(take_time)

        year,month,day = take_day.split('-')
        print(year)
        print(month)
        print(day)

        hour,minute,seconds = take_time.split(':')
        print(hour)
        print(minute)
        print(seconds)

        job = queue.enqueue_at(datetime(int(year), int(month), int(day), int(hour), int(minute)), facebook_create_post,facebook_login,facebook_password,test_publish,test)
        registry = ScheduledJobRegistry(queue=queue)
        print(job in registry)
        flash('Your task has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_task.html', title='New Task', form = form, legend = 'New task')



@app.route("/add_project", methods=['GET', 'POST'])
@login_required
def add_project():
    form = AddProject()
    if form.validate_on_submit():
        project = Project(name = form.name.data, own_project = current_user)
        db.session.add(project)
        db.session.commit()


        flash('Your task has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_project.html', title='New Project', form = form, legend = 'New project')

@app.route("/add_social", methods=['GET', 'POST'])
@login_required
def add_social():
    form = AddSocial()
    if form.validate_on_submit():
        #type2 = dict(form.type.choices).get(form.type.data)
        #hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        social = Social(login=form.login.data, password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')\
                        ,owner=current_user,type=dict(form.type.choices).get(form.type.data))
        db.session.add(social)
        db.session.commit()
        flash('Your task has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_social.html', title='New social', form = form, legend = 'New social')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form =RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, email = form.email.data, password = hashed_password)

        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created. You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register',form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember = form.remember.data)
            next_page = request.args.get('next')
            return redirect (next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('home'))

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if request.method == "POST" and form.validate():
        user = User.query.filter_by(email=form.email.data).first()

        if bcrypt.check_password_hash(current_user.password, form.passwordcheck.data):
            hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            current_user.password = hashed_password
            current_user.username = form.username.data
            current_user.email = form.email.data
            user.password = hashed_password
            db.session.commit()
            flash('Success. You change your account', 'success')
        else:
            flash('Unsuccess. Please check correct of uor input data', 'danger')
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', title = 'Account', form = form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(user_id=user.id).paginate(page, 20, False)
    return render_template('user.html', user=user, posts=posts.items)

def admin_login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_admin():
            return abort(403)
        return func(*args, **kwargs)
    return decorated_view

@app.route('/admin')
@login_required
@admin_login_required
def home_admin():
    return render_template('index.html')


#@app.route('/loginn')
#def loginn():
#    auth = request.authorization
#    if not auth or not auth.username or not auth.password:
#        return make_response('Coukd not verify', 401, {'WWW-Authenticate':'Basic realm-"Login required"'})
#    user = User.query.filter_by(name = auth.username).first
#    if not user:
#        return make_response('Coukd not verify', 401, {'WWW-Authenticate':'Basic realm-"Login required"'})
#    if chech_password_hash(user.password, auth.password):
#        token = jwt.encode({'public_id':user.id, 'exp': datetime.datetime.utcnow() +
#                            datetime.timedelta(mintes=30)}, app.config['SECRET_KEY'])
#        return jsonify({'token' : token.decode('utf-8')})
#    return make_response('Could not verify', 401, {'WWW-Authenticate':'Basic realm-"Login required"'})

#def token_required(f):
#    @wraps(f)
#    def decorated(*args, **kwargs):
#        token = none
#        if 'x-access-token' in request.headers:
#            token = request.headers['x-access-token']
#            if not token:
#                return jsonify({'message':'Token is missing!'}), 401
#            try:
#               data = jwt.decode(token, app.config['SECRET_KEY'])
#                current_user = User.query.filter_by(id=data['id'].first())
#            except:
#               return jsonify({'message':'Token is invalid!'}), 401
#            return f(current_user,*args,**kwargs)
#    return decorated



@app.route('/post_api', methods=['GET'])
#@token_required
#def get_all_posts(current_user):
def get_all_posts():

    posts = Post.query.all()

    output=[]
    for post in posts :
        post_data = {}
        post_data['title'] = post.title
        post_data['content'] = post.content
        post_data['date_posted'] = post.date_posted
        post_data['image_file'] = post.image_file
        post_data['tags'] = post.tags
        id = post.user_id
        if id !=None:
            user = User.query.filter_by(id=id).first()
            post_data['author'] = user.username
        else: pass
        id = post.project_id
        if id !=None:
            project = Project.query.filter_by(id=id).first()
            post_data['pr_post'] = project.name
        else: pass

        id = post.social_id
        if id !=None:
            social = Social.query.filter_by(id=id).first()
            post_data['soc_type'] = social.type
            post_data['soc_login'] = social.login
            post_data['soc_pass'] = social.password
        else: pass

        output.append(post_data)

    return jsonify({'posts' : output})

@app.route('/post_api/<id>', methods=['GET'])
#@token_required
#def get_one_post(current_user, id):
def get_one_post(id):

    post = Post.query.filter_by(id=id).first()
    if not post:
        return jsonify({'message' : 'No post found'})
    output=[]

    post_data = {}
    post_data['title'] = post.title
    post_data['content'] = post.content
    post_data['date_posted'] = post.date_posted
    post_data['image_file'] = post.image_file
    post_data['tags'] = post.tags
    id = post.user_id
    if id !=None:
        user = User.query.filter_by(id=id).first()
        post_data['author'] = user.username
    else: pass
    id = post.project_id
    if id !=None:
        project = Project.query.filter_by(id=id).first()
        post_data['pr_post'] = project.name
    else: pass

    id = post.social_id
    if id !=None:
        social = Social.query.filter_by(id=id).first()
        post_data['soc_type'] = social.type
        post_data['soc_login'] = social.login
        post_data['soc_pass'] = social.password
    else: pass
    output.append(post_data)
    return jsonify({'post' : output})

@app.route('/post_api', methods=['POST'])
#@token_required
#def create_post(current_user):
def create_post():
    data = request.get_json()

    new_post = Post(title=data['title'],
                    content=data['content'],
                    date_posted=data['date_posted'],
                    image_file=data['image_file'],
                    tags=data['tags'],
                    social_id=data['social_id'],
                    project_id = data['project_id'],
                    user_id = data['user_id'])
    db.session.add(new_post)
    db.session.commit()
    return jsonify({'message': 'New post created'})

@app.route('/post_api/<id>', methods=['PUT'])
#@token_required
#def promote_post(current_user,id):
def promote_post(id):


    post = Post.query.filter_by(id=id).first()

    if not post:
        return jsonify({'message' : 'No post found'})

    post.already_posted = True
    db.session.commit()

    return jsonify({'message' : 'The post has been already posted'})

@app.route('/post_api/<id>', methods=['DELETE'])
#@token_required
#def delete_post(current_user,id):
def delete_post(id):

    post = Post.query.filter_by(id=id).first()

    if not post:
        return jsonify({'message' : 'No usposter found'})

    db.session.delete(post)
    db.session.commit()
    return jsonify({'posts' : 'The post has been deleted'})





#token = {"EAANLMYjSFFABABnUUBynulVVqCVPiMwKU5eF7iI6MWAsTVZBLERZCZCySWtBZCnIDM6TIMuwbxJrlm206y3xAfZAuaufZB5G0tE1LQcq29FkUAFOjyrdKA4do0LrcZCdRTgHqwiII3eGQh1yaByw0WInIOwnWTloUH3MOKb2mDNFNBLeViGYES50E5LZARdOCu8ZD"}
#graph = facebook.GraphAPI(token)

#fb = facebook.GraphAPI(access_token=token)
#fb.put_object(parent_object='105020864533772', connection_name='feed',message = 'tHIS IS a new message' )


#fields = ['id, name','posts']
#profile = fb.get_object('105020864533772',fields=fields)
#print(json.dumps(profile,indent=4))
