import json
from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class SourceManager:
    def __init__(self, sources_file: str = "sources.json"):
        self.sources_file = Path(sources_file)
        self.sources_data = self._load_sources()
    
    def _load_sources(self) -> Dict[str, Any]:
        if self.sources_file.exists():
            with open(self.sources_file, 'r') as f:
                return json.load(f)
        return {"sources": [], "blacklist": []}
    
    def _save_sources(self) -> None:
        with open(self.sources_file, 'w') as f:
            json.dump(self.sources_data, f, indent=2)
    
    def get_active_sources(self) -> List[Dict[str, Any]]:
        return [
            source for source in self.sources_data["sources"]
            if source["active"] and source["url"] not in self.sources_data["blacklist"]
        ]
    
    def add_source(self, name: str, url: str, source_type: str = "rss", 
                   category: str = "general") -> bool:
        for source in self.sources_data["sources"]:
            if source["url"] == url:
                logger.warning(f"Source {url} already exists")
                return False
        
        new_source = {
            "name": name,
            "url": url,
            "type": source_type,
            "category": category,
            "active": True
        }
        self.sources_data["sources"].append(new_source)
        self._save_sources()
        logger.info(f"Added source: {name}")
        return True
    
    def remove_source(self, url: str) -> bool:
        initial_count = len(self.sources_data["sources"])
        self.sources_data["sources"] = [
            s for s in self.sources_data["sources"] if s["url"] != url
        ]
        if len(self.sources_data["sources"]) < initial_count:
            self._save_sources()
            logger.info(f"Removed source: {url}")
            return True
        logger.warning(f"Source {url} not found")
        return False
    
    def blacklist_source(self, url: str) -> bool:
        if url not in self.sources_data["blacklist"]:
            self.sources_data["blacklist"].append(url)
            self._save_sources()
            logger.info(f"Blacklisted source: {url}")
            return True
        logger.warning(f"Source {url} already blacklisted")
        return False
    
    def unblacklist_source(self, url: str) -> bool:
        if url in self.sources_data["blacklist"]:
            self.sources_data["blacklist"].remove(url)
            self._save_sources()
            logger.info(f"Removed {url} from blacklist")
            return True
        logger.warning(f"Source {url} not in blacklist")
        return False
    
    def toggle_source(self, url: str) -> bool:
        for source in self.sources_data["sources"]:
            if source["url"] == url:
                source["active"] = not source["active"]
                self._save_sources()
                status = "activated" if source["active"] else "deactivated"
                logger.info(f"Source {source['name']} {status}")
                return True
        logger.warning(f"Source {url} not found")
        return False
    
    def list_sources(self, category: str = None) -> List[Dict[str, Any]]:
        sources = self.sources_data["sources"]
        if category:
            sources = [s for s in sources if s["category"] == category]
        return sources