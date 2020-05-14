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

    def __init__(self, username, email, password, admin=False):
        self.username = username
        self.email = email
        self.password = password
        self.admin = admin

    def is_admin(self):
        return self.admin

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    socials = db.relationship('Social', backref='pr_owner', lazy=True)
    posts = db.relationship('Post', backref='pr_post', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    def __repr__(self):
        return self.name




association_table = db.Table('association_table', db.Model.metadata,
    db.Column('Socials_id', db.Integer, db.ForeignKey('socials.id',ondelete="CASCADE"),primary_key=True),
    db.Column('Post_id', db.Integer, db.ForeignKey('posts.id',ondelete="CASCADE"),primary_key=True),
    db.UniqueConstraint('Socials_id', 'Post_id', name='UC_social_id_post_id')
)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime)
    content = db.Column(db.Text, nullable=False)
    image_file = db.Column(db.String(100))
    tags = db.Column(db.Text)
    already_posted = db.Column(db.Boolean())
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    job_id = db.Column(db.Text)
    link_post = db.Column(db.Text)
    notes = db.Column(db.Boolean())

    __tablename__ = 'posts'
    socials = db.relationship('Social', secondary = association_table,back_populates='posts',  lazy='dynamic')
    #social_id = db.Column(db.Integer, db.ForeignKey('social.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return self.title

class Social(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    type = db.Column(db.String(30), nullable=False)
    __tablename__ = 'socials'
    posts = db.relationship('Post', secondary=association_table,back_populates='socials', lazy='dynamic')
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    def __repr__(self):
        return self.login +" social: "+ self.type

