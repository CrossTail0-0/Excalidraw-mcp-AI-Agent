import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import aiofiles

class ChatHistoryStorage:
    """Simple chat history storage with flat file structure."""
    
    def __init__(self, storage_dir: str = "CHAT_HISTORY"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Current session data
        self.current_session_id: Optional[str] = None
        self.current_history: List[Dict[str, Any]] = []
    
    def start_new_session(self) -> str:
        """Start a new chat session and generate a session ID."""
        # Generate session ID with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_session_id = f"chat_history_{timestamp}"
        self.current_history = []
        return self.current_session_id
    
    def add_to_history(self, entry: Dict[str, Any]):
        """Add an entry to the current session history."""
        if not self.current_session_id:
            self.start_new_session()
        
        # Add timestamp if not present
        if "timestamp" not in entry:
            entry["timestamp"] = datetime.now().isoformat()
        
        self.current_history.append(entry)
    
    async def save_current_session(self) -> str:
        """Save the current chat history to a file."""
        if not self.current_session_id or not self.current_history:
            return ""
        
        # Create the filename
        filename = f"{self.current_session_id}.json"
        filepath = self.storage_dir / filename
        
        # Prepare data
        data = {
            "session_id": self.current_session_id,
            "started_at": self.current_history[0].get("timestamp", datetime.now().isoformat()) if self.current_history else datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "history": self.current_history
        }
        
        # Write to file
        async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(data, indent=2, ensure_ascii=False))
        
        return str(filepath)
    
    async def load_session(self, filename: str) -> Dict[str, Any]:
        """Load a specific chat history file."""
        filepath = self.storage_dir / filename
        if not filepath.exists():
            return {}
        
        async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
            content = await f.read()
            return json.loads(content)
    
    async def list_sessions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List all available chat history files."""
        sessions = []
        
        # Get all JSON files in the directory
        files = list(self.storage_dir.glob("chat_history_*.json"))
        files.sort(reverse=True)  # Most recent first
        
        for filepath in files[:limit]:
            try:
                data = await self.load_session(filepath.name)
                sessions.append({
                    "filename": filepath.name,
                    "session_id": data.get("session_id", filepath.name),
                    "started_at": data.get("started_at", ""),
                    "message_count": len(data.get("history", [])),
                    "filepath": str(filepath)
                })
            except Exception as e:
                print(f"Error loading {filepath.name}: {e}")
        
        return sessions
    
    def get_current_history(self) -> List[Dict[str, Any]]:
        """Get the current session's history."""
        return self.current_history
    
    def clear_current_session(self):
        """Clear the current session data."""
        self.current_session_id = None
        self.current_history = []