import pytest
from ticket_assistant.graph.nodes.qa import MAX_RETRIEVAL_ATTEMPTS, route_after_answer
from ticket_assistant.graph.state import QuestionState
from ticket_assistant.retriever import load_kb_chunks
from ticket_assistant.graph.graph import build_graph
from langgraph.graph import START, END

from ticket_assistant.schemas import PolicyAnswer

def test_documents_load_and_split():
    documents = load_kb_chunks()

    account_and_billing_chunks = 0
    known_issues_chunks = 0
    refund_policy_chunks = 0
    shipping_policy_chunks = 0

    for document in documents:
        source = document.metadata["source"]
        if "account-and-billing.md" in source:
            account_and_billing_chunks += 1
        elif "known-issues.md" in source:
            known_issues_chunks += 1
        elif "refund-policy.md" in source:
            refund_policy_chunks += 1
        elif "shipping-policy.md" in source:
            shipping_policy_chunks += 1

        assert document.page_content # assert chunk not empty

    # manual count of sections -> chunks in kb_documents
    assert account_and_billing_chunks == 4
    assert known_issues_chunks == 4
    assert refund_policy_chunks == 6
    assert shipping_policy_chunks == 4


def test_graph_has_expected_nodes_and_edges():
    graph = build_graph()
    structure = graph.get_graph() # get graph structure

    nodes = ["question", "retrieve", "answer", "reframe", "output"]
    for node in nodes:
        assert node in structure.nodes

    edges = {
        (edge.source, edge.target)
        for edge in structure.edges
    }

    assert (START, "question") in edges
    assert ("question", "retrieve") in edges
    assert ("retrieve", "answer") in edges
    assert ("reframe", "retrieve") in edges
    assert ("output", END) in edges

    # the conditional edges expected
    assert ("answer", "output") in edges
    assert ("answer", "reframe") in edges


@pytest.mark.parametrize("grounded", [True, False])
def test_answer_conditional_routing(grounded):
    state: QuestionState = {
        "messages": [],
        "evidence": [],
        "retrieval_attempts": 1,
        "answer": PolicyAnswer(
            grounded=grounded,
            sources=["shipping-policy.md"],
            answer="You may request a replacement or refund.",
        ),
    }

    if grounded:
        assert route_after_answer(state) == "output"
    else:
        assert route_after_answer(state) == "reframe" # test other route


@pytest.mark.parametrize("attempts", [MAX_RETRIEVAL_ATTEMPTS - 1, MAX_RETRIEVAL_ATTEMPTS])
def test_route_answer_after_max_retrieval_attempts(attempts):
    state: QuestionState = {
        "messages": [],
        "evidence": [],
        "retrieval_attempts": attempts,
        "answer": PolicyAnswer(
            grounded=False,
            sources=[],
            answer="I don't know and cannot answer this question as none of my sources apply.",
        ),
    }

    # testing routing before and after hitting max retrieval attempts
    if attempts < MAX_RETRIEVAL_ATTEMPTS:
        assert route_after_answer(state) == "reframe"
    else:
        assert route_after_answer(state) == "output"