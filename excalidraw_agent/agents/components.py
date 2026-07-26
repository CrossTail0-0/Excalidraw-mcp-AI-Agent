import json
from ..prompts.components import COMPONENTS_PROMPT



def components_agent(
    state,
    llm
):
    prompt = COMPONENTS_PROMPT.substitute(
        concept=state["concept"]
    )

    print("Creating Components")
    response = llm.chat(
        [
            {
                "role":"system",
                "content":prompt
            }
        ]
    )

    print( response)
    state["components"] = json.loads(response)


    return state