from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from os import path
import os 
from flask_login import LoginManager
from datetime import datetime

#initialise sql database for accounts and data storage
db = SQLAlchemy()
migrate = Migrate()
DB_NAME = "database.db"


#initialization of app when run
def create_app():
    app = Flask(__name__, instance_relative_config=True) #had to implement instance checking for creation of database
    #create key for basic encryption
    app.config['SECRET_KEY'] = 'hdoisnduvyenslkspsjfdugbn'
    #allocate db location/name
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, DB_NAME)
    #check path for anyt instances of database creation
    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)
    #initialise the database to the python application
    db.init_app(app)
    #initliaize the migration feature from flask_migrate
    migrate.init_app(app,db)
    
    #import blueprints
    from .views import views
    from .auth import auth

    #register blueprint and set prefixes
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    #register a jinja filter for formatting CSV table output
    app.jinja_env.filters['custom_datetime_format'] = custom_datetime_format

    from .models import User
    create_database(app)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    return app

# check if database already exists/ if not then create it
def create_database(app):
    if not path.exists('website/' + DB_NAME):
        with app.app_context():
            db.create_all()
        print('Created Database.')

#use for table csv output for dattime formatting
def custom_datetime_format(datetime_str):
    # Parse the input datetime string
    input_format = '%Y-%m-%dT%H:%M:%S.%fZ'
    output_format = '%Y-%m-%d'
    
    try:
        datetime_obj = datetime.strptime(datetime_str, input_format)
        formatted_datetime = datetime_obj.strftime(output_format)
        return formatted_datetime
    except ValueError:
        return "Invalid Datetime"
    
def get_color():
    return session.get('color', '#FFFFFF')
