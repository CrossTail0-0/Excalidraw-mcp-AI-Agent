import json
from loguru import logger

from ..prompts.layout import LAYOUT_PROMPT



def layout_agent(
    state,
    llm
):
    components = state["components"]
    prompt = LAYOUT_PROMPT.substitute(
        components=state["components"]
    )

    #print("Creating Layout...")
    logger.info("Creating Layout...")
    response = llm.chat(
        [
            {
                "role":"system",
                "content":prompt
            }
        ]
    )

    #print(response)
    layout = json.loads(response)
    state["layout"] = json.loads(response)

    logger.info(f"Extracted layout for components: {components} is: {layout}")
    logger.add("./LOGS/logs.log", rotation="500 MB", retention="10 days")

    return {
        "layout": json.loads(response),
        "chat_history": [{"role": "layout_agent", "content": "Layout computed"}]  # Note: wrapped in list

    }