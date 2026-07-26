import json
from loguru import logger

from ..prompts.concept import CONCEPT_PROMPT


def concept_agent(
    state,
    llm
):
    user_query = state["user_query"]
    prompt = CONCEPT_PROMPT.substitute(
        user_query = user_query
    )

    #print("Extracting Concept")
    logger.info("Extracting Concept...")
    response = llm.chat(
        [
            {
                "role":"system",
                "content":prompt
            }
        ]
    )
    #print(response)
    concept = json.loads(response)
    state["concept"] = concept

    logger.info(f"Extracted concept for query: {user_query} is: {concept}")
    logger.add("./LOGS/logs.log", rotation="500 MB", retention="10 days")

    return state