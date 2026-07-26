from typing import Annotated, TypedDict, List, Dict, Any, Optional
import operator

class DiagramState(TypedDict):
    # conversation
    chat_history: Annotated[List[Dict[str, Any]], operator.add]
    
    # user input
    user_query: str
    
    # Intent detection
    is_diagram_request: bool  # True if user wants a diagram
    intent_response: Optional[str]  # Direct response for non-diagram queries
    
    # concept agent result
    concept: Dict[str, Any]
    
    # components
    components: Dict[str, Any]
    
    # layout agent result
    layout: Dict[str, Any]
    
    # geometry
    design: Dict[str, Any]
    
    # generated excalidraw elements
    elements: List[Dict[str, Any]]
    
    # MCP state
    excalidraw_checkpoint: Optional[str]
    export_url: Optional[str]
    
    # Excalidraw documentation
    excalidraw_docs: str