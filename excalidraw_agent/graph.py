from langgraph.graph import StateGraph, END
from langgraph.graph import START
from typing import Dict, Any

from .state import DiagramState
from .agents.supervisor import supervisor
from .agents.concept import concept_agent
from .agents.components import components_agent
from .agents.design import design_agent
from .agents.layout import layout_agent
from .agents.excalidraw import excalidraw_agent
from .agents.intent import intent_agent
from .agents.responder import direct_responder

def build_graph(llm, excalidraw):
    workflow = StateGraph(DiagramState)
    
    # Add all nodes
    workflow.add_node("intent", lambda state: intent_agent(state, llm))
    workflow.add_node("supervisor", supervisor)
    workflow.add_node("concept", lambda state: concept_agent(state, llm))
    workflow.add_node("components", lambda state: components_agent(state, llm))
    workflow.add_node("layout", lambda state: layout_agent(state, llm))
    workflow.add_node("design", lambda state: design_agent(state, llm))
    workflow.add_node("excalidraw", lambda state: excalidraw_agent(state))
    workflow.add_node("responder", lambda state: direct_responder(state, llm))
    
    async def render(state):
        result = await excalidraw.render(state["elements"])
        export = await excalidraw.export_diagram(state["elements"])
        state["export_url"] = export
        return state
    
    workflow.add_node("render", render)
    
    # Set entry point to intent detection
    workflow.set_entry_point("intent")
    
    # Conditional routing based on intent
    def route_based_on_intent(state: Dict[str, Any]) -> str:
        """Route to diagram pipeline or direct response based on intent."""
        if state.get("is_diagram_request", False):
            return "diagram_pipeline"
        else:
            return "direct_response"
    
    # Add conditional edges from intent
    workflow.add_conditional_edges(
        "intent",
        route_based_on_intent,
        {
            "diagram_pipeline": "supervisor",
            "direct_response": "responder"
        }
    )
    
    # Diagram pipeline edges
    workflow.add_edge("supervisor", "concept")
    workflow.add_edge("concept", "components")
    workflow.add_edge("components", "layout")
    workflow.add_edge("components", "design")
    workflow.add_edge("layout", "excalidraw")
    workflow.add_edge("design", "excalidraw")
    workflow.add_edge("excalidraw", "render")
    workflow.add_edge("render", END)
    
    # Direct response edge
    workflow.add_edge("responder", END)
    
    return workflow.compile()