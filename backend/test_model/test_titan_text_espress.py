import boto3
import json

# Initialize Bedrock client
bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')

def invoke_bedrock_titan_model(model_id, input_text):
    # Construct the payload with only 'inputText'
    body = json.dumps({
        "inputText": input_text  # Keep it simple with just 'inputText'
    })
    
    try:
        response = bedrock_client.invoke_model(
            body=body,
            modelId=model_id,
            contentType="application/json",
            accept="application/json"
        )
        # Parse and return the response
        result = json.loads(response['body'].read())
        return result
    except Exception as e:
        # Print detailed error information
        print(f"Error invoking Titan model: {e}")
        if hasattr(e, 'response'):
            print("Error response from AWS:")
            print(json.dumps(e.response, indent=4))  # Print the full error response in a readable format
        return None

# Test with Titan Text G1 - Express model
model_id = "amazon.titan-text-express-v1"  # Ensure you're using the correct Titan model ID
input_text = "What are the account types in Techcombank?"
response = invoke_bedrock_titan_model(model_id, input_text)

print(response)
