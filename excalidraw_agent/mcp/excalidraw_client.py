import json


class ExcalidrawClient:


    def __init__(
        self,
        tools
    ):

        self.create_view = None
        self.export = None


        for tool in tools:

            if tool.name=="create_view":
                self.create_view = tool


            if tool.name=="export_to_excalidraw":
                self.export = tool



    async def render(
        self,
        elements
    ):

        return await self.create_view.ainvoke(
            {
                "elements":json.dumps(elements)
            }
        )



    async def export_diagram(
        self,
        elements
    ):

        document={

            "type":"excalidraw",

            "version":2,

            "elements":elements,

            "appState":{},

            "files":{}

        }


        return await self.export.ainvoke(
            {
                "json":json.dumps(document)
            }
        )