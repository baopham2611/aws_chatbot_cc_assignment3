import boto3

# Initialize Bedrock client to list models
bedrock = boto3.client('bedrock', region_name='us-east-1')

def list_bedrock_models():
    """List available models in Bedrock."""
    response = bedrock.list_foundation_models()
    
    # Iterate over the correct key 'modelSummaries'
    for model in response['modelSummaries']:
        print(f"Model ID: {model['modelId']}, Provider: {model['providerName']}")

# List the models to find the correct one for Claude or Titan
list_bedrock_models()
