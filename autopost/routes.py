from flask import json,jsonify, render_template,url_for, flash, redirect, request,abort
from autopost import app, db, bcrypt
from PIL import Image
from autopost.forms import AdminUserUpdateForm, AdminUserCreateForm, RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from autopost.models import User, Post
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


@app.route('/userr', methods=['GET'])
def get_all_users():
    users = User.query.all()

    output=[]

    for user in users :
        user_data = {}
        user_data['username'] = user.username
        user_data['email'] = user.email
        if type(user.password)== str:
            user_data['password'] = user.password
        else:
            user_data['password'] = user.password.decode('utf-8')
        user_data['admin'] = user.admin
        output.append(user_data)

    return jsonify({'users' : output})

@app.route('/userr/<id>', methods=['GET'])
def get_one_user(id):
    user = User.query.filter_by(id=id).first()

    if not user:
        return jsonify({'message' : 'No user found'})

    user_data = {}
    user_data['username'] = user.username
    user_data['email'] = user.email
    user_data['password'] = user.password.decode('utf-8')
    user_data['admin'] = user.admin
    return jsonify({'user':user_data})

@app.route('/userr', methods=['POST'])
def create_user():
    data = request.get_json()

    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')

    new_user = User(username=data['username'], email=data['email'], \
                    password = hashed_password, admin=False)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'New user created'})

@app.route('/userr/<id>', methods=['PUT'])
def promote_user(id):
    user = User.query.filter_by(id=id).first()

    if not user:
        return jsonify({'message' : 'No user found'})

    user.admin = True
    db.session.commit()

    return jsonify({'message' : 'The user has been promoted'})

@app.route('/userr/<id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.filter_by(id=id).first()

    if not user:
        return jsonify({'message' : 'No user found'})

    db.session.delete(user)
    db.session.commit()
    return jsonify({'users' : 'The user has been deleted'})
