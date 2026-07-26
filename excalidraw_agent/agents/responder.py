from typing import Dict, Any
from ..prompts.responder import RESPONDER_SYSTEM_PROMPT

def direct_responder(state: Dict[str, Any], llm) -> Dict[str, Any]:
    """Responds directly to non-diagram queries using the LLM."""
    
    print("Direct Responder: answering general question...")
    
    user_query = state["user_query"]
    
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
    
    return state