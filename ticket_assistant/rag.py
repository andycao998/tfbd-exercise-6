""" Using retrievers as a part of a chain for RAG """

from operator import itemgetter
from typing import cast, Any

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableLambda, RunnableParallel

from ticket_assistant.chains import build_question_chain
from ticket_assistant.llm import get_chat_model
from ticket_assistant.retriever import get_retriever, load_kb_chunks
from ticket_assistant.schemas import PolicyQuestion, PolicyAnswer
from ticket_assistant.prompts import POLICY_ANSWER_PROMPT


def format_query(question: PolicyQuestion) -> str:
    return f"{question.question} - {question.summary}"

def format_docs(docs: list[Document]) -> str:
    """ turn each found doc into one long string that can be added to the model system prompt """

    blocks = []
    for doc in docs:
        meta = doc.metadata
        header = f"source: {meta.get("source", "unknown")}"
        if meta.get("section"):
            header += f" | section: {meta.get("section")}"

        blocks.append(f"--- {header} ---\n{doc.page_content.strip()}")

    result = "\n\n".join(blocks)
    return result

def enforce_grounding(answer: PolicyAnswer) -> PolicyAnswer:
    """ Make sure the model actually grounded itself in the content, rather than just saying it did """

    known = {chunk.metadata["source"] for chunk in load_kb_chunks()}
    valid_citations = [source for source in answer.sources if source in known]

    if not valid_citations:
        return answer.model_copy(
            update={
                "grounded": False, 
                "sources": [],
                "answer": "I don't know and cannot answer this question as none of my sources apply."
            }
        )
    return answer.model_copy(update={"sources": valid_citations})

def build_rag_chain(k: int = 4) -> Runnable:
    retriever = get_retriever(k=k)

    prompt = ChatPromptTemplate.from_messages([
        ("system", POLICY_ANSWER_PROMPT),
        ("human", "{question}")
    ])

    structured_model: Runnable[Any, PolicyAnswer] = cast(
        "Runnable[Any, PolicyAnswer]", 
        get_chat_model().with_structured_output(PolicyAnswer)
    )

    return (RunnableParallel(
        question=itemgetter("question"),
        context=itemgetter("question") | retriever | RunnableLambda(format_docs)
    ) | prompt | structured_model | RunnableLambda(enforce_grounding))


def build_answer_chain() -> Runnable:
    """ Putting the RAG chain together with question chain to use RAG with the question """

    rag = build_rag_chain()

    return RunnableParallel(question=build_question_chain()) | RunnableParallel(
        question=itemgetter("question"),
        answer=(
            itemgetter("question") | 
            RunnableLambda(format_query) | 
            RunnableLambda(lambda q: {"question" : q}) |
            rag
        )
    )
