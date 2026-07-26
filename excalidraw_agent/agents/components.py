import json
from loguru import logger

from ..prompts.components import COMPONENTS_PROMPT



def components_agent(
    state,
    llm
):
    concept = state["concept"]
    prompt = COMPONENTS_PROMPT.substitute(
        concept = concept
    )

    #print("Creating Components")
    logger.info("Creating Components...")
    response = llm.chat(
        [
            {
                "role":"system",
                "content":prompt
            }
        ]
    )

    #print( response)
    components = json.load(response)
    state["components"] = components

    logger.info(f"Extracted components for concept: {concept} is: {components}")
    logger.add("./LOGS/logs.log", rotation="500 MB", retention="10 days")


    return state