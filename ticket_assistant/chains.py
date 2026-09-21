from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableParallel, RunnableLambda
from ticket_assistant.llm import get_chat_model
from ticket_assistant.schemas import PolicyQuestion
from ticket_assistant.prompts import POLICY_QUESTION_PROMPT
from operator import itemgetter

def build_question_chain() -> Runnable:
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", POLICY_QUESTION_PROMPT),
            ("human", "Question:\n{question}")
        ]
    )

    structured_model = get_chat_model().with_structured_output(PolicyQuestion)
    return prompt | structured_model