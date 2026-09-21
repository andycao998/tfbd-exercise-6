from langchain_core.messages import HumanMessage, SystemMessage
from ticket_assistant.chains import build_question_chain
from ticket_assistant.graph.state import QuestionState
from ticket_assistant.rag import enforce_grounding, format_docs, format_query
from ticket_assistant.retriever import get_retriever
from ticket_assistant.schemas import PolicyAnswer
from ticket_assistant.llm import get_chat_model
from ticket_assistant.prompts import POLICY_ANSWER_PROMPT, REFRAME_QUESTION_PROMPT
from typing import cast

def question_node(state: QuestionState) -> dict:
    question = build_question_chain().invoke({"question": state["search_query"]})

    return {
        "question": question,
        "search_query": format_query(question)
    }

def retrieve_node(state: QuestionState) -> dict:
    """Fetch policy excerpts for the current search query."""

    query = state.get("search_query")
    docs = get_retriever(k=4).invoke(query)
    attempts = state.get("retrieval_attempts", 0) + 1
    return {
        "retrieval_attempts": attempts,
        "evidence": [f"retrieved {len(docs)} excerpt(s) for {query!r}"],
        "messages": [
            HumanMessage(f"Policy excerpts for {query!r}:\n\n{format_docs(docs)}")
        ]
    }

def answer_node(state: QuestionState) -> dict:
    """Produce an answer, then verify its citations before storing it."""

    convo = list(state["messages"]) + [
        HumanMessage(
            f"""Use only the policy excerpts below to answer this question:
            Question: {state["search_query"]}, 
            Sources: {state["evidence"]}
            """
        )
    ]
    raw: PolicyAnswer = cast(
        "PolicyAnswer",
        get_chat_model()
        .with_structured_output(PolicyAnswer)
        .invoke([SystemMessage(POLICY_ANSWER_PROMPT)] + convo)
    )

    answer = enforce_grounding(raw)
    return {
        "answer": answer,
        "evidence": [
            f"answer grounded={answer.grounded} sources={answer.sources}"
        ]
    }

MAX_RETRIEVAL_ATTEMPTS = 2
def route_after_answer(state: QuestionState) -> str:
    """Grounded? output it. Not grounded? try a different search, then give up."""

    answer = state.get("answer")
    if answer and answer.grounded:
        return "output"
    if state.get("retrieval_attempts", 0) < MAX_RETRIEVAL_ATTEMPTS:
        return "reframe"
    return "output"

def reframe_node(state: QuestionState) -> dict:
    """Rewrite the search query and send the graph back to `retrieve`."""

    question = state.get("question")
    failed = state.get("search_query", "")
    ask = (
        f"Question: {question.question}\n"
        f"Query that found nothing: {failed!r}\n\n"
        "Better query:"
    )
    new_query = (
        get_chat_model(temperature=0.2)
        .invoke([SystemMessage(REFRAME_QUESTION_PROMPT), HumanMessage(ask)])
        .text.strip()
        .strip('"')
    )
    
    if not new_query:
        new_query = question.summary # try summary as fall back
    return {
        "search_query": new_query,
        "evidence": [f"reframed query -> {new_query!r}"]
    }

def output_node(state: QuestionState) -> dict:
    return {"output": state.get("answer").answer}