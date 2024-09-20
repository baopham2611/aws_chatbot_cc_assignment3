# ./frontend/application/api_user.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, current_app
# from flask_login import login_required, current_user, logout_user
# from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import check_password_hash
from .model.users import User  
from .model.sessions import Session 
import requests
import uuid


# Blueprint Configuration
user_api = Blueprint("user_api", __name__)
base_url = current_app.config['BASE_BACKEND_URL']



@user_api.route('/user/add', methods=['POST'])
@login_required
def insert_user():
    ''' Add new user by admin '''
    if request.method == "POST":
        # Get form data
        name = request.form['fullname']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        # Generate a unique user_id
        user_id = str(uuid.uuid4())

        # Define the API endpoint and headers
        api_url_create_user = f"{base_url}/user/create"
        headers_create_user = {'Content-Type': 'application/json'}
        
        # Prepare payload with generated user_id
        payload_create_user = {
            'user_id': user_id,  # Add generated user_id to the payload
            'email': email,
            'password': password,
            'user_name': name,
            'role': role
        }
        print(payload_create_user)  # Print the payload for debugging

        # Send POST request to the backend
        response_create_user = requests.post(api_url_create_user, json=payload_create_user, headers=headers_create_user)

        # Check the response and handle accordingly
        if response_create_user.status_code == 200:
            flash("New User Inserted Successfully", 'success')
        elif response_create_user.status_code == 400:
            flash(response_create_user.json().get('detail', 'User already exists'), 'danger')
        else:
            flash("Error adding user. Please try again.", 'danger')

        # Redirect to the previous page
        return redirect(request.referrer)




# Update user data - Admin role
@user_api.route('/user/update', methods=['POST'])
@login_required
def update_user():
    ''' Admin update user '''
    
    # Set the new data
    user_id = request.form['id']  # Assuming the form sends user_id
    name = request.form['fullname']
    password = request.form['password']
    email = request.form['email']
    role = request.form['role']

    # Fix the API URL to point to the correct user_id endpoint
    api_url_update_user = f"{base_url}/users/{user_id}"  # Use user_id instead of email
    headers_update_user = {'Content-Type': 'application/json'}
    payload_update_user = {
        'email': email,
        'password': password,
        'user_name': name,
        'role': role
    }

    # Make the PUT request to update the user
    response_update_user = requests.put(api_url_update_user, json=payload_update_user, headers=headers_update_user)

    if response_update_user.status_code == 200:
        flash("User updated successfully", 'success')
    else:
        flash("Error updating user", 'danger')

    return redirect(request.referrer)

    


@user_api.route('/home', methods=['GET'])
@login_required
def show_favorites():
    user_email = current_user.email  # Assuming you have access to the logged-in user's email
    base_url = current_app.config['BASE_BACKEND_URL']
    api_url = f"{base_url}/favorites/"
    response = requests.get(api_url, params={'user_email': user_email})

    if response.status_code == 200:
        favorite_musics = response.json()
    else:
        flash('Failed to fetch favorites')
        favorite_musics = []

    return render_template('screen/favorites.html', favorite_musics=favorite_musics)



@user_api.route('/admin/users/all/<int:page_num>', methods=['GET'])
@login_required
def get_users_admin(page_num):
    api_url = f"{base_url}/users/all/"
    headers = {'Content-Type': 'application/json'}

    per_page = request.args.get('per_page', 10, type=int)

    response = requests.get(api_url, headers=headers, params={'page': page_num, 'per_page': per_page})
    if response.ok:
        data = response.json()
        users = data['users']
        # print(f"users ---------> {users}")
        total = data['total']
    else:
        flash('Failed to fetch users')
        users = []
        total = 0

    return render_template('admin/user_handler_admin.html', users=users, page=page_num, per_page=per_page, total=total)


    


@user_api.route('/users/delete/<int:user_id>', methods=['GET'])
@login_required
async def delete_role(user_api):
    """ Endpoint to delete a role by an Admin """
    print("role_id: ",user_api)
    api_url = f"{base_url}/roles/delete/{user_api}"
    headers = {'Content-Type': 'application/json'}
    
    response = requests.delete(api_url, headers=headers)
    if response.status_code == 200:
        flash('User deletion successful')
    else:
        flash('User deletion failed')

    return redirect(request.referrer)
