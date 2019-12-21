from flask import json,jsonify, render_template,url_for, flash, redirect, request,abort
from autopost import app, db, bcrypt
from PIL import Image
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


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/add_task", methods=['GET', 'POST'])
@login_required
def add_task():
    form = AddTask()
    if form.validate_on_submit():
        post = Post(title = form.title.data, content = form.content.data, \
                    author= current_user, date_posted = form.date_posted.data, \
                    image_file = form.image_file.data, tags = form.tags.data, \
                    already_posted = form.already_posted.data,\
                    )
        db.session.add(post)
        db.session.commit()
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



@app.route('/post_api', methods=['GET'])
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
        #post_data['pr_post'] = post.pr_post
        #post_data['soc'] = post.soc
        #post_data['author'] = post.author
        output.append(post_data)

    return jsonify({'posts' : output})

@app.route('/post_api/<id>', methods=['GET'])
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
    #post_data['pr_post'] = post.pr_post
    #post_data['soc'] = post.soc
    #post_data['author'] = post.author
    output.append(post_data)

    return jsonify({'post' : output})

@app.route('/post_api', methods=['POST'])
def create_post():
    data = request.get_json()

    new_post = Post(title=data['title'], content=data['content'], \
                    date_posted=data['date_posted'], image_file=data['image_file'], \
                    tags=data['tags'], #pr_post=data['pr_post'], \
                    #soc=data['soc'],
                    author=data['author'])
    db.session.add(new_post)
    db.session.commit()
    return jsonify({'message': 'New post created'})

@app.route('/post_api/<id>', methods=['PUT'])
def promote_post(id):
    post = Post.query.filter_by(id=id).first()

    if not post:
        return jsonify({'message' : 'No post found'})

    post.already_posted = True
    db.session.commit()

    return jsonify({'message' : 'The post has been already posted'})

@app.route('/post_api/<id>', methods=['DELETE'])
def delete_post(id):
    post = Post.query.filter_by(id=id).first()

    if not post:
        return jsonify({'message' : 'No usposter found'})

    db.session.delete(post)
    db.session.commit()
    return jsonify({'posts' : 'The post has been deleted'})
