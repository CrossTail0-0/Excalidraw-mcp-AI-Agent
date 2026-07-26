class Chatbot:
    def __init__(
        self,
        graph,
        read_me
    ):
        self.graph = graph
        self.read_me = read_me

    async def chat(self):
        print("Excalidraw Agent")
        print("Type 'exit' to quit\n")

        while True:
            query = input("\nYou: ")

            if query.lower() == "exit":
                print("Goodbye!")
                break

            state = {
                "chat_history": [],
                "user_query": query,
                "is_diagram_request": None,
                "intent_response": "",
                "concept": {},
                "components": {},
                "layout": {},
                "design": {},
                "elements": [],
                "checkpoint_id": None,
                "export_url": None,
                "excalidraw_docs": self.read_me
            }

            try:
                result = await self.graph.ainvoke(state)

                # Check if this was a diagram request
                if result.get("is_diagram_request", False):
                    # Diagram flow
                    print("\n📐 Diagram Generated!")
                    
                    if result.get("export_url"):
                        print(f"🔗 View your diagram at: {result['export_url']}")
                    else:
                        print("⚠️  Diagram was generated but no export URL was created.")
                    
                else:
                    # Non-diagram flow - show the assistant's response
                    print("\n🤖 Assistant:")
                    
                    if result.get("intent_response"):
                        print(result["intent_response"])
                    else:
                        print("I'm not sure how to respond to that. Could you rephrase?")

            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                print("Please try again with a different query.")