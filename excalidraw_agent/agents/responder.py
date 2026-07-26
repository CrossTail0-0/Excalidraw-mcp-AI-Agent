from typing import Dict, Any
from loguru import logger

from ..prompts.responder import RESPONDER_SYSTEM_PROMPT

def direct_responder(state: Dict[str, Any], llm) -> Dict[str, Any]:
    """Responds directly to non-diagram queries using the LLM."""
    
    #print("Direct Responder: answering general question...")
    
    user_query = state["user_query"]
    logger.info(f"Direct Responder: answering general question...")
    
    # Use the LLM service's chat method
    response = llm.chat([
        {
            "role": "system",
            "content": RESPONDER_SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": user_query
        }
    ])
    
    # Store the response in the state
    state["intent_response"] = response
    state["chat_history"] = [
        {"role": "assistant", "content": response}
    ]
    logger.info(f"LLM response to quer: {user_query} is: {response}")
    logger.add("./LOGS/logs.log", rotation="500 MB", retention="10 days")
    
    return state