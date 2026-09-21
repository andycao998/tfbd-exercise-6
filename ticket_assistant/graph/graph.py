
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.checkpoint.memory import InMemorySaver
from ticket_assistant.schemas import PolicyQuestion, PolicyAnswer
from ticket_assistant.graph.state import QuestionState
from ticket_assistant.graph.nodes.qa import question_node, retrieve_node, answer_node, reframe_node, output_node, route_after_answer

SERDE = JsonPlusSerializer(allowed_msgpack_modules=[PolicyQuestion, PolicyAnswer])

def build_graph(checkpointer=None):

    graph = StateGraph(QuestionState)

    # --- NODES ---
    graph.add_node("question", question_node)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("answer", answer_node)
    graph.add_node("reframe", reframe_node)
    graph.add_node("output", output_node)

    # --- EDGES ---
    graph.add_edge(START, "question")
    graph.add_edge("question", "retrieve")
    graph.add_edge("retrieve", "answer")

    graph.add_conditional_edges(
        "answer",
        route_after_answer,
        {
            "output": "output",
            "reframe": "reframe",
        },
    )

    graph.add_edge("reframe", "retrieve")
    graph.add_edge("output", END)

    return graph.compile(checkpointer=checkpointer)

def build_graph_with_memory():
    """ builds the graph with a checkpointer so the state can survive an interruption """
    return build_graph(checkpointer=InMemorySaver(serde=SERDE))

if __name__ == "__main__":
    app = build_graph()
    print(app.get_graph().draw_mermaid())