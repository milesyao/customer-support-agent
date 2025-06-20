import json

from agents import Agent, WebSearchTool, function_tool
from agents.tool import UserLocation

import app.mock_api as mock_api
import os
import sys
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

STYLE_INSTRUCTIONS = "Use a conversational tone and write in a chat style without formal formatting or lists and do not use any emojis."

@function_tool
def get_known_product_info(user_query: str):
    """find answers about user's questions on product details including usage, features, etc."""
    retrieved_results = retrieve(user_query, bedrock_kb_id, num_of_results=3)
    # sources = {}
    # s3 = boto3.client('s3')
    # for result in retrieved_results["retrievalResults"]:
    #     s3_url = result["metadata"]["x-amz-bedrock-kb-source-uri"]
    #     # Remove 's3://' prefix and split only on the first slash
    #     s3_path = s3_url.replace('s3://', '', 1)
    #     bucket_name, document_name = s3_path.split('/', 1)
    #     presigned_url = s3.generate_presigned_url(
    #         'get_object',
    #         Params={'Bucket': bucket_name, 'Key': document_name},
    #         ExpiresIn=3600  # URL valid for 1 hour
    #     )
    #     sources[document_name] = presigned_url
    # return sources
    return retrieved_results

supported_products = ["iSteady M7"]

# Create dynamic product list for instructions
product_list = ", ".join(supported_products)

customer_support_agent = Agent(
    name="Customer Support Agent",
    instructions=f"You are a customer support assistant. \
        Use get_known_product_info tool to answer questions related to {product_list}, otherwise use WebSearchTool \
        to get latest information about Hoham products, Q & A and customer policy. {STYLE_INSTRUCTIONS}",
    model="gpt-4o-mini",
    tools=[get_known_product_info, WebSearchTool()],
)

starting_agent = customer_support_agent
