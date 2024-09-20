import boto3
from botocore.exceptions import ClientError

# Define the model ID for Claude 3.5 Sonnet
MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"

# Initialize Bedrock client for the Bedrock runtime
bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-east-1")

# Define the user message (without image)
user_message = "What are the account types in Techcombank?"

# Construct the messages array for text only
messages = [
    {
        "role": "user",
        "content": [
            {"text": user_message},
        ],
    }
]

try:
    # Send the message using the 'converse' method
    response = bedrock_runtime.converse(
        modelId=MODEL_ID,
        messages=messages,
    )

    # Extract and print the response text
    response_text = response["output"]["message"]["content"][0]["text"]
    print(response_text)

except ClientError as e:
    # Print the error if something goes wrong
    print(f"Error invoking Claude model: {e}")
