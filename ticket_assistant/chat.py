""" interactive chat with Bedrock model using Converse API and tool calls where necessary """

from ticket_assistant.converse import converse, text_of, usage_of, format_user_message
from ticket_assistant.knowledge_base import answer_with_sources

MAX_TOOL_REQUESTS = 5
SYSTEM_PROMPT = (
    "You are a support engineer's assistant for an e-commerce company."
    "Use your tools to check facts rather than guessing."
    "If you do not know something and no tool can tell you, say so plainly."
    "Keep answers concise."
)


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