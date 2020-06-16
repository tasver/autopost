from flask import json,jsonify, render_template,url_for, flash, redirect, request,abort, session,Response
from autopost import app, db, bcrypt
from PIL import Image
import json, facebook
from autopost.forms import *
from autopost.models import User, Post, Project, Social
from flask_login import login_user, current_user, logout_user,login_required
import os
import secrets
import errno
from datetime import datetime
import shutil
from functools import wraps
import re
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
from wtforms.utils import unset_value

from autopost import driver
from worker import *
from utils import *

@app.route("/")
@app.route("/home")
def home():
    if current_user.is_authenticated:
        username = current_user.username
        user = User.query.filter_by(username=username).first_or_404()
        page = request.args.get('page', 1, type=int)
        posts = Post.query.filter_by(user_id=user.id).filter_by(notes=False).order_by(Post.date_posted.desc()).paginate(page, 10, False)
        return render_template('home.html', user=user, posts=posts)
    else:
        return render_template('home_dev.html')

@app.route("/notes")
def notes():
    if current_user.is_authenticated:
        username = current_user.username
        user = User.query.filter_by(username=username).first_or_404()
        page = request.args.get('page', 1, type=int)
        posts = Post.query.filter_by(user_id=user.id).filter_by(notes=True).order_by(Post.date_posted.desc()).paginate(page, 10, False)
        return render_template('notes.html', user=user, posts=posts)
    else:
        return redirect(url_for('home'))


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

            file_path_3 = 'https://dyploma-autopost2.s3-us-west-2.amazonaws.com/' + name_file

        else:
            file_path_3 = "no file"
        date_posted2 = None

        post = Post(title = form.title.data, content = form.content.data, \
                    author= current_user, date_posted = date_posted2, \
                    image_file = file_path_3, tags = form.tags.data, \
                    already_posted=False,notes= form.notes.data
                    )



        if form.date_posted.data:
            date_test = str(form.date_posted.data)
            year,month,day = date_test.split('-')
            hour_ser = 0
            minute = 0
            date_posted2 = datetime(int(year), int(month), int(day), int(hour_ser), int(minute))
            post.date_posted=date_posted2

        if form.time_posted.data:
            time_test = str(form.time_posted.data)
            time_te = time_test[11:]
            hour_ser,minute,seconds = time_te.split(':')
            year = 2020
            month = 1
            day = 1
            date_posted2 = datetime(int(year), int(month), int(day), int(hour_ser), int(minute))
            post.date_posted=date_posted2

        if form.date_posted.data and form.time_posted.data:
            date_test = str(form.date_posted.data)
            time_test = str(form.time_posted.data)
            time_te = time_test[11:]
            year,month,day = date_test.split('-')
            hour_ser,minute,seconds = time_te.split(':')
            date_posted2 = datetime(int(year), int(month), int(day), int(hour_ser), int(minute))
            post.date_posted=date_posted2

        if not form.time_posted.data or not form.date_posted.data:
            post.notes=True


        db.session.add(post)
        db.session.commit()
        test_publish = post.title + '\n\n'+ post.content + '\n\n'+post.tags
        test = None
        if post.image_file!=None and post.image_file!="no file":
            key = post.image_file
            test = file_path_3
            print(test)
        else:
            test = None
        flash('Your task has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_task.html', title='New Task', form = form, legend = 'New task')


"""
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
"""
@app.route("/add_social", methods=['GET', 'POST'])
@login_required
def add_social():
    form = AddSocial()
    if form.validate_on_submit():
        #type2 = dict(form.type.choices).get(form.type.data)
        #hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        social = Social(login=form.login.data, password=form.password.data\
                        ,owner=current_user,type=dict(form.type.choices).get(form.type.data))
        db.session.add(social)
        db.session.commit()
        flash('Your task has been created!', 'success')
        return redirect(url_for('socials'))
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
            flash('Unsuccess. Please check correct of yuor input data', 'danger')
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', title = 'Account', form = form)

"""
@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(user_id=user.id).paginate(page, 20, False)
    return render_template('user.html', user=user, posts=posts.items)
"""
def admin_login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_admin():
            return abort(403)
        return func(*args, **kwargs)
    return decorated_view


def get_res(job, post):
    #time.sleep(120)
    result_job = job.result
    tessstid = post.job_id
    post.job_id = str(tessstid) +  str(job.id)
    lennnnk = post.link_post
    post.link_post = str(lennnnk) + str(result_job)
    #return str(result_job)

@app.route("/task/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_task(post_id):

    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    user = current_user
    need_socials = Social.query.filter_by(user_id = user.id).all()
    socials_list = [(i.id, i.login +"|"+ i.type ) for i in need_socials]
    form = AddTask(obj=user)
    choo_noth = [(0,None)] + socials_list
    form.socials.choices = choo_noth

    if request.method == 'POST' and form.validate_on_submit():

        sommm = post.socials
        for elem in sommm:
            print(elem)
            post.socials.remove(elem)
            elem.posts.remove(post)
        db.session.commit()

        file_path = post.image_file

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

            file_path_3 = 'https://dyploma-autopost2.s3-us-west-2.amazonaws.com/' + name_file

        else:
            file_path_3 = file_path
        date_test = str(form.date_posted.data)
        time_test = str(form.time_posted.data)
        time_te = time_test[11:]
        year,month,day = date_test.split('-')
        hour_ser,minute,seconds = time_te.split(':')
        date_posted2 = datetime(int(year), int(month), int(day), int(hour_ser), int(minute))
        post.title = form.title.data
        post.content = form.content.data
        post.date_posted = date_posted2
        post.image_file = file_path_3
        post.tags = form.tags.data
        soc = form.socials.data


        for elem in soc:
            test_int = int(str(elem))
            elem_soc = Social.query.get(test_int)
            print(elem_soc)
            print(test_int)
            if test_int != 0:
                post.socials.append(elem_soc)
                print('maybe success')
                db.session.commit()
            elif test_int ==0:
                sommm = post.socials
                for elem in sommm:
                    print(elem)
                    post.socials.remove(elem)
                    elem.posts.remove(post)
                #elem_soc.posts.remove(post)
                #post.socials.remove(elem_soc)
                #elem_soc.posts.remove(post)
                db.session.commit()
                print("valu = 0")
            else:
                #flash('Your can not choose nothing', 'danger')
                print("not value")


        db.session.commit()
        flash('Your task has been updated!', 'success')
        return redirect(url_for('home'))

    elif request.method == 'GET':
        test_default = []
        teeeeest_post = Post.query.filter_by(id = post.id).all()
        print(teeeeest_post)
        #len_soc = len(post.socials)
        #if len_soc>0:
            #print(post.socials)
        for elem in post.socials:
            tmp_default = str(elem.id)
            test_default.append(tmp_default)
        print(test_default)
        if len(test_default)>0:
            form.socials.default = test_default
            form.process()

        form.title.data = post.title
        form.content.data = post.content
        form.date_posted.data = post.date_posted
        form.time_posted.data = post.date_posted
        form.image_file.data = post.image_file
        form.tags.data = post.tags
        form.image_file_url.data = post.image_file


    return render_template('update_task.html', title='Update Task' , form  = form, legend = 'Update Task',post = post)

@app.route("/note/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_note(post_id):

    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    user = current_user
    need_socials = Social.query.filter_by(user_id = user.id).all()
    socials_list = [(i.id, i.login +"|"+ i.type ) for i in need_socials]
    form = AddTask(obj=user)
    choo_noth = [(0,None)] + socials_list
    form.socials.choices = choo_noth

    if request.method == 'POST' and form.validate_on_submit():

        sommm = post.socials
        for elem in sommm:
            print(elem)
            post.socials.remove(elem)
            elem.posts.remove(post)
        db.session.commit()

        file_path = post.image_file

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

            file_path_3 = 'https://dyploma-autopost2.s3-us-west-2.amazonaws.com/' + name_file
            post.image_file = file_path_3
        else:
            file_path_3 = file_path
            post.image_file = file_path_3

        if form.date_posted.data and form.time_posted.data:
            date_test = str(form.date_posted.data)
            time_test = str(form.time_posted.data)
            time_te = time_test[11:]
            year,month,day = date_test.split('-')
            hour_ser,minute,seconds = time_te.split(':')
            date_posted2 = datetime(int(year), int(month), int(day), int(hour_ser), int(minute))
            post.date_posted = date_posted2
        if form.date_posted.data:
            date_test = str(form.date_posted.data)
            year,month,day = date_test.split('-')
            hour_ser = 0
            minute = 0
            date_posted2 = datetime(int(year), int(month), int(day), int(hour_ser), int(minute))
            post.date_posted = date_posted2
        if form.time_posted.data:
            time_test = str(form.time_posted.data)
            time_te = time_test[11:]
            hour_ser,minute,seconds = time_te.split(':')
            year = 2020
            month = 1
            day = 1
            date_posted2 = datetime(int(year), int(month), int(day), int(hour_ser), int(minute))
            post.date_posted = date_posted2

        if form.title.data:
            post.title = form.title.data
        if form.content.data:
            post.content = form.content.data
        if form.tags.data:
            post.tags = form.tags.data

        soc = form.socials.data

        for elem in soc:
            test_int = int(str(elem))
            elem_soc = Social.query.get(test_int)
            print(elem_soc)
            print(test_int)
            if test_int != 0:
                post.socials.append(elem_soc)
                print('maybe success')
                db.session.commit()
            elif test_int ==0:
                sommm = post.socials
                for elem in sommm:
                    print(elem)
                    post.socials.remove(elem)
                    elem.posts.remove(post)
                #elem_soc.posts.remove(post)
                #post.socials.remove(elem_soc)
                #elem_soc.posts.remove(post)
                db.session.commit()
                print("valu = 0")
            else:
                #flash('Your can not choose nothing', 'danger')
                print("not value")

        db.session.commit()
        flash('Your note has been updated!', 'success')
        return redirect(url_for('notes'))

    elif request.method == 'GET':
        test_default = []
        teeeeest_post = Post.query.filter_by(id = post.id).all()
        print(teeeeest_post)
        #len_soc = len(post.socials)
        #if len_soc>0:
            #print(post.socials)
        for elem in post.socials:
            tmp_default = str(elem.id)
            test_default.append(tmp_default)
        print(test_default)
        if len(test_default)>0:
            form.socials.default = test_default
            form.process()

        form.title.data = post.title
        form.content.data = post.content
        form.date_posted.data = post.date_posted
        form.time_posted.data = post.date_posted
        form.image_file.data = post.image_file
        form.tags.data = post.tags
        form.image_file_url.data = post.image_file


    return render_template('update_note.html', title='Update Task' , form  = form, legend = 'Update Task',post = post)

@app.route("/note/<int:post_id>/add_to_task", methods=['GET', 'POST'])
@login_required
def add_to_task(post_id):
    if current_user.is_authenticated:
        post = Post.query.get_or_404(post_id)
        if post.author != current_user:
            abort(403)


        if post.date_posted:
            post.notes = False
            db.session.commit()
            flash('You add a new task from note!', 'success')
            return redirect(url_for('home'))
        else:
            flash('You did no choose datetime!', 'danger')
            return redirect(url_for('notes'))
    else:
        pass
    return redirect(url_for('notes'))

@app.route("/task/<int:post_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_task(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))

@app.route("/note/<int:post_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_note(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your note has been deleted!', 'success')
    return redirect(url_for('notes'))


@app.route("/socials")
def socials():
    if current_user.is_authenticated:
        username = current_user.username
        user = User.query.filter_by(username=username).first_or_404()
        page = request.args.get('page', 1, type=int)
        socials = Social.query.filter_by(user_id=user.id).order_by(Social.id.desc()).paginate(page, 5, False)
        return render_template('socials.html', user=user, socials=socials)
    else:
        return redirect(url_for('home'))


@app.route("/social/<int:social_id>/update", methods=['GET', 'POST'])
@login_required
def update_social(social_id):
    social = Social.query.get_or_404(social_id)
    form = UpdateSocial()
    if request.method == 'POST' and form.validate_on_submit():
        if social.password == form.passwordcheck.data:
            #hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            social.password = form.new_password.data
            social.login = form.login.data
            db.session.commit()
            flash('Success. You change your social account', 'success')
        else:
            flash('Unsuccess. Please check correct of yuor input data', 'danger')
        return redirect(url_for('socials'))
    elif request.method == 'GET':
        form.login.data = social.login
        #form.type.choices
    return render_template('update_social.html', title='Update Social account' , form  = form, legend = 'Update Social account',social = social)

@app.route("/social/<int:social_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_social(social_id):
    social = Social.query.get_or_404(social_id)
    if social.owner != current_user:
        abort(403)
    #postsss = Post.query.all()
    #for post in postsss:
    #def remove_tag(tag_id):
    #tag = Tag.query.get(tag_id)
    #for post in social.posts:
    #    p = Post.query.get(post.id)
    #    p.socials.remove(social)
        #post.socials.remove(social)
        #social.posts.remove()

    db.session.delete(social)
    db.session.commit()
    flash('Your social has been deleted!', 'success')
    return redirect(url_for('socials'))

@app.route("/post/<int:post_id>/publish", methods=['GET', 'POST'])
@login_required
def publish_task(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)

    test_publish = post.title + '\n\n'+ post.content + '\n\n'+post.tags
    test = None
    if post.image_file!=None and post.image_file!="no file":
        #key = post.image_file
        test = post.image_file
        print(test)
    else:
        test = None

    test_datetime = post.date_posted
    take_day,take_time = str(test_datetime).split(' ')
    year,month,day = take_day.split('-')
    hour_ser,minute,seconds = take_time.split(':')
    hour = int(hour_ser) - 3
    if hour<0:
        hour=24+hour


    tmp = 0
    for soc in post.socials:
        tmp = tmp+1

    if tmp>0:
        for soc in post.socials:
            if soc.type =='Facebook':
                print('its facebook')
                #url = facebook_create_post(soc.login,soc.password,test_publish,test)
                job = queue.enqueue(facebook_create_post,soc.login,soc.password,test_publish,test,result_ttl=-1)
                post.job_id = str(post.job_id) + str(job.id)
                #print(job)
                #time.sleep(2)
                    #job2 = queue.enqueue_at(datetime(int(year), int(month), int(day), hour, int(minute)),get_res,job,post)
                #result_job = job.result
                #print("result job")
                #print(result_job)
                #alr_posts = str(post.link_post)
                #facebook_url = "facebook: " + url + " "
                #post.link_post = alr_posts + facebook_url
                #print(alr_posts + facebook_url)
                print('success')
                print(soc)
                #print(url)
            if soc.type =='Instagram':
                alr_posts = str(post.link_post)
                url = 'test'
                instagram_url = "instagram: " + url + " "
                post.link_post = alr_posts + instagram_url
                print(alr_posts + instagram_url)
                print('its instagram')
            if soc.type =='Twitter':
                url="test"
                alr_posts = str(post.link_post)
                twitter_url = "twitter: " + url + " "
                post.link_post = alr_posts + twitter_url
                print(alr_posts + twitter_url)
                print('its twitter')
        post.already_posted = True
        flash('Your post will be publish now!', 'success')
    else:
        post.already_posted = False
        flash('Your post not publish now, please choose your social!', 'danger')

    #job = queue.enqueue_at(datetime(int(year), int(month), int(day), hour, int(minute)), facebook_create_post,facebook_login,facebook_password,test_publish,test)
    #registry = ScheduledJobRegistry(queue=queue)
    #print(job in registry)
    #print('Job id: %s' % job.id)

    db.session.commit()

    return redirect(url_for('home'))

@app.route("/post/<int:post_id>/addqueue", methods=['GET', 'POST'])
@login_required
def add_to_queue_task(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    test_publish = post.title + '\n\n'+ post.content + '\n\n'+post.tags
    test = None
    if post.image_file!=None and post.image_file!="no file":
        #key = post.image_file
        test = post.image_file
        print(test)
    else:
        test = None

    test_datetime = post.date_posted
    take_day,take_time = str(test_datetime).split(' ')
    year,month,day = take_day.split('-')
    hour_ser,minute,seconds = take_time.split(':')
    hour = int(hour_ser) - 3
    if hour<0:
        hour=24+hour

    tmp = 0
    for soc in post.socials:
        tmp = tmp+1

    if tmp>0:
        for soc in post.socials:
            if soc.type =='Facebook':
                print('its facebook')
                #url = facebook_create_post(soc.login,soc.password,test_publish,test)
                job = queue.enqueue_at(datetime(int(year), int(month), int(day), hour, int(minute)), facebook_create_post,soc.login,soc.password,test_publish,test,result_ttl=-1)
                registry = ScheduledJobRegistry(queue=queue)
                print(job in registry)
                #print('Job id: %s' % job.id)
                post.job_id = str(post.job_id) + str(job.id)
                #time.sleep(2)
                    #job2 = queue.enqueue_at(datetime(int(year), int(month), int(day), hour, int(minute)),get_res,job,post)
                #result_job = job.result
                #print("result job")
                #print(result_job)
                #post.job_id = str(job)
                #alr_posts = str(post.link_post)
                #facebook_url = "facebook: " + url + " "
                #post.link_post = alr_posts + facebook_url
                #print(alr_posts + facebook_url)
                print('success')
                print(soc)
                #print(url)
            if soc.type =='Instagram':
                alr_posts = str(post.link_post)
                url = 'test'
                instagram_url = "instagram: " + url + " "
                post.link_post = alr_posts + instagram_url
                print(alr_posts + instagram_url)
                print('its instagram')
            if soc.type =='Twitter':
                url="test"
                alr_posts = str(post.link_post)
                twitter_url = "twitter: " + url + " "
                post.link_post = alr_posts + twitter_url
                print(alr_posts + twitter_url)
                print('its twitter')
        post.already_posted = True
    else:
        post.already_posted = False
        flash('Your post not publish now, please choose your social!', 'danger')
    db.session.commit()
    flash('Your post will add to queue!', 'success')
    return redirect(url_for('home'))

@app.route("/post/<int:post_id>/go_to_post")
def go_to_post(post_id):
    if current_user.is_authenticated:

        post = Post.query.get_or_404(post_id)
        if post.author != current_user:
            abort(403)
        tmp = 0
        for soc in post.socials:
            print(soc)
            tmp = tmp+1
        tmp2 = tmp
        #print(post.socials)
        #posts = posts2.paginate(page, 10, False)
        if tmp == 0:
            flash('You has no post on Facebook', 'danger')
            return redirect(url_for('home'))

        if post.job_id!=None:
            teeeeeeest = post.link_post

            test_job = post.job_id
            print('test_job')
            print(test_job)

            job_id_len = len(str(test_job)) / tmp
            print(str(test_job))
            print(job_id_len)
            job_id_len = int(job_id_len)
            job_id_len_test = test_job[:job_id_len]
            print(job_id_len_test)
            test_url_list = ''
            link_post_test_old = ''
            n = 0
            while tmp>0:
                try:
                    test_url = test_job[n:job_id_len]
                    job = queue.fetch_job(test_url)
                    print(job)
                    link_post_test = job.result
                    print(link_post_test)

                    test_url_list = str(link_post_test_old) + str(" ") + str(link_post_test)

                    print(test_url_list)
                    n = n+job_id_len
                    job_id_len = job_id_len+job_id_len
                    tmp=tmp-1
                    link_post_test_old = test_url_list
                    print(test_url_list)
                    post.link_post = test_url_list
                    db.session.commit()
                except:
                    print("no one links")
                    flash('no one links', 'danger')
                    return redirect(url_for('home'))


            #post.job_id = None




        url = post.link_post
        url_len = len(str(url)) / tmp2
        print(str(url))
        print(url_len)
        url_len = int(url_len)
        test_url = url[:url_len]
        print(test_url)
        test_url_list = []
        n = 0
        while tmp2>0:
            try:
                test_url = url[n:url_len]
                #test_url_list.append(test_url)
                test_url_list = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', url)
                n = n+url_len
                url_len = url_len+url_len
                tmp2=tmp2-1
            except:
                print("no one links")

        print(test_url_list)

        #posts = Post.query.filter_by(user_id=user.id).filter_by(notes=False).order_by(Post.date_posted.desc()).paginate(page, 10, False)
        return render_template('go_to_post.html', post=post,test_url_list=test_url_list)
    else:
        return redirect(url_for('home'))

@app.route("/post/<int:post_id>/<int:url_count>/delete_post_on_social")
def delete_post_on_social(post_id,url_count):
    if current_user.is_authenticated:
        post = Post.query.get_or_404(post_id)
        if post.author != current_user:
            abort(403)
        tmp = 0
        for soc in post.socials:
            print(soc)
            if tmp == url_count:
                soc_del = soc
                social_log = soc.login
                print(social_log)
                social_pas = soc.password
                print(social_pas)
            tmp = tmp+1
        url = post.link_post
        print(url)
        url_len = len(str(url)) / tmp
        url_len = int(url_len)
        print('urllen')
        print(url_len)
        test_url = url[:url_len]
        test_url_list = []
        n = 0
        while tmp>0:
            try:
                test_url = url[n:url_len]
                test_url_list.append(test_url)
                n = n+url_len
                url_len = url_len+url_len
                tmp=tmp-1
            except:
                print("no one links")
        print(test_url_list)
        need_url = test_url_list[url_count]
        print(need_url)
        job = queue.enqueue(facebook_delete_post,social_log,social_pas,need_url)
        test_url_list.remove(need_url)

        str1 = ""
        for ele in test_url_list:
            str1 += ele
        print("str1:")
        print(str1)
        post.link_post = str1
        post.socials.remove(soc_del)
        db.session.commit()
        flash('Your post on facebook will be deleted', 'success')

        return redirect(url_for('home'))
    return redirect(url_for('home'))

"""
@app.route("/projects")
def projects():
    if current_user.is_authenticated:
        username = current_user.username
        user = User.query.filter_by(username=username).first_or_404()
        page = request.args.get('page', 1, type=int)
        projects = Project.query.filter_by(user_id=user.id).order_by(Project.id.desc()).paginate(page, 1, False)

        return render_template('projects.html', user=user, projects=projects)
    else:
        return redirect(url_for('home'))

@app.route("/project/<int:project_id>/update", methods=['GET', 'POST'])
@login_required
def update_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.own_project != current_user:
        abort(403)
    return render_template('update_project.html', title='Update Project' ,  legend = 'Update Project',project= project)


@app.route("/project/<int:project_id>/update", methods=['GET', 'POST'])
@login_required
def update_project(project_id):
    form = ProjectAdminView()
    
    project = Project.query.get_or_404(project_id)
    user = current_user
    post = Post.query.filter_by(user_id=user.id).order_by(Post.id.desc())
    user = User.query.filter_by(email=form.email.data).first()
    if post.author != current_user:
        abort(403)
    if project.own_project != current_user:
        abort(403)

    if request.method == 'POST' and form.validate_on_submit():
        project.name = form.name.data
        db.session.commit()
        flash('Your project hes been updated!', 'success')
        return redirect(url_for('home'))
    elif request.method == 'GET':
        form.name.data = project.name

        form.title.data = post.title
        form.content.data = post.content

        form.nickname.data = post.date_posted

    return render_template('update_task.html', title='Update Task' , form  = form, legend = 'Update Task',post = post)

@app.route("/project/<int:project_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.own_project != current_user:
        abort(403)
    db.session.delete(project)
    db.session.commit()
    flash('Your project hes been deleted!', 'success')
    return redirect(url_for('projects'))

"""
"""
@app.route("/notes")
def notes():
    if current_user.is_authenticated:
        username = current_user.username
        user = User.query.filter_by(username=username).first_or_404()
        page = request.args.get('page', 1, type=int)
        posts = Post.query.filter_by(user_id=user.id).filter(Post.title.like('%(notesss)')).filter(Post.content.like('%(notesss)')).order_by(Post.id.desc()).paginate(page, 10, False)

        return render_template('notes.html', user=user, posts=posts)
    else:
        return redirect(url_for('home'))


@app.route("/add_note", methods=['GET', 'POST'])
@login_required
def add_note():
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

            file_path_3 = 'https://dyploma-autopost2.s3-us-west-2.amazonaws.com/' + name_file

        else:
            file_path_3 = "no file"
        date_test = str(form.date_posted.data)
        time_test = str(form.time_posted.data)
        time_te = time_test[11:]
        year,month,day = date_test.split('-')
        hour_ser,minute,seconds = time_te.split(':')
        date_posted2 = datetime(int(year), int(month), int(day), int(hour_ser), int(minute))

        post = Post(title = form.title.data + "(notesss)", content = form.content.data + "(notesss)", \
                    author= current_user, date_posted = date_posted2, \
                    image_file = file_path_3, tags = form.tags.data, \
                    already_posted=False
                    )
        db.session.add(post)
        db.session.commit()

        flash('Your notes has been created!', 'success')
        return redirect(url_for('notes'))
    return render_template('add_notes.html', title='New Notes', form = form, legend = 'New notes')

@app.route("/notes/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_notes(post_id):
    form = NotesTask()
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)

    if request.method == 'POST' and form.validate_on_submit():
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

            file_path_3 = 'https://dyploma-autopost2.s3-us-west-2.amazonaws.com/' + name_file
            post.image_file = file_path_3
        else:
            file_path_3 = "no file"
            post.image_file = file_path_3

        if form.date_posted.data:
            date_test = str(form.date_posted.data)
            time_test = str(form.time_posted.data)
            time_te = time_test[11:]
            year,month,day = date_test.split('-')
            hour_ser,minute,seconds = time_te.split(':')
            date_posted2 = datetime(int(year), int(month), int(day), int(hour_ser), int(minute))
            post.date_posted = date_posted2
        if form.title.data:
            post.title = form.title.data
        if form.content.data:
            post.content = form.content.data
        if form.tags.data:
            post.tags = form.tags.data
        db.session.commit()
        flash('Your task hes been updated!', 'success')
        return redirect(url_for('notes'))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        form.date_posted.data = post.date_posted
        form.time_posted.data = post.date_posted
        form.image_file.data = post.image_file
        form.tags.data = post.tags
        form.image_file_url.data = post.image_file
    return render_template('update_task.html', title='Update Notes' , form  = form, legend = 'Update Notes',post = post)

@app.route("/notes/<int:post_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_notes(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your notes hes been deleted!', 'success')
    return redirect(url_for('notes'))
"""
@app.route('/admin')
@login_required
@admin_login_required
def home_admin():
    return render_template('index.html')

"""
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
"""
