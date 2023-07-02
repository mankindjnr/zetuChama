from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, Manager, Chamas
from flask_login import login_user, logout_user, login_required, current_user
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/auth/member/login', methods=['GET'])
def member_login():
    return render_template('member_login.html')

@auth.route('/auth/member/login', methods=['POST'])
def member_login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    username = request.form.get('username')
    remember = True if request.form.get('remember') else False

    user  = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.member_login')) # if user doesn't exist or password is wrong, reload the page

    login_user(user, remember=remember)
    return redirect(url_for('main.member_from_db', mem_id=current_user.id))




@auth.route("/auth/manager/login", methods=['GET'])
def manager_login():
    return render_template('manager_login.html')

@auth.route('/auth/manager/login', methods=['POST'])
def manager_login_post():
    # login code goes here
    email = request.form.get('email')
    password = request.form.get('password')
    username = request.form.get('username')
    remember = True if request.form.get('remember') else False

    manager  = Manager.query.filter_by(email=email).first()

    if not manager or not check_password_hash(manager.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.manager_login'))
        
    login_user(manager, remember=remember)

    user_name = current_user.username
    return redirect(url_for('main.manager_from_db', user_name=user_name))





@auth.route('/auth/signup', methods=['GET'])
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    # code to validate and add user to database goes here
    email = request.form.get('email')
    name = request.form.get('name')
    username = request.form.get('username')
    password = request.form.get('password')

    # if this returns a user, then the email already exists in database
    user = User.query.filter_by(email=email).first()

    if user: # if a user is found, we want to redirect back to signup page so user can try again    
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))

    # create a new user with the form data. Hash the password so plaintext version isn't saved. 
    new_user = User(email=email, name=name, username=username, password=generate_password_hash(password, method='sha256'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.member_login'))

@auth.route('/auth/manager/signup', methods=['GET'])
def manager_signup():
    return render_template('manager_signup.html')

@auth.route('/auth/manager/signup', methods=['POST'])
def manager_signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    username = request.form.get('username')
    password = request.form.get('password')

    manager = Manager.query.filter_by(username=username).first()

    if manager:
        flash('Username already exists')
        return redirect(url_for('auth.manager_signup'))

    new_manager = Manager(email=email, name=name, username=username, password=generate_password_hash(password, method='sha256'))

    db.session.add(new_manager)
    db.session.commit()

    return redirect(url_for('auth.manager_login'))

    
@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))
