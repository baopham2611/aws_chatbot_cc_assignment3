# ./frontend/application/model/session.py

from flask_login import UserMixin
from werkzeug.security import check_password_hash

class Session(UserMixin):
    def __init__(self, user_id, name, email, role):
        """inits User with data
        Arguments:
            username {str} -- User's username
            password {str} -- User's password
            email {str} -- User's email
            etc..
        """

        self.user_id              =     user_id        
        self.name              =     name                   
        self.email             =     email            
        self.role             =     role 

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.email


    @staticmethod
    def validate_login(password_hash, password):
        """Check if the provided password matches the stored hash."""
        return check_password_hash(password_hash, password)
