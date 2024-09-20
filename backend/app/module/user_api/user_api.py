# ./backend/module/user_api.py
from fastapi import APIRouter, HTTPException
from model.users import User, UpdateUser, LoginCredentials, UserResponse
import boto3
from boto3.dynamodb.conditions import Key, Attr
from typing import Optional, List
from fastapi.encoders import jsonable_encoder
import logging
from fastapi import Query
import uuid
from fastapi.responses import JSONResponse

router = APIRouter()

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
login_table = dynamodb.Table('users') 


# Create user
@router.post("/user/create", response_model=UserResponse)
def create_user(user: User):
    # Check if the user already exists by scanning the table for the email
    print("Received data:", user.dict())
    response = login_table.scan(
        FilterExpression=Attr('email').eq(user.email)
    )
    
    if response.get('Items'):
        raise HTTPException(status_code=400, detail="User already exists")


    # Prepare the data to be inserted, including the generated user_id
    user_data = {
        'user_id': user.user_id,
        'email': user.email,
        'user_name': user.user_name,
        'role': user.role,
        'password': user.password  # Not hashing the password as specified
    }

    # Insert the new user into the DynamoDB table
    login_table.put_item(Item=user_data)

    # Return the response with the newly created user details
    return UserResponse(
        user_id=user.user_id,
        email=user.email,
        user_name=user.user_name,
        role=user.role
    )



# Update user by user_id
@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: str, user: UpdateUser):
    # Fetch the user from the table based on user_id
    response = login_table.get_item(Key={'user_id': user_id})

    # Ensure the user exists
    if 'Item' not in response:
        raise HTTPException(status_code=404, detail="User not found")

    updated_data = response['Item']

    # Update only the fields provided in the request
    user_data = user.dict(exclude_unset=True)  # Get only the fields that are provided
    updated_data.update(user_data)  # Update the existing user data with the new data

    # Put the updated data back into the table
    login_table.put_item(Item=updated_data)

    return UserResponse(
        user_id=updated_data['user_id'],
        email=updated_data['email'],
        user_name=updated_data['user_name'],
        role=updated_data['role']
    )




@router.post("/register/", response_model=UserResponse)
def register_user(user: User):
    try:
        # Check if the user already exists by scanning the table for the email
        response = login_table.scan(
            FilterExpression=Attr('email').eq(user.email)
        )
        
        if response.get('Items'):
            return JSONResponse(status_code=400, content={"message": "User with this email already exists"})

        # If the user doesn't exist, add them to the table
        login_table.put_item(
            Item={
                'user_id': user.user_id,  # Use the user_id passed from frontend
                'email': user.email,
                'user_name': user.user_name,
                'role': user.role,  # Fixed: user.role to match the model
                'password': user.password  # Not hashing the password as per the original design
            }
        )

        # Return the response without password for security reasons
        return UserResponse(
            user_id=user.user_id,
            email=user.email,
            user_name=user.user_name,
            role=user.role
        )

    except Exception as e:
        logging.error(f"Error in register_user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")



    
    
def get_user_id_from_email(email: str) -> str:
    """
    Fetch user_id from the 'users' table based on the email address.
    Assumes there is a GSI for email named 'EmailIndex'.
    """
    try:
        response = login_table.query(
            IndexName='EmailIndex',  # This should be set on your DynamoDB 'login' table if you're querying by email
            KeyConditionExpression=Key('email').eq(email)
        )
        if not response['Items']:
            raise HTTPException(status_code=404, detail="User not found")

        # Assuming the user_id is stored in the 'user_id' field
        return response['Items'][0]['user_id']
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user ID: {str(e)}")



    

# Login
@router.post("/login/", response_model=UserResponse)
def login_user(credentials: LoginCredentials):
    email = credentials.email
    password = credentials.password
    try:
        response = login_table.query(
            IndexName='EmailIndex',
            KeyConditionExpression=Key('email').eq(email)
        )
        if not response['Items']:
            raise HTTPException(status_code=404, detail="User not found")

        user = response['Items'][0]
        if user['password'] != password:
            raise HTTPException(status_code=401, detail="Invalid password")

        return UserResponse(email=user['email'], user_name=user['user_name'], role=user['role'], user_id=user['user_id'])
    except Exception as e:
        logging.error(f"Error during login: {e}")
        raise HTTPException(status_code=500, detail=f"Error during login: {str(e)}")



# Get all users
@router.get("/users/", response_model=List[User])
def get_all_users():
    print(f"Accessing DynamoDB Table: {login_table.name} in Region: {dynamodb.meta}")
    try:
        response = login_table.scan()
        users = response.get('Items', [])
        return [User(**user) for user in users]
    except Exception as e:
        error_msg = f"Error accessing DynamoDB: {str(e)}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)



# Get user by email
@router.get("/users/{email}", response_model=User)
def read_user(email: str):
    response = login_table.get_item(Key={'email': email})
    if 'Item' not in response:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**response['Item'])




# Delete user
@router.delete("/users/{email}", response_model=dict)
def delete_user(email: str):
    response = login_table.get_item(Key={'email': email})
    if 'Item' not in response:
        raise HTTPException(status_code=404, detail="User not found")
    login_table.delete_item(Key={'email': email})
    return {"message": "User deleted successfully"}



@router.get("/users/{email}", response_model=User)
def get_user_by_email(email: str):
    response = login_table.get_item(Key={'email': email})
    if 'Item' not in response:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**response['Item'])


