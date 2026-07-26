from typing import Dict, Any
import json
import re

from ..prompts.intent import INTENT_SYSTEM_PROMPT

def intent_agent(state: Dict[str, Any], llm) -> Dict[str, Any]:
    """Detects if the user wants to draw a diagram or just ask a question."""
    
    print("Intent Agent: analyzing user query...")
    
    user_query = state["user_query"]
    
    # Use the LLM service's chat method
    response = llm.chat([
        {
            "role": "system",
            "content": INTENT_SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": f"User query: {user_query}\n\nDetermine if this is a diagram request."
        }
    ])
    
    print(f"Intent Agent response: {response}")
    
    # Parse the JSON response
    try:
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            is_diagram = result.get("is_diagram", False)
            reason = result.get("reason", "")
        else:
            # Fallback: simple keyword detection
            is_diagram = detect_diagram_keywords(user_query)
            reason = "Fallback keyword detection"
    except:
        # Fallback: keyword detection
        is_diagram = detect_diagram_keywords(user_query)
        reason = "Fallback keyword detection"
    
    # Update state
    state["is_diagram_request"] = is_diagram
    
    # If not a diagram, we'll use LLM to answer directly later
    if not is_diagram:
        state["intent_response"] = None  # Will be filled by direct_responder
        state["chat_history"] = [
            {"role": "intent_agent", "content": f"Detected: Not a diagram request. {reason}"}
        ]
    else:
        state["chat_history"] = [
            {"role": "intent_agent", "content": f"Detected: Diagram request. {reason}"}
        ]
    
    return state

def detect_diagram_keywords(query: str) -> bool:
    """Simple keyword-based fallback detection."""
    diagram_keywords = [
        "draw", "diagram", "chart", "flowchart", "visualize", 
        "graph", "map", "schema", "architecture", "design",
        "illustrate", "plot", "render", "show", "display",
        "network", "process", "workflow", "outline", "layout",
        "flow", "structure", "hierarchy", "tree", "cycle"
    ]
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in diagram_keywords)