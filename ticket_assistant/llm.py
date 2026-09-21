
from langchain_core.language_models import BaseChatModel
from langchain_aws import ChatBedrockConverse
from ticket_assistant.config import AWS_REGION, BEDROCK_MAX_TOKENS, BEDROCK_MODEL_ID

def get_chat_model(
    *,
    temperature: float = 0.0,
    max_tokens: int | None = None,
) -> BaseChatModel:
    """ Return a configured bedrock chat model - could be swapped out for any BaseChatModel """

    return ChatBedrockConverse(
        model=BEDROCK_MODEL_ID,
        region_name=AWS_REGION,
        temperature=temperature,
        max_tokens=max_tokens or BEDROCK_MAX_TOKENS
    )