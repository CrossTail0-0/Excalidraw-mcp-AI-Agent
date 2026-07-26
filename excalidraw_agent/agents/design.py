import json
from loguru import logger
from ..prompts.design import DESIGN_PROMPT



def design_agent(
    state,
    llm
):
    components = state["components"]
    prompt = DESIGN_PROMPT.substitute(
        components=components,
    )

    #print("Creating Design...")
    logger.info("Creating Design...")
    response = llm.chat(
        [
            {
                "role":"system",
                "content":prompt
            }
        ]
    )

    #print(response)
    #state["design"] = json.loads(response)
    design = json.loads(response)

    
    logger.info(f"Extracted design for components: {components} is: {design}")
    logger.add("./LOGS/logs.log", rotation="500 MB", retention="10 days")


    return {
        "design": design,
        "chat_history": [{"role": "design_agent", "content": "Design computed"}]  # Note: wrapped in list

    }