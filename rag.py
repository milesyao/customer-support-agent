# Standard library imports
import os
import sys
import json
import time

# Third-party imports
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

os.environ["AWS_DEFAULT_REGION"] = "us-east-2"

# Print SDK versions
print(f"Python version: {sys.version.split()[0]}")
print(f"Boto3 SDK version: {boto3.__version__}")

# Create boto3 session and set AWS region
boto_session = boto3.Session()
aws_region = boto_session.region_name

print(f"aws regsion is {aws_region}")
# Create boto3 clients for Bedrock
bedrock_config = Config(connect_timeout=120, read_timeout=120, retries={'max_attempts': 0})
bedrock_client = boto3.client('bedrock-runtime')
bedrock_agent_client = boto3.client('bedrock-agent-runtime', config=bedrock_config)

bedrock_kb_id = "W9CGK0RGBV"

# Print configurations
print("AWS Region:", aws_region)
print("Bedrock Knowledge Base ID:", bedrock_kb_id)


# Implement the `retrieve` function
def retrieve(user_query, kb_id, num_of_results=5):
    return bedrock_agent_client.retrieve(
        retrievalQuery= {
            'text': user_query
        },
        knowledgeBaseId=kb_id,
        retrievalConfiguration= {
            'vectorSearchConfiguration': {
                'numberOfResults': num_of_results,
            }
        }
    )

user_query = "How to use bluetooth?"

response = retrieve(user_query, bedrock_kb_id, num_of_results=3)

print("Retrieval Results:\n", json.dumps(response['retrievalResults'], indent=2, default=str))
