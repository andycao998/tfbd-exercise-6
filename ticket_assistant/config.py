import os

from dotenv import load_dotenv

load_dotenv()

AWS_PROFILE = os.environ["AWS_PROFILE"]
AWS_REGION = os.environ["AWS_REGION"]
BEDROCK_MODEL_ID = os.environ["BEDROCK_MODEL_ID"]
BEDROCK_EMBED_MODEL_ID = os.environ["BEDROCK_EMBED_MODEL_ID"]
BEDROCK_MAX_TOKENS = os.environ["BEDROCK_MAX_TOKENS"]