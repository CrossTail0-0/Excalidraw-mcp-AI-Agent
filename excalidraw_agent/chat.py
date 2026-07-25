class Chatbot:


    def __init__(
        self,
        graph,
        read_me
    ):

        self.graph = graph
        self.read_me = read_me



    async def chat(self):

        print(
            "Excalidraw Agent"
        )


        while True:

            query=input(
                "\nYou: "
            )


            if query=="exit":
                break


            state={

                "chat_history":[],

                "user_query":query,

                "concept":{},

                "layout_plan":{},

                "elements":[],

                "checkpoint_id":None,

                "export_url":None,

                "excalidraw_docs":self.read_me

            }


            result = await self.graph.ainvoke(
                state
            )


            print(
                "\nDiagram:"
            )


            print(
                result["export_url"]
            )