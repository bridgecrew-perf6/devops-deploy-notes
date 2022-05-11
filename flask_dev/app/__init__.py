from flask import Flask
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy
from app.config import Config
from redis import Redis
from rq import Queue, Worker, Connection
import click

# redis instace
redis = Redis(host="cache", port=6379)
redis_queue = Queue("default", connection=redis)
redis_queue_hi = Queue("high", connection=redis)
redis_queue_lo = Queue("low", connection=redis)

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    initialize_extensions(app)
    initialize_blueprints(app)
    register_commands(app)
    return app

def initialize_extensions(app):
    db.init_app(app)

def initialize_blueprints(app):
    from app.views import view
    app.register_blueprint(view)

def register_commands(app):
    app.cli.add_command(init_db)
    app.cli.add_command(seed_db)
    app.cli.add_command(rqworkers)

# Command that needs to be called to initialize database
@click.command(name='init_db')
@with_appcontext
def init_db():
    # you need to import/load in models to initialize the database
    from app.models import User
    db.drop_all()
    db.create_all()
    db.session.commit()

# Command that needs to be called to populate database
@click.command(name='seed_db')
@with_appcontext
def seed_db():
    from app.models import User
    db.session.add(User(email="michael@mherman.org"))
    db.session.commit()

# Command that needs to be called to intialize all RQ workers
@click.command(name='rqworkers')
@with_appcontext
def rqworkers():
    worker_names = ["high", "default", "low"]
    with Connection(redis):
        worker = Worker(list(map(Queue, worker_names)))
        worker.work()
