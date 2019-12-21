from datetime import datetime
from autopost import db, login_manager
from flask_login import UserMixin
from hashlib import md5
from flask import Flask, request, jsonify, make_response
import uuid

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    socials = db.relationship('Social', backref='owner', lazy=True)
    posts = db.relationship('Post', backref='author', lazy=True)
    projects = db.relationship('Project', backref='own_project', lazy=True)
    admin = db.Column(db.Boolean())

    def __repr__(self):
        return self.username

    def __init__(self, username, email, password, admin=True):
        self.username = username
        self.email = email
        self.password = password
        self.admin = admin

    def is_admin(self):
        return self.admin


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime)
    content = db.Column(db.Text, nullable=False)
    image_file = db.Column(db.String(100))
    tags = db.Column(db.Text)
    already_posted = db.Column(db.Boolean())
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    social_id = db.Column(db.Integer, db.ForeignKey('social.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    def __repr__(self):
        return self.title


class Social(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    type = db.Column(db.String(30), nullable=False)
    posts = db.relationship('Post', backref='soc', lazy=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    def __repr__(self):
        return self.login +" social: "+ self.type

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    socials = db.relationship('Social', backref='pr_owner', lazy=True)
    posts = db.relationship('Post', backref='pr_post', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    def __repr__(self):
        return self.name


