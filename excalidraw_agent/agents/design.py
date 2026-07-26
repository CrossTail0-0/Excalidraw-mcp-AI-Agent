import json
from ..prompts.design import DESIGN_PROMPT



def design_agent(
    state,
    llm
):
    prompt = DESIGN_PROMPT.substitute(
        components=state["components"],
    )

    print("Creating Design...")
    response = llm.chat(
        [
            {
                "role":"system",
                "content":prompt
            }
        ]
    )

    print(response)
    #state["design"] = json.loads(response)


    return {
        "design": json.loads(response),
        "chat_history": [{"role": "design_agent", "content": "Design computed"}]  # Note: wrapped in list

    }