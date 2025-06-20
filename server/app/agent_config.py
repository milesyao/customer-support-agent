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

# @function_tool
# def get_past_orders():
#     return json.dumps(mock_api.get_past_orders())

# @function_tool
# def submit_refund_request(order_number: str):
#     """Confirm with the user first"""
#     return mock_api.submit_refund_request(order_number)

@function_tool
def get_product_info(user_query: str):
    """find answers about user's questions on product details including usage, features, etc."""
    retrieved_results = retrieve(user_query, bedrock_kb_id, num_of_results=3)
    return retrieved_results


customer_support_agent = Agent(
    name="Customer Support Agent",
    instructions=f"You are a customer support assistant. Always use the get_product_info tool to answer user's questions. {STYLE_INSTRUCTIONS}",
    model="gpt-4o-mini",
    tools=[get_product_info],
)

# stylist_agent = Agent(
#     name="Stylist Agent",
#     model="gpt-4o-mini",
#     instructions=f"You are a stylist assistant. {STYLE_INSTRUCTIONS}",
#     tools=[WebSearchTool(user_location=UserLocation(type="approximate", city="Tokyo"))],
#     handoffs=[customer_support_agent],
# )

# triage_agent = Agent(
#     name="Triage Agent",
#     model="gpt-4o-mini",
#     instructions=f"Route the user to the appropriate agent based on their request. {STYLE_INSTRUCTIONS}",
#     handoffs=[customer_support_agent],
# )

starting_agent = customer_support_agent
