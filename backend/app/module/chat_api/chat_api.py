# ./backend/app/module/chat_api/chat_api.py
from fastapi import APIRouter, HTTPException, Request, Query
from boto3.dynamodb.conditions import Attr
from module.chat_api.pdf_processor import get_pdf_text_from_s3
from utils import query_bedrock_model
import uuid
import boto3
from datetime import datetime

router = APIRouter()

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
conversations_table = dynamodb.Table('conversations')

# S3 bucket name
bucket_name = "aws-cloud-computing"



@router.get('/api/conversations')
async def get_conversations(user_id: str = Query(...)):
    try:
        # Filter conversations by user_id
        response = conversations_table.scan(
            FilterExpression=Attr('user_id').eq(user_id),  # Only fetch conversations for the given user_id
            ProjectionExpression="conversation_id, #ts, message",
            ExpressionAttributeNames={"#ts": "timestamp"}
        )
        
        conversations = response.get('Items', [])

        # Dictionary to hold the latest message for each conversation
        latest_conversations = {}

        for conv in conversations:
            conv_id = conv.get('conversation_id')
            conv_timestamp = conv.get('timestamp')
            conv_message = conv.get('message', '')  # Default to empty string if no message

            # Ensure the conversation has the necessary fields
            if conv_id and conv_timestamp:
                try:
                    # Parse timestamp into datetime object for comparison
                    conv_time_obj = datetime.fromisoformat(conv_timestamp)
                    
                    # Only keep the latest message based on the timestamp
                    if (conv_id not in latest_conversations or
                        datetime.fromisoformat(latest_conversations[conv_id]['timestamp']) < conv_time_obj):
                        latest_conversations[conv_id] = {
                            "conversation_id": conv_id,
                            "timestamp": conv_timestamp,
                            "message": conv_message
                        }
                except ValueError:
                    print(f"Invalid timestamp format for conversation: {conv_id}, skipping...")

        # Return the latest message for each conversation
        result = [
            {
                "conversation_id": conv['conversation_id'],
                "timestamp": conv['timestamp'],
                "message": conv['message'][:30] + '...' if len(conv['message']) > 30 else conv['message']  # Truncate the message
            } for conv in latest_conversations.values()
        ]

        print(f"Conversations with latest messages for user {user_id}: {result}")  # For debugging

        return {"conversations": result}

    except Exception as e:
        print(f"Error fetching conversations for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching conversations for user {user_id}")



@router.post('/api/chat')
async def chatbot(request: Request):
    # Parse JSON data from the request body
    data = await request.json()
    user_input = data.get('message')
    conversation_id = data.get('conversation_id', None)  # Get or generate conversation ID
    user_id = data.get('user_id')
    user_role = data.get('role')
    print(f"User input: {user_input}, conversation_id: {conversation_id}, user_role: {user_role}")

    # If no conversation ID exists, create a new one
    if not conversation_id:
        conversation_id = str(uuid.uuid4())  # Generate a unique conversation ID
    
    # Store the user message in DynamoDB
    store_conversation(conversation_id, user_id, user_input, sender='User')

    # Extract text from a PDF based on user input (if needed)
    extracted_text = ""

    if "techcombank account" in user_input.lower():
        pdf_key = "techcombank_pdfs/Chi_tiet_cac_loai_tai_khoan_Techcombank_5dce5e2f0e_48a1d2549e.pdf"
        extracted_text = get_pdf_text_from_s3(bucket_name, pdf_key)
    elif "techcombank guide" in user_input.lower():
        pdf_key = "techcombank_pdfs/HDSD-FEB-APPROVED-18032022-203995d63a-b53721b8d4.pdf"
        extracted_text = get_pdf_text_from_s3(bucket_name, pdf_key)
    elif "techcombank loyal customers service" in user_input.lower():
        pdf_key = "techcombank_pdfs/DS phong giao dich Techcombank.pdf"
        extracted_text = get_pdf_text_from_s3(bucket_name, pdf_key)
    elif "techcombank fees" in user_input.lower():
        pdf_key = "techcombank_pdfs/vn-phu-luc-bieu-phi-dich-vu-the-tin-dung-kh-thuong.pdf"
        extracted_text = get_pdf_text_from_s3(bucket_name, pdf_key)
    elif "techcombank address" in user_input.lower():
        pdf_key = "techcombank_pdfs/DS phong giao dich Techcombank.pdf"
        extracted_text = get_pdf_text_from_s3(bucket_name, pdf_key)
    elif "techcombank annual report" in user_input.lower():
        if user_role == 'customer':
            ai_response = "Sorry, this is company credential, customer cannot be able to know about this."
            store_conversation(conversation_id, user_id, ai_response, 'Bot')
            return {
                "answer": ai_response,
                "conversation_id": conversation_id  # Return conversation ID for tracking
            }
        else:
            pdf_key = "techcombank_pdfs/Annual_report_2014_805941a588.pdf"
            extracted_text = get_pdf_text_from_s3(bucket_name, pdf_key)
    elif "techcombank business secret" in user_input.lower():
        if user_role == 'customer':
            ai_response = "Sorry, this is company credential, customer cannot be able to know about this."
            store_conversation(conversation_id, user_id, ai_response, 'Bot')
            return {
                "answer": ai_response,
                "conversation_id": conversation_id  # Return conversation ID for tracking
            }
        else:
            print("Checking Annual_report_2014_805941a588")
            pdf_key = "techcombank_pdfs/Annual_report_2014_805941a588.pdf"
            extracted_text = get_pdf_text_from_s3(bucket_name, pdf_key)


    
 

    # Combine user input and extracted text for the prompt
    full_input = user_input if not extracted_text else f"{user_input}\n\n{extracted_text}"

    # Use the Claude model ID
    model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"

    # Query the generative model and get the response
    ai_response = query_bedrock_model(model_id, full_input)

    # Store the bot response in DynamoDB
    store_conversation(conversation_id,user_id, ai_response, 'Bot')

    print(f"ai_response: {ai_response}")

    # Return the AI's response and conversation ID
    return {
        "answer": ai_response,
        "conversation_id": conversation_id  # Return conversation ID for tracking
    }


def store_conversation(conversation_id, user_id, message, sender):
    """
    Store each message (both from the user and bot) into the DynamoDB 'conversations' table.
    Each conversation is tied to the user's ID (user_id).
    """
    timestamp = datetime.utcnow().isoformat()  # Store the current time in ISO format

    # Add the message and user ID to the DynamoDB table
    conversations_table.put_item(
        Item={
            'conversation_id': conversation_id,
            'user_id': user_id,  # Store the user ID
            'timestamp': timestamp,
            'message': message,
            'sender': sender
        }
    )





@router.get('/api/conversations/{conversation_id}')
async def get_conversation_messages(conversation_id: str):
    # Query for all messages with the specified conversation_id
    response = conversations_table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key('conversation_id').eq(conversation_id)
    )
    
    messages = response.get('Items', [])
    return {"messages": messages}
