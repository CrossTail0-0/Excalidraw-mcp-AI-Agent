import json
from ..prompts.layout import LAYOUT_PROMPT



def layout_agent(
    state,
    llm
):
    #print("Concept:", state["concept"])
    prompt = LAYOUT_PROMPT.substitute(
        concept=state["concept"]
    )


    response = llm.chat(
        [
            {
                "role":"system",
                "content":prompt
            }
        ]
    )

    #print("Layout Agent Response:", response)
    state["layout_plan"] = json.loads(response)


    return state