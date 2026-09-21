""" Challenge: recreate chat.py from earlier in the week but include RAG """

from ticket_assistant.converse import format_user_message
from ticket_assistant.knowledge_base import answer_with_sources

def main() -> None:
    messages: list[dict] = []
    total_input_tokens = 0
    total_output_tokens = 0


    print("Ticket assistant. Type /quit to exit, /tokens for usage, and /reset to start a new conversation")

    while True:
        try: 
            prompt = input("msg> ").strip()
        except (EOFError, KeyboardInterrupt):
            return

        if not prompt:
            continue
        if prompt == "/quit":
            return
        if prompt == "/tokens":
            print(f"Total Input Tokens: {total_input_tokens}; Total Output Tokens: {total_output_tokens}")
            continue
        if prompt == "/reset":
            messages = []
            total_input_tokens = 0
            total_output_tokens = 0
            continue

        # add user's new message to maintained list
        messages.append(format_user_message(prompt))
        result = answer_with_sources(prompt)
        usage = result["usage"]
        total_input_tokens += usage["input_tokens"]
        total_output_tokens += usage["output_tokens"]

        print(f"assistant> {result["answer"]}")
        for source in result["sources"]:
            print(f"\t{source}")

       
if __name__ == "__main__":
    main()