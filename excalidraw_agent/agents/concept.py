import json
from ..prompts.concept import CONCEPT_PROMPT



def concept_agent(
    state,
    llm
):

    response = llm.chat(
        [
            {
                "role":"system",
                "content":CONCEPT_PROMPT
            },

            {
                "role":"user",
                "content":state["user_query"]
            }
        ]
    )


    state["concept"] = json.loads(response)


    return state