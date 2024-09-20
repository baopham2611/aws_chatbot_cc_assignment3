# ./frontend/application/homesite.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, current_app
# from flask_login import login_required, current_user, logout_user
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import check_password_hash
from .model.users import User  
from .model.sessions import Session 
import requests
import bcrypt
import uuid

# Blueprint Configuration
site = Blueprint("site", __name__)
base_url = current_app.config['BASE_BACKEND_URL']



@site.route('/register', methods=['GET', 'POST'])
def registerPage():
    if request.method == 'POST':
        # Generate a unique user_id
        user_id = str(uuid.uuid4())  # Generate the user_id on the frontend
        email = request.form['email']
        user_name = request.form['user_name']
        password = request.form['password']
        role = 'customer'  # Default role

        # URL of the external API
        api_url = f"{current_app.config['BASE_BACKEND_URL']}/register/"
        headers = {'Content-Type': 'application/json'}
        payload = {
            'user_id': user_id,  # Include generated user_id
            'email': email,
            'password': password,
            'user_name': user_name,
            'role': role
        }
        print("Sending payload to backend:", payload)  # Debugging print to check payload

        # Make the POST request
        response = requests.post(api_url, json=payload, headers=headers)

        if response.status_code == 200:
            user_data = response.json()
            session['logged_in'] = True
            user = User(
                name=user_data['user_name'],
                email=user_data['email'],
                password=password,  # Save un-hashed password for login
                user_id=user_data['user_id'],
                role=user_data['role']
            )
            session['name'] = user_data['user_name']
            session['email'] = email
            session['role'] = user_data['role']
            session['user_id'] = user_data['user_id']
            login_user(user)

            return redirect(url_for('site.homePage'))
        else:
            flash('Registration failed. Please try again.')
            return redirect(url_for('site.registerPage'))

    return render_template('auth/register.html')



@site.route('/home/', methods=['GET'])
@login_required
def homePage():
    ''' Show user's favorite music with pagination '''
    user_email = current_user.email
    api_url = f"{base_url}/users/"
    headers = {'Content-Type': 'application/json'}

    # Get pagination parameters
    page_num = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Request the user's favorite music with pagination parameters
    response = requests.get(api_url, headers=headers, params={'user_email': user_email, 'page': page_num, 'per_page': per_page})
    if response.ok:
        data = response.json()
        users = data
        # print(users)
        total = len(data)
        current_role=current_user.role
        print(f"current_role: {current_role}")
        if current_role == 'admin':
            return render_template('controllers/user_handler.html', users=users, page=page_num, per_page=per_page, total=total)
        elif current_role == 'customer':
            return redirect(url_for('chat_api.base'))
        elif current_role == 'staff':
            return render_template('controllers/user_handler.html', users=users, page=page_num, per_page=per_page, total=total)
    else:
        flash('Failed')
        total = 0

    


# Welcome page
@site.route('/')
async def index():
    """Display Index page

    Returns:
        .html -- The Index page of the web application
    """
    if current_user.is_authenticated:
        return redirect(url_for('site.homePage'))
    else:
        return render_template('auth/index.html')


# Login page
@site.route('/login', methods=['GET', 'POST'])
def loginPage():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # URL of the external API
        api_url = f"{current_app.config['BASE_BACKEND_URL']}/login/"
        headers = {'Content-Type': 'application/json'}
        payload = {'email': email, 'password': password}

        # Make the POST request
        response = requests.post(api_url, json=payload, headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            print(user_data)
            session['logged_in'] = True
            user = User(name=user_data['user_name'], email=user_data['email'], password= password, role=user_data['role'], user_id=user_data['user_id'])
            # Assuming login_user is defined to handle user sessions
            session['name'] = user_data['user_name']
            session['email'] = email
            session['role'] = user_data['role']
            session['user_id'] = user_data['user_id']
            login_user(user)

            return redirect(url_for('site.homePage'))
        else:
            flash('Login failed. Please check your credentials.')
            return redirect(url_for('site.loginPage'))

    return render_template('auth/login.html')
    
    
    
# Endpoint to logout
@site.route('/logout')
@login_required
async def logout():

    # Remove the user ID from the session if it is there
    # Logout user clear _id of the session
    logout_user()
    session.clear()

    return redirect(url_for('site.index'))
