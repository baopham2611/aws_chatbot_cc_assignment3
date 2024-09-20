# ./backend/model/users.py
from pydantic import BaseModel
from typing import Optional

class UserResponse(BaseModel):
    user_id: str
    email: str
    user_name: str
    role: str
    # Do not include password here for security

class User(BaseModel):
    user_id: str
    email: str
    user_name: str
    password: str 
    role: str

class UpdateUser(BaseModel):
    user_name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None

class LoginCredentials(BaseModel):
    email: str
    password: str
