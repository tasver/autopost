import click
from flask.cli import with_appcontext

from flaskblog import db
from flaskblog.models import User, Post

@click.command(name = 'create_tables')
@with_appcontext
def create_tables():
    db.create_all()

@click.group()
def cli():
    pass

@click.command(name='create_admin')
@with_appcontext
def create_admin():
    click.echo('Hello! Run command ok before')
    username = "admin"
    admin = True
    email = "admib@gmail.com"
    password = "admin"
    u = User(username=username, admin=admin, email=email, password=password)
    #print("superadmin created", u)
    db.session.add(u)
    db.session.commit()
    click.echo("superadmin created!!!")

cli.add_command(create_tables)
cli.add_command(create_admin)


if __name__ == '__main__':
    cli()
