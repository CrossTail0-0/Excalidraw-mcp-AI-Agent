import asyncio
from .chat_history.storage import ChatHistoryStorage

class Chatbot:
    def __init__(self, graph, read_me, storage_dir: str = "CHAT_HISTORY"):
        self.graph = graph
        self.read_me = read_me
        self.storage = ChatHistoryStorage(storage_dir)
        self.conversation_count = 0

    async def chat(self):
        print("\n" + "="*60)
        print("✏️  Excalidraw AI Agent")
        print("="*60)
        print("💡 I can help you draw diagrams or answer questions!")
        print("💡 Type 'exit' to quit")
        print("💡 Type 'help' for examples")
        print("💡 Type 'history' to view past sessions")
        print("="*60 + "\n")
        
        # Start a new session
        session_id = self.storage.start_new_session()
        print(f"📝 Session started: {session_id}")

        while True:
            query = input("\nYou: ").strip()

            if query.lower() == "exit":
                # Save before exiting
                if self.storage.get_current_history():
                    filepath = await self.storage.save_current_session()
                    print(f"\n💾 Chat history saved to: {filepath}")
                print("\n👋 Goodbye! Have a great day!")
                break
            
            if query.lower() == "help":
                self.show_help()
                continue
            
            if query.lower() == "history":
                await self.show_history()
                continue

            if not query:
                print("Please enter a message.")
                continue

            self.conversation_count += 1
            
            # Add user message to history
            self.storage.add_to_history({
                "role": "user",
                "content": query
            })
            
            print(f"\n⏳ Processing... (Message #{self.conversation_count})")

            state = {
                "chat_history": self.storage.get_current_history(),  # Pass full history
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
                
                # Display and store the response
                await self.display_response(result)
                
                # Auto-save after each interaction
                filepath = await self.storage.save_current_session()
                print(f"\n💾 Auto-saved to: {filepath}")

            except Exception as e:
                error_msg = str(e)
                self.storage.add_to_history({
                    "role": "error",
                    "content": error_msg
                })
                await self.storage.save_current_session()
                print(f"\n❌ Error: {error_msg}")
                print("Please try again with a different query.")

    async def display_response(self, result: Dict):
        """Display the response and add to history."""
        
        if result.get("is_diagram_request", False):
            # Diagram response
            response = self._format_diagram_response(result)
            print(response)
            
            # Add assistant response to history
            self.storage.add_to_history({
                "role": "assistant",
                "content": response,
                "diagram_url": result.get("export_url"),
                "elements_count": len(result.get("elements", []))
            })
            
        else:
            # Conversational response
            response = result.get("intent_response", "I'm not sure how to respond to that.")
            print(f"\n🤖 Assistant:\n{response}")
            
            # Add assistant response to history
            self.storage.add_to_history({
                "role": "assistant",
                "content": response,
                "is_diagram": False
            })

    def _format_diagram_response(self, result: Dict) -> str:
        """Format diagram response."""
        parts = [
            "\n" + "="*60,
            "📐 DIAGRAM GENERATED",
            "="*60
        ]
        
        concept = result.get("concept", {})
        if concept:
            topic = concept.get("topic", "Unknown topic")
            parts.append(f"📝 Topic: {topic}")
        
        components = result.get("components", {})
        if components:
            nodes = components.get("nodes", [])
            connections = components.get("connections", [])
            parts.append(f"🟦 Nodes: {len(nodes)}")
            parts.append(f"🔗 Connections: {len(connections)}")
        
        elements = result.get("elements", [])
        parts.append(f"📦 Total Elements: {len(elements)}")
        
        if result.get("export_url"):
            parts.append("\n" + "-"*60)
            parts.append("🔗 VIEW YOUR DIAGRAM:")
            parts.append(f"   {result['export_url']}")
            parts.append("="*60 + "\n")
        
        return "\n".join(parts)

    async def show_history(self):
        """Display recent chat history sessions."""
        sessions = await self.storage.list_sessions(limit=10)
        
        if not sessions:
            print("\n📭 No chat history found.")
            return
        
        print("\n" + "="*60)
        print("📜 RECENT CHAT SESSIONS")
        print("="*60)
        
        for i, session_info in enumerate(sessions, 1):
            print(f"{i}. {session_info['filename']}")
            print(f"   📅 {session_info['started_at']}")
            print(f"   💬 {session_info['message_count']} messages")
            print("-"*40)
        
        # Option to view a specific session
        try:
            choice = input("\nEnter session number to view details (or 'back' to return): ")
            if choice.lower() == 'back':
                return
            
            idx = int(choice) - 1
            if 0 <= idx < len(sessions):
                session_data = await self.storage.load_session(sessions[idx]['filename'])
                self._display_session_details(session_data)
        except (ValueError, IndexError):
            print("Invalid selection.")

    def _display_session_details(self, session_data: Dict):
        """Display detailed session information."""
        print("\n" + "="*60)
        print(f"📋 Session: {session_data.get('session_id', 'Unknown')}")
        print("="*60)
        
        for entry in session_data.get("history", []):
            role = entry.get("role", "").upper()
            content = entry.get("content", "")
            timestamp = entry.get("timestamp", "")
            
            print(f"\n[{role}] {timestamp}")
            print(content[:500] + "..." if len(content) > 500 else content)
            
            if entry.get("diagram_url"):
                print(f"🔗 Diagram: {entry['diagram_url']}")
            
            print("-"*40)

    def show_help(self):
        """Show help message."""
        print("\n" + "="*60)
        print("📚 HELP - Example Queries")
        print("="*60)
        print("\n📐 Diagram Requests:")
        print("  • 'Draw a diagram of a neural network'")
        print("  • 'Create a flowchart for user login'")
        print("  • 'Visualize the architecture of a transformer'")
        print("\n💬 General Questions:")
        print("  • 'What is machine learning?'")
        print("  • 'Explain the difference between AI and ML'")
        print("\n🛠️  Commands:")
        print("  • 'exit' - Quit and save chat")
        print("  • 'help' - Show this help")
        print("  • 'history' - View past sessions")
        print("="*60 + "\n")