from langgraph.graph import StateGraph, END
from typing import Dict, Any, Optional
import time

from .state import DiagramState
from .cache.diagram_cache import DiagramCache
from .agents.supervisor import supervisor
from .agents.concept import concept_agent
from .agents.components import components_agent
from .agents.design import design_agent
from .agents.layout import layout_agent
from .agents.excalidraw import excalidraw_agent
from .agents.intent import intent_agent
from .agents.responder import direct_responder

def build_graph(llm, excalidraw, redis_url: Optional[str] = None):
    workflow = StateGraph(DiagramState)
    
    # Initialize Redis cache
    cache = DiagramCache(
        redis_url=redis_url or "redis://localhost:6379/0",
        fallback_to_memory=True
    )
    
    # Cache check node (async)
    async def check_cache(state: Dict[str, Any]) -> Dict[str, Any]:
        """Check if diagram is cached using Redis."""
        print("🔍 Checking Redis cache...")
        user_query = state["user_query"]
        
        # Check health first
        is_healthy = await cache.health_check()
        if not is_healthy:
            print("⚠️  Redis is unavailable, using in-memory fallback")
        
        cached_result = await cache.get_cached_result(user_query)
        
        if cached_result:
            print("✅ Cache HIT! Returning cached diagram.")
            state["elements"] = cached_result.get("elements", [])
            state["export_url"] = cached_result.get("export_url", "")
            state["is_cached"] = True
            state["cached_query"] = user_query
            state["cache_metadata"] = cached_result.get("metadata", {})
        else:
            print("❌ Cache MISS. Generating new diagram...")
            state["is_cached"] = False
        
        return state
    
    # Cache save node (async)
    async def save_to_cache(state: Dict[str, Any]) -> Dict[str, Any]:
        """Save generated diagram to Redis cache."""
        if not state.get("is_cached", False):
            user_query = state["user_query"]
            elements = state.get("elements", [])
            export_url = state.get("export_url", "")
            
            if elements and export_url:
                print("💾 Saving to Redis cache...")
                success = await cache.store_result(
                    query=user_query,
                    elements=elements,
                    export_url=export_url,
                    metadata={
                        "concept": state.get("concept", {}),
                        "components": state.get("components", {}),
                        "layout": state.get("layout", {}),
                        "design": state.get("design", {}),
                    }
                )
                if success:
                    print("✅ Cached successfully in Redis!")
                else:
                    print("⚠️  Failed to cache in Redis")
            else:
                print("⚠️  Not saving to cache: missing elements or export_url")
        
        return state
    
    # Conditional routing based on cache
    def route_after_cache(state: Dict[str, Any]) -> str:
        """Route to render or diagram pipeline based on cache."""
        if state.get("is_cached", False):
            return "render_directly"
        else:
            return "generate_diagram"
    
    # Add all nodes (making them async-friendly)
    workflow.add_node("intent", lambda state: intent_agent(state, llm))
    workflow.add_node("check_cache", check_cache)
    workflow.add_node("supervisor", supervisor)
    workflow.add_node("concept", lambda state: concept_agent(state, llm))
    workflow.add_node("components", lambda state: components_agent(state, llm))
    workflow.add_node("layout", lambda state: layout_agent(state, llm))
    workflow.add_node("design", lambda state: design_agent(state, llm))
    workflow.add_node("excalidraw", lambda state: excalidraw_agent(state))
    workflow.add_node("save_cache", save_to_cache)
    workflow.add_node("responder", lambda state: direct_responder(state, llm))
    
    # Render node
    async def render(state):
        start_time = time.time()
        
        elements = state.get("elements", [])
        export_url = state.get("export_url", "")
        
        # If no export_url (fresh generation), create it
        if not export_url and elements:
            print("📤 Exporting diagram...")
            result = await excalidraw.render(elements)
            export_url = await excalidraw.export_diagram(elements)
            state["export_url"] = export_url
        
        state["rendering_time"] = time.time() - start_time
        return state
    
    workflow.add_node("render", render)
    
    # Set entry point
    workflow.set_entry_point("intent")
    
    # Routing from intent
    def route_based_on_intent(state: Dict[str, Any]) -> str:
        if state.get("is_diagram_request", False):
            return "diagram_pipeline"
        else:
            return "direct_response"
    
    workflow.add_conditional_edges(
        "intent",
        route_based_on_intent,
        {
            "diagram_pipeline": "check_cache",
            "direct_response": "responder"
        }
    )
    
    # Cache routing
    workflow.add_conditional_edges(
        "check_cache",
        route_after_cache,
        {
            "render_directly": "render",
            "generate_diagram": "supervisor"
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
    workflow.add_edge("render", "save_cache")
    workflow.add_edge("save_cache", END)
    
    # Direct response edge
    workflow.add_edge("responder", END)
    
    return workflow.compile()