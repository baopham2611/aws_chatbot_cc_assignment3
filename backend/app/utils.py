import boto3
from botocore.exceptions import ClientError

# Initialize the Bedrock client
bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-east-1")

def query_bedrock_model(model_id, user_input):
    """Query the Bedrock generative AI models (Claude 3.5 Sonnet)."""
    
    # Construct the messages array with a request for English response
    messages = [
        {
            "role": "user",
            "content": [
                {"text": f"{user_input}\n\nPlease provide the response in English."},  # Adding instruction for English response
            ],
        }
    ]

    try:
        # Send the message using the 'converse' method
        response = bedrock_runtime.converse(
            modelId=model_id,
            messages=messages,
        )

        # Extract and return the response text
        response_text = response["output"]["message"]["content"][0]["text"]
        return response_text

    except ClientError as e:
        # Handle errors in communication with Bedrock
        print(f"Error invoking Claude model: {e}")
        return "Sorry, I couldn't process your request at the moment."
