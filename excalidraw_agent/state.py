from typing import TypedDict, List, Dict, Any, Optional


class DiagramState(TypedDict):

    # conversation
    chat_history: List[Dict[str, str]]

    # user input
    user_query: str


    # concept agent result
    concept: Dict[str, Any]


    # layout agent result
    layout_plan: Dict[str, Any]


    # generated excalidraw elements
    elements: List[Dict[str, Any]]


    # MCP state
    excalidraw_checkpoint: Optional[str]

    export_url: Optional[str]


    # Excalidraw documentation
    excalidraw_docs: str