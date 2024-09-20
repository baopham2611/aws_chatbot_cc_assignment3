# ./frontend/application/api_chat.py
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_user, current_user, logout_user, login_required
import requests

# Create the Blueprint for the home site
chat_api = Blueprint('chat_api', __name__)



# API route to handle fetching conversation history
@chat_api.route('/api/conversations', methods=['GET'])  # We want a GET request here, not POST
@login_required
def get_historical_data():
    try:
        user_id = current_user.user_id  # Get the user_id of the logged-in user
        
        # Call backend (FastAPI) on localhost port 8000
        api_gateway_url = f"http://localhost:8000/api/conversations?user_id={user_id}"
        
        # Send GET request to the backend API to get conversation history for the user_id
        response = requests.get(api_gateway_url)
        
        # If the backend returns a status code other than 200, raise an error
        if response.status_code != 200:
            return jsonify({"error": f"Failed to fetch conversations from backend. Status code: {response.status_code}"}), 500
        
        # Parse the JSON response from the backend
        conversation_data = response.json()
        print(f"Conversations fetched for user {user_id}: {conversation_data}")
        
        # Return the conversation data to the frontend
        return jsonify(conversation_data)
    
    except requests.exceptions.RequestException as e:
        print(f"Error while fetching conversations for user {user_id}: {e}")
        return jsonify({"error": f"Unable to fetch conversations for user {user_id} from backend"}), 500

    


    
# Home route to render the HTML template
@chat_api.route('/chat/')
def base():
    user_id = current_user.user_id
    user_role = current_user.role
    print(user_id)
    print(user_role)
    return render_template('/controllers/chat_page.html')

# API route to handle chatbot interactions
@chat_api.route('/api/chat', methods=['POST'])
def chatbot():
    user_message = request.json.get('message')
    conversation_id = request.json.get('conversation_id', None)  # Get conversation ID if available
    print(f"user_message: {user_message}, conversation_id: {conversation_id}")

    # Use local backend running on port 8000
    api_gateway_url = "http://localhost:8000/api/chat"

    # Send the user's message and conversation_id to the local backend
    user_id = current_user.user_id
    user_role = current_user.role
    print(user_id)
    response = requests.post(api_gateway_url, json={'message': user_message, 'conversation_id': conversation_id, 'user_id': user_id, 'role': user_role})
    response_data = response.json()
    print(f"backend_response: {response_data}")
    
    # Return the chatbot's response to the frontend
    return jsonify({
        'answer': response_data.get('answer'),
        'conversation_id': response_data.get('conversation_id')  # Pass conversation_id back if it's created
    })

    



# API route to handle fetching conversation chat history by conversation_id
@chat_api.route('/api/conversations/<conversation_id>', methods=['GET'])
def get_conversation_chat(conversation_id):
    try:
        # Backend FastAPI URL to get conversation messages
        api_gateway_url = f"http://localhost:8000/api/conversations/{conversation_id}"
        
        # Send GET request to the backend API to fetch the messages for a specific conversation
        response = requests.get(api_gateway_url)
        
        # If the backend returns a status code other than 200, raise an error
        if response.status_code != 200:
            return jsonify({"error": f"Failed to fetch messages from backend. Status code: {response.status_code}"}), 500
        
        # Parse the JSON response from the backend
        messages_data = response.json()
        print(f"Messages fetched for conversation {conversation_id}: {messages_data}")
        
        # Return the messages data to the frontend
        return jsonify(messages_data)
    
    except requests.exceptions.RequestException as e:
        print(f"Error while fetching messages for conversation {conversation_id}: {e}")
        return jsonify({"error": f"Unable to fetch messages for conversation {conversation_id} from backend"}), 500
