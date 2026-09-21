from ticket_assistant.graph.graph import build_graph_with_memory
from ticket_assistant.graph.state import QuestionState

import uuid
from langchain_core.runnables import RunnableConfig

def print_steps(app, graph_state, config: RunnableConfig):
    for chunk in app.stream(graph_state, config, stream_mode="updates"):
        print("=================================")
        print(chunk)

    return "closed"

def start_conversation(app, config):
    print("Ticket assistant. Type /quit to exit.")

    state = {}
    
    while True:
        try: 
            prompt = input("> ")
        except (EOFError, KeyboardInterrupt):
            return

        if not prompt:
            continue
        if prompt == "/quit":
            return

        graph_state = {
            "search_query": prompt,
            # "messages": state.messages or [],
            "evidence": [],
            "retrieval_attempts": 0
        }

        status: str = "new"
        while status != "closed":
            status = print_steps(app, graph_state, config)

if __name__ == "__main__":

    app = build_graph_with_memory()

    # question = input("> ")

    thread_id = uuid.uuid4()
    config: RunnableConfig = {
        "configurable": {
            "thread_id": thread_id,    
        }
    }

    start_conversation(app, config)
    
    

        # # handle interruptions
        # if status == "interrupted":
        #     answer = input("approve / reject > ") or "reject"
        #     state = Command(resume=answer)

    # final_state = app.get_state(config).values
    # for node in final_state.get("trace", []):
    #     print(f"{node} ->")