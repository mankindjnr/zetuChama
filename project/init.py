from flask import Flask, request, render_template, jsonify
import requests
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import pymysql
from .config import my_secrets

# initializing sql-alchemy so we can use it later in our models
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = my_secrets.get('database_2')
    app.config['SQLALCHEMY_DATABASE_URI'] = my_secrets.get('database_2')
    db.init_app(app)

    #mpesa
    BASE_URL = 'https://sandbox.safaricom.co.ke'
    CONSUMER_KEY = my_secrets.get('consumer_key')
    CONSUMER_SECRET = my_secrets.get('consumer_secret')

    ACCESS_TOKEN_URL = '{}/oauth/v1/generate?grant_type=client_credentials'.format(BASE_URL)
    C2B_REGISTER_URL = '{}/mpesa/c2b/v1/registerurl'.format(BASE_URL)
    C2B_SIMULATE_URL = '{}/mpesa/c2b/v1/simulate'.format(BASE_URL)

    #a function to obtain access token from MPESA API
    def get_access_token():
        response = requests.get(ACCESS_TOKEN_URL, auth=(CONSUMER_KEY, CONSUMER_SECRET))
        access_token = response.json()["access_token"]
        return access_token
    
    #a functions to reggister te C2B URL with MPESA API
    def register_c2b_url():
        access_token = get_access_token()
        headers = {"Authorization": "Bearer {}".format(access_token)}
        data = {
            "ResponseType": "Completed",
            "ConfirmationURL": "https://chama-zetu.onrender.com/confirmation",
            "ValidationURL": "https://chama-zetu.onrender.com/validation"
        }
        response = requests.post(C2B_REGISTER_URL, json=data, headers=headers)
        return response.text
    
    #simulate transaction
    def simulate_c2b_transaction(amount, msisdn, reference):
        access_token = get_access_token()
        headers = {"Authorization": "Bearer {}".format(access_token)}
        data = {
            "CommandID": "CustomerPayBillOnline",
            "Amount": amount,
            "Msisdn": msisdn,
            "BillRefNumber": reference
        }
        response = requests.post(C2B_SIMULATE_URL, json=data, headers=headers)
        return response.text
    
    

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    # tells flask-login how to load a user given the id
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

