# RAG Assistant as LangGraph Agent
Multi-turn conversation agent built on a LangGraph graph that relies on RAG to answer specific policy questions.
## Usage
### Run Graph:
1. `python -m ticket_assistant.graph.run`

### Tests:
1. Install optional dependencies (for tests): `pip install -e ".[test]"`
1. Run tests: `python -m pytest`

## Documentation
1. Requirement 4: A question not covered by provided knowledge base documents: `Can a gift card be returned?`
    - Deliberately not mentioned in the refund-policy containing the list of non-returnable items
    - No sources found -> model responds that it doesn't know
1. Requirement 8: Graph cycle through retrieve -> answer -> reframe -> retrieve loop if the first doesn't pull back a source. The model attempts to reframe the question based on the set of provided topics to see if that makes the question more relevant to the knowledge base sources.
1. Requirement 9: Max retrieval attempts is 2, with the assistant responding it doesn't know after hitting that threshold.

### Graph Diagram
```mermaid
---
config:
  flowchart:
    curve: linear
---
graph TD;
        __start__([<p>__start__</p>]):::first
        question(question)
        retrieve(retrieve)
        answer(answer)
        reframe(reframe)
        output(output)
        __end__([<p>__end__</p>]):::last
        __start__ --> question;
        answer -.-> output;
        answer -.-> reframe;
        question --> retrieve;
        reframe --> retrieve;
        retrieve --> answer;
        output --> __end__;
        classDef default fill:#f2f0ff,line-height:1.2
        classDef first fill-opacity:0
        classDef last fill:#bfb6fc
