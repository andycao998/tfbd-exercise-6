from typing import TypedDict, Annotated, NotRequired
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
import operator

from ticket_assistant.schemas import PolicyQuestion, PolicyAnswer

class QuestionState(TypedDict):
    # query: str
    messages: Annotated[list[AnyMessage], add_messages]
    question: NotRequired[PolicyQuestion | None]
    evidence: Annotated[list[str], operator.add]
    search_query: NotRequired[str]
    retrieval_attempts: int
    answer: NotRequired[PolicyAnswer | None]
    output: NotRequired[str | None]