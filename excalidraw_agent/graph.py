from langgraph.graph import StateGraph, END

from .state import DiagramState

from .agents.supervisor import supervisor
from .agents.concept import concept_agent
from .agents.components import components_agent
from .agents.design import design_agent
from .agents.layout import layout_agent
from .agents.excalidraw import excalidraw_agent



def build_graph(
    llm,
    excalidraw
):


    workflow = StateGraph(
        DiagramState
    )


    workflow.add_node(
        "supervisor",
        supervisor
    )


    workflow.add_node(
        "concept",

        lambda state:
        concept_agent(
            state,
            llm
        )
    )

    workflow.add_node(
        "components",

        lambda state:
        components_agent(
            state,
            llm
        )
    )
    

    workflow.add_node(
        "layout",

        lambda state:
        layout_agent(
            state,
            llm
        )
    )

    workflow.add_node(
        "design",

        lambda state:
        design_agent(
            state,
            llm
        )
    )

    workflow.add_node(
        "excalidraw",

        lambda state:
        excalidraw_agent(
            state
        )
    )


    async def render(state):

        result = await excalidraw.render(
            state["elements"]
        )


        export = await excalidraw.export_diagram(
            state["elements"]
        )


        state["export_url"]=export


        return state



    workflow.add_node("render", render)


    workflow.set_entry_point("supervisor")
    workflow.add_edge("supervisor", "concept")
    workflow.add_edge("concept", "components")

    workflow.add_edge("components", "layout")
    workflow.add_edge("components", "design")

    workflow.add_edge( "layout", "excalidraw")
    workflow.add_edge( "design", "excalidraw")

    workflow.add_edge("excalidraw", "render")


    workflow.add_edge(
        "render",
        END
    )


    return workflow.compile()