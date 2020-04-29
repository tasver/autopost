from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import SelectField, widgets, DateTimeField, StringField, PasswordField, SubmitField, BooleanField,TextAreaField
from wtforms.validators import InputRequired, DataRequired, Length, Email, EqualTo, ValidationError
from autopost.models import User, Post, Project, Social
from flask import flash, redirect, url_for, Markup

from flask_ckeditor import CKEditorField

from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose, AdminIndexView
from flask_admin.form import rules
from autopost import bcrypt


class RegistrationForm(FlaskForm):
    username=StringField('Username', validators=[DataRequired(),Length(min=2,max=20)])
    email=StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password',validators = [DataRequired()])
    confirm_password = PasswordField('Confirm Password',validators = [DataRequired(), EqualTo('password')])
    submit= SubmitField('Sign up')
    def validate_field(self,field):
        if True:
            raise ValidationError('Validation message')
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one')
    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

class LoginForm(FlaskForm):
    email =StringField('Email', validators = [DataRequired(),Email()])
    password = PasswordField('Password',validators = [DataRequired()])
    remember = BooleanField('Remember Me')
    submit= SubmitField('Log in')

class UpdateAccountForm(FlaskForm):
    username=StringField('Username', validators=[DataRequired(),Length(min=2,max=20)])
    email=StringField('Email', validators=[DataRequired(),Email()])
    submit= SubmitField('Update')
    new_password = PasswordField('New password',validators = [DataRequired()])
    passwordcheck = PasswordField('Old password',validators = [DataRequired()])
    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one')
    def validate_email(self,email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

class AddTask(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    date_posted = DateTimeField('Date Posted', format='%Y-%m-%d %H:%M')
    image_file = FileField('Choose picture', validators=[FileAllowed(['jpg','png'])])
    tags = TextAreaField('Tags')
    already_posted = BooleanField('Already Posted?')
    #project_id = SelectField('Select project', choices=Project.name)

    #social_id = db.Column(db.Integer, db.ForeignKey('social.id'))
    #user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    submit = SubmitField('Add task')

class AddProject(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    #social_id = db.Column(db.Integer, db.ForeignKey('social.id'))
    #user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    submit = SubmitField('Add Project')

class AddSocial(FlaskForm):
    login = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Password',validators = [DataRequired()])
    #type = StringField('Type', validators=[DataRequired()])
    type = SelectField(u'Type', choices=[('Instagram', 'Instagram'),\
                           ('Facebook', 'Facebook'), ('Twitter', 'Twitter')])

    #project_id = SelectField('Select project', choices=Project.name)

    #user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    submit = SubmitField('Add task')


class AdminUserCreateForm(FlaskForm):
    username = StringField('Username', [InputRequired()])
    password = PasswordField('Password', [InputRequired()])
    admin = BooleanField('Is Admin ?')
    posts = StringField('Posts', [InputRequired()])
class AdminUserUpdateForm(FlaskForm):
    username = StringField('Username', [InputRequired()])
    admin = BooleanField('Is Admin ?')


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

class CKTextAreaWidget(widgets.TextArea):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('class_', 'ckeditor')
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)

class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget()

class UserAdminView(ModelView):
    column_searchable_list = ('username',)
    column_sortable_list = ('username', 'admin')
    #form_overrides = dict(about=CKEditorField)
    create_template = 'create.html'
    edit_template = 'edit.html'
    #column_exclude_list = ('password',)
    #form_excluded_columns = ('password',)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def scaffold_form(self):
        form_class = super(UserAdminView, self).scaffold_form()
        form_class.new_password = PasswordField('New Password')
        form_class.confirm = PasswordField('Confirm New Password')
        return form_class

    def create_model(self, form):
        model = self.model(
            form.username.data, form.password.data, form.admin.data
        )
        form.populate_obj(model)
        model.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        self.session.add(model)
        self._on_model_change(form, model, True)
        self.session.commit()
        return redirect(url_for('home_admin'))


    def update_model(self, form, model):
        form.populate_obj(model)
        if form.new_password.data:
            if form.new_password.data != form.confirm.data:
                return flash('Passwords must match')
            model.password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
        self.session.add(model)
        self._on_model_change(form, model, False)
        self.session.commit()
        return redirect(url_for('home_admin'))

class PostAdminView(ModelView):
    column_searchable_list = ('title',)
    column_sortable_list = ('title', 'already_posted','date_posted')
    details_template = 'details.html'

    can_view_details = True
    column_details_list = ('type','login','socials')
    #form_overrides = dict(about=CKEditorField)
    create_template = 'create.html'
    edit_template = 'edit.html'

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()


class ProjectAdminView(ModelView):
    column_searchable_list = ('name',)
    create_template = 'create.html'
    edit_template = 'edit.html'
    details_template = 'details.html'
    can_view_details = True
    column_details_list = ('name','socials','posts')
    def _get_list_value(self, context, model, name, column_formatters,
                    column_type_formatters):
        """
            Returns the value to be displayed.

            :param context:
                :py:class:`jinja2.runtime.Context` if available
            :param model:
                Model instance
            :param name:
                Field name
            :param column_formatters:
                column_formatters to be used.
            :param column_type_formatters:
                column_type_formatters to be used.
        """
        column_fmt = column_formatters.get(name)
        if column_fmt is not None:
            value = column_fmt(self, context, model, name)
        else:
            value = self._get_field_value(model, name)

        choices_map = self._column_choices_map.get(name, {})
        if choices_map:
            return choices_map.get(value) or value

        type_fmt = None
        for typeobj, formatter in column_type_formatters.items():
            if isinstance(value, typeobj):
                type_fmt = formatter
                break
        if type_fmt is not None:
            value = type_fmt(self, value)
        ### overwritten here
        if name == 'socials':

            html_string  = '<ul>'
            for item in value.split(','):
                html_string += '<li> {} </li>'.format(item)
            html_string += '</ul>'

            value = Markup(html_string)

        elif name == 'posts':

            html_string  = '<table>'
            for item in value.split(','):
                html_string += '<tr><td> {} </td></tr>'.format(item)
            html_string += '</table>'

            value = Markup(html_string)

        return value

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()


class SocialAdminView(ModelView):
    column_searchable_list = ('login',)
    create_template = 'create.html'
    edit_template = 'edit.html'
    details_template = 'details.html'
    can_view_details = True
    column_details_list = ('type','login','posts')
    #column_exclude_list = ('password',)
    #form_excluded_columns = ('password',)
    form_overrides = dict(
        type=SelectField
    )
    form_args = dict(
        type=dict(
            choices=[('Instagram', 'Instagram'),\
                           ('Facebook', 'Facebook'), ('Twitter', 'Twitter')]
        )
    )

    def _get_list_value(self, context, model, name, column_formatters,
                    column_type_formatters):
        """
            Returns the value to be displayed.

            :param context:
                :py:class:`jinja2.runtime.Context` if available
            :param model:
                Model instance
            :param name:
                Field name
            :param column_formatters:
                column_formatters to be used.
            :param column_type_formatters:
                column_type_formatters to be used.
        """
        column_fmt = column_formatters.get(name)
        if column_fmt is not None:
            value = column_fmt(self, context, model, name)
        else:
            value = self._get_field_value(model, name)

        choices_map = self._column_choices_map.get(name, {})
        if choices_map:
            return choices_map.get(value) or value

        type_fmt = None
        for typeobj, formatter in column_type_formatters.items():
            if isinstance(value, typeobj):
                type_fmt = formatter
                break
        if type_fmt is not None:
            value = type_fmt(self, value)
        ### overwritten here
        if name == 'posts':

            html_string  = '<table>'
            for item in value.split(','):
                html_string += '<tr><td> {} </td></tr>'.format(item)
            html_string += '</table>'

            value = Markup(html_string)

        return value




    def create_model(self, form):

        model = self.model(
            login = form.login.data, password = form.password.data, \
            type=dict(form.type.choices).get(form.type.data)
        )
        form.populate_obj(model)
        model.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        self.session.add(model)
        self._on_model_change(form, model, True)
        self.session.commit()
        return redirect(url_for('home_admin'))

    def update_model(self, form, model):
        form.populate_obj(model)
        if form.password.data:
            model.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        self.session.add(model)
        self._on_model_change(form, model, False)
        self.session.commit()
        return redirect(url_for('home_admin'))


    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

