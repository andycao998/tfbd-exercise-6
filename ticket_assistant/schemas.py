from pydantic import BaseModel, Field

class PolicyQuestion(BaseModel):
    """ 
        A question regarding a specific company policy.

        Use only the question asked. Do not assume facts it does not state.
        Do not answer the question.
    """

    question: str = Field(
        description="The full question, copied verbatim."
    )

    summary: str = Field(
        description="Summary of the question for the purposes of model knowledge."
    )


class PolicyAnswer(BaseModel):
    """ A policy-grounded answer to a question.

    Answer ONLY from the policy documents provided to you. The excerpts are the
    company's own operational policy; your own general knowledge about how
    software systems usually behave is NOT a source and must not be used to
    fill a gap.

    If the excerpts do not cover the situation, say so by setting
    `grounded` to false and saying you don't know for the answer.
    DO NOT try to come up with a plausible sounding answer if you have
    no sources.
    """

    grounded: bool = Field(
        description=(
            "True only if the policy document excerpts directly support your answer. "
            "False if you had to rely on general knowledge or guesswork."
        )
    )

    sources: list[str] = Field(
        description=(
            "The exact policy document filenames you used. "
            "If you do not use or have any sources, populate with an empty list. Ex: []"
        ),
    )

    answer: str = Field(
        description=(
            "The grounded answer to the question based on the used policy documents. "
            "If the excerpts do not cover this situation, say you don't know and refuse to answer."
        )
    )