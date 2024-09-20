import boto3
from boto3.dynamodb.conditions import Key
import pandas as pd
import json
import requests
from io import BytesIO
import uuid  # Import UUID library to generate unique IDs
from datetime import datetime


def initialize_aws_services():
    """Initialize and return AWS DynamoDB and S3 clients."""
    dynamodb = boto3.resource('dynamodb')
    s3 = boto3.client('s3')
    return dynamodb, s3


def table_exists(dynamodb, table_name):
    """Check if a DynamoDB table exists."""
    try:
        dynamodb.Table(table_name).load()
        return True
    except dynamodb.meta.client.exceptions.ResourceNotFoundException:
        return False


def create_table(dynamodb, table_name, key_schema, attribute_definitions, provisioned_throughput, gsi=None):
    """Create a DynamoDB table if it does not already exist."""
    if not table_exists(dynamodb, table_name):
        params = {
            'TableName': table_name,
            'KeySchema': key_schema,
            'AttributeDefinitions': attribute_definitions,
            'ProvisionedThroughput': provisioned_throughput
        }
        if gsi:
            params['GlobalSecondaryIndexes'] = gsi
        table = dynamodb.create_table(**params)
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        print(f'{table_name} table created.')
        return table
    else:
        print(f'{table_name} table already exists.')
        return dynamodb.Table(table_name)


def load_data_to_dynamodb(dynamodb, table_name, data):
    """Load data into a DynamoDB table using batch writer, checking for duplicates."""
    table = dynamodb.Table(table_name)
    with table.batch_writer() as batch:
        for item in data:
            if table_name == 'users':
                item_key = 'user_id'
            response = table.query(KeyConditionExpression=Key(item_key).eq(item[item_key]))
            if response['Count'] == 0:
                batch.put_item(Item=item)
    print(f"Data has been inserted into {table_name}.")


def initialize_conversation(dynamodb):
    """Initialize a new conversation in DynamoDB and return the conversation ID."""
    conversation_table = dynamodb.Table('conversations')

    # Generate unique conversation_id
    conversation_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()

    # Store the initial conversation record in DynamoDB
    conversation_table.put_item(
        Item={
            'conversation_id': conversation_id,
            'timestamp': timestamp,
            'message': 'Conversation initiated',
            'sender': 'System'
        }
    )

    print(f"New conversation initiated with ID: {conversation_id}")
    return conversation_id


def main():
    """Main function to orchestrate the AWS operations."""
    dynamodb, s3 = initialize_aws_services()

    # Create 'users' table with GSI for email querying
    email_index = {
        'IndexName': 'EmailIndex',
        'KeySchema': [{'AttributeName': 'email', 'KeyType': 'HASH'}],
        'Projection': {'ProjectionType': 'ALL'},
        'ProvisionedThroughput': {'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
    }
    create_table(dynamodb, 'users',
                 [{'AttributeName': 'user_id', 'KeyType': 'HASH'}],
                 [{'AttributeName': 'user_id', 'AttributeType': 'S'}, {'AttributeName': 'email', 'AttributeType': 'S'}],
                 {'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1},
                 gsi=[email_index])

    # Load data using UUIDs
    file_path = 'login.csv'
    login_data = pd.read_csv(file_path, delimiter=',')
    formatted_login_data = [{'user_id': str(uuid.uuid4()), 'email': row['email'].strip(), 'user_name': row['user_name'].strip(), 'password': row['password'].strip(), 'role': row['role'].strip()} for index, row in login_data.iterrows()]
    load_data_to_dynamodb(dynamodb, 'users', formatted_login_data)

    # Create 'conversations' table to store chat history
    create_table(dynamodb, 'conversations',
                 [{'AttributeName': 'conversation_id', 'KeyType': 'HASH'}, {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}],
                 [{'AttributeName': 'conversation_id', 'AttributeType': 'S'}, {'AttributeName': 'timestamp', 'AttributeType': 'S'}],
                 {'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1})

    # Initialize a new conversation
    conversation_id = initialize_conversation(dynamodb)
    print(f'Conversation started with ID: {conversation_id}')


if __name__ == "__main__":
    main()
