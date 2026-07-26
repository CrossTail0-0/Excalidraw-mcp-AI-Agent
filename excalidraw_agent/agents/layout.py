import json
from ..prompts.layout import LAYOUT_PROMPT



def layout_agent(
    state,
    llm
):
    prompt = LAYOUT_PROMPT.substitute(
        components=state["components"]
    )

    print("Creating Layout...")
    response = llm.chat(
        [
            {
                "role":"system",
                "content":prompt
            }
        ]
    )

    print(response)
    state["layout"] = json.loads(response)



    return {
        "layout": json.loads(response),
        "chat_history": [{"role": "layout_agent", "content": "Layout computed"}]  # Note: wrapped in list

    }