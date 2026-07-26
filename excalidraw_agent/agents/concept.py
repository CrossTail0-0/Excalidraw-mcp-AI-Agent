import json
from ..prompts.concept import CONCEPT_PROMPT


def concept_agent(
    state,
    llm
):
    prompt = CONCEPT_PROMPT.substitute(
        user_query = state["user_query"]
    )

    print("Extracting Concept")
    response = llm.chat(
        [
            {
                "role":"system",
                "content":prompt
            }
        ]
    )
    print(response)
    state["concept"] = json.loads(response)


    return state