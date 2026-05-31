"""
Eira Nexus - Centralized Memory Module
======================================
Single point of truth for all memory read/write operations.
Only the Nexus core can write; interfaces can only read via this API.
"""
import os
import time
import json
from pathlib import Path

class EiraMemory:
    """Centralized memory access layer for the Eira cognitive system."""
    
    def __init__(self, config_path: str = None):
        """Initialize memory with configuration."""
        self.config = self._load_config(config_path)
        self.memory_path = Path(self.config.get("memory", {}).get("path", "D:/Digital Lab/Eira's Library/Core_Memory"))
        self._ensure_memory_exists()
    
    def _load_config(self, config_path: str) -> dict:
        """Load identity configuration."""
        if config_path and os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        
        # Default config path
        default_path = Path(__file__).parent.parent / "identity.json"
        if default_path.exists():
            with open(default_path, "r", encoding="utf-8") as f:
                return json.load(f)
        
        return {}
    
    def _ensure_memory_exists(self):
        """Create memory directory if it doesn't exist."""
        if not self.memory_path.exists():
            print(f"📁 Creating memory directory: {self.memory_path}")
            self.memory_path.mkdir(parents=True, exist_ok=True)
    
    def load_all(self) -> str:
        """
        Read all memory files (.md, .txt) and return combined context.
        This is the READ operation available to all components.
        """
        combined_memory = ""
        
        if not self.memory_path.exists():
            return "No hay memoria previa."
        
        print("🧠 Loading Memory...")
        try:
            for file_path in self.memory_path.iterdir():
                if file_path.suffix in [".md", ".txt"]:
                    try:
                        content = file_path.read_text(encoding="utf-8")
                        combined_memory += f"\n--- MEMORY FILE: {file_path.name} ---\n{content}\n"
                        print(f"  + Loaded: {file_path.name}")
                    except Exception as e:
                        print(f"  x Error reading {file_path.name}: {e}")
        except Exception as e:
            print(f"Error accessing memory: {e}")
        
        return combined_memory
    
    def load_file(self, filename: str) -> str:
        """Read a specific memory file."""
        file_path = self.memory_path / filename
        if file_path.exists():
            return file_path.read_text(encoding="utf-8")
        return ""
    
    def get(self, key: str) -> str:
        """
        Get a specific value from memory (for simple key-value lookups).
        Currently reads from User_Profile.md for known keys.
        """
        # Simple key-value extraction from User_Profile
        profile_content = self.load_file("User_Profile.md")
        
        # Basic parsing (can be enhanced)
        for line in profile_content.split("\n"):
            if key.lower() in line.lower():
                if ":" in line:
                    return line.split(":", 1)[1].strip()
        
        return ""
    
    def remember(self, concept: str, source: str = "nexus") -> bool:
        """
        Write a concept to the persistent Neural_Patterns.md file.
        ONLY the Nexus core should call this (enforced by source check).
        
        Args:
            concept: The information to remember
            source: The caller identifier (must be "nexus" to write)
        
        Returns:
            True if successful, False otherwise
        """
        # Enforce write permissions
        writable_by = self.config.get("memory", {}).get("writable_by", ["nexus"])
        if source not in writable_by:
            print(f"❌ Memory Write Denied: {source} is not authorized")
            return False
        
        memory_file = self.memory_path / "Neural_Patterns.md"
        timestamp = time.strftime("%Y-%m-%d %H:%M")
        
        entry = f"\n- [LEARNED {timestamp}]: {concept}"
        
        try:
            with open(memory_file, "a", encoding="utf-8") as f:
                f.write(entry)
            print(f"💾 MEMORY SAVED: {concept}")
            return True
        except Exception as e:
            print(f"❌ Memory Write Error: {e}")
            return False
    
    def get_stats(self) -> dict:
        """Return memory statistics."""
        stats = {
            "path": str(self.memory_path),
            "exists": self.memory_path.exists(),
            "files": 0,
            "total_size": 0
        }
        
        if self.memory_path.exists():
            files = list(self.memory_path.iterdir())
            stats["files"] = len([f for f in files if f.is_file()])
            stats["total_size"] = sum(f.stat().st_size for f in files if f.is_file())
        
        return stats


# Singleton instance for global access
_memory_instance = None

def get_memory() -> EiraMemory:
    """Get the global memory instance."""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = EiraMemory()
    return _memory_instance
