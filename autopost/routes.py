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
    if current_user.is_authenticated:
        username = current_user.username
        user = User.query.filter_by(username=username).first_or_404()
        page = request.args.get('page', 1, type=int)
        posts = Post.query.filter_by(user_id=user.id).order_by(Post.date_posted.desc()).paginate(page, 10, False)
        return render_template('home.html', user=user, posts=posts)
    else:
        return render_template('home_dev.html')


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
        date_test = str(form.date_posted.data)
        time_test = str(form.time_posted.data)
        time_te = time_test[11:]
        year,month,day = date_test.split('-')
        hour_ser,minute,seconds = time_te.split(':')
        date_posted2 = datetime(int(year), int(month), int(day), int(hour_ser), int(minute))

        post = Post(title = form.title.data, content = form.content.data, \
                    author= current_user, date_posted = date_posted2, \
                    image_file = file_path_3, tags = form.tags.data, \
                    already_posted=False
                    )
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
        test_datetime = post.date_posted
        take_day,take_time = str(test_datetime).split(' ')
        year,month,day = date_test.split('-')
        hour_ser,minute,seconds = take_time.split(':')
        hour = int(hour_ser) - 3
        if hour<0:
            hour=24+hour


        job = queue.enqueue_at(datetime(int(year), int(month), int(day), hour, int(minute)), facebook_create_post,facebook_login,facebook_password,test_publish,test)
        registry = ScheduledJobRegistry(queue=queue)
        print(job in registry)
        print('Job id: %s' % job.id)
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
    #posts = Post.query.filter_by(user_id = user.id).all()
    #sneed_socials2 = Social.query.join(association_table).join(Post).filter((association_table.c.social_id ==Social.id) &(association_table.c.post_id ==Post.id) )
    #query_user_role = User.query.join(roles_users).join(Role).
    #filter((roles_users.c.user_id == User.id) & (roles_users.c.role_id == Role.id)).all()

    print(sneed_socials2)
    form.socials.default = ['1']
    form.process()


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

        else:
            file_path_3 = "no file"
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
        db.session.commit()

        soc = form.socials.data
        for elem in soc:
            test_int = int(str(elem))
            print(test_int)
            post.socials.append(Social.query.get(test_int))
            print('maybe success')
            db.session.commit()

        flash('Your task hes been updated!', 'success')
        return redirect(url_for('home'))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        form.date_posted.data = post.date_posted
        form.time_posted.data = post.date_posted
        form.image_file.data = post.image_file
        form.tags.data = post.tags
        form.image_file_url.data = post.image_file



    return render_template('update_task.html', title='Update Task' , form  = form, legend = 'Update Task',post = post)

@app.route("/post/<int:post_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_task(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post hes been deleted!', 'success')
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
