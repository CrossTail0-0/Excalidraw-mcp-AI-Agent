import json
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime
import redis.asyncio as redis

class DiagramCache:
    """Simple Redis-based cache for diagram generation results."""
    
    def __init__(self, redis_url: Optional[str] = None, fallback_to_memory: bool = True):
        """
        Initialize Redis cache.
        
        Args:
            redis_url: Redis connection URL (e.g., redis://localhost:6379/0)
            fallback_to_memory: If True, uses in-memory cache if Redis is unavailable
        """
        self.redis_url = redis_url or "redis://localhost:6379/0"
        self.fallback_to_memory = fallback_to_memory
        self.cache_ttl = 3600 * 24 * 30  # 30 days default TTL
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                max_connections=10,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Test connection
            import asyncio
            asyncio.create_task(self._test_connection())
            print("✅ Redis cache initialized")
        except Exception as e:
            print(f"⚠️  Redis connection failed: {e}")
            if fallback_to_memory:
                print("   Using in-memory fallback...")
                self.redis_client = None
            else:
                raise
    
    async def _test_connection(self):
        """Test Redis connection."""
        try:
            await self.redis_client.ping()
            print("✅ Redis connection successful")
        except:
            print("⚠️  Redis connection test failed")
            if self.fallback_to_memory:
                print("   Using in-memory fallback...")
                self.redis_client = None
    
    def _generate_key(self, query: str) -> str:
        """Generate a unique key for a query."""
        normalized = ' '.join(query.lower().strip().split())
        return f"diagram_cache:{hashlib.sha256(normalized.encode()).hexdigest()}"
    
    async def get_cached_result(self, query: str) -> Optional[Dict[str, Any]]:
        """Get cached result."""
        key = self._generate_key(query)
        
        # Try Redis first
        if self.redis_client:
            try:
                data = await self.redis_client.get(key)
                if data:
                    print(f"✅ Cache HIT (Redis): {query[:50]}...")
                    return json.loads(data)
            except Exception as e:
                print(f"⚠️  Redis get error: {e}")
                if not self.fallback_to_memory:
                    return None
        
        # Fallback to memory
        if self.fallback_to_memory and key in self._memory_cache:
            print(f"✅ Cache HIT (Memory): {query[:50]}...")
            return self._memory_cache[key]
        
        print(f"❌ Cache MISS: {query[:50]}...")
        return None
    
    async def store_result(self, query: str, elements: List[Dict[str, Any]], 
                          export_url: str, metadata: Optional[Dict] = None) -> bool:
        """Store result in cache."""
        key = self._generate_key(query)
        
        cache_data = {
            "query": query,
            "query_key": key,
            "elements": elements,
            "export_url": export_url,
            "cached_at": datetime.now().isoformat(),
            "metadata": metadata or {},
            "elements_count": len(elements)
        }
        
        # Store in Redis
        if self.redis_client:
            try:
                await self.redis_client.setex(
                    key,
                    self.cache_ttl,
                    json.dumps(cache_data, ensure_ascii=False)
                )
                print(f"💾 Stored in Redis: {query[:50]}...")
                return True
            except Exception as e:
                print(f"⚠️  Redis store error: {e}")
                if not self.fallback_to_memory:
                    return False
        
        # Fallback to memory
        if self.fallback_to_memory:
            self._memory_cache[key] = cache_data
            print(f"💾 Stored in memory: {query[:50]}...")
            return True
        
        return False
    
    async def clear(self) -> bool:
        """Clear all cached data."""
        # Clear Redis
        if self.redis_client:
            try:
                pattern = "diagram_cache:*"
                cursor = 0
                deleted = 0
                
                while True:
                    cursor, keys = await self.redis_client.scan(cursor, match=pattern, count=100)
                    if keys:
                        await self.redis_client.delete(*keys)
                        deleted += len(keys)
                    if cursor == 0:
                        break
                
                print(f"✅ Cleared {deleted} Redis entries")
            except Exception as e:
                print(f"⚠️  Redis clear error: {e}")
        
        # Clear memory
        self._memory_cache.clear()
        print("✅ Cleared memory cache")
        return True
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = {
            "cache_type": "Redis" if self.redis_client else "Memory",
            "ttl_seconds": self.cache_ttl,
            "ttl_days": self.cache_ttl / (3600 * 24),
            "fallback_to_memory": self.fallback_to_memory,
            "memory_entries": len(self._memory_cache)
        }
        
        if self.redis_client:
            try:
                pattern = "diagram_cache:*"
                cursor = 0
                count = 0
                while True:
                    cursor, keys = await self.redis_client.scan(cursor, match=pattern, count=100)
                    count += len(keys)
                    if cursor == 0:
                        break
                
                stats["total_entries"] = count
                stats["status"] = "connected"
            except:
                stats["total_entries"] = len(self._memory_cache)
                stats["status"] = "error"
        else:
            stats["total_entries"] = len(self._memory_cache)
            stats["status"] = "memory_fallback"
        
        return stats
    
    async def list_entries(self, limit: int = 20) -> List[Dict[str, Any]]:
        """List cached entries."""
        entries = []
        
        # Get from Redis
        if self.redis_client:
            try:
                pattern = "diagram_cache:*"
                cursor = 0
                count = 0
                
                while True:
                    cursor, keys = await self.redis_client.scan(cursor, match=pattern, count=100)
                    
                    for key in keys[:limit - count]:
                        data = await self.redis_client.get(key)
                        if data:
                            try:
                                parsed = json.loads(data)
                                entries.append({
                                    "key": key.split(":")[1][:16] + "...",
                                    "query": parsed.get("query", "Unknown")[:100] + "..." if len(parsed.get("query", "")) > 100 else parsed.get("query", "Unknown"),
                                    "cached_at": parsed.get("cached_at", "Unknown"),
                                    "elements_count": parsed.get("elements_count", 0)
                                })
                                count += 1
                            except:
                                pass
                    
                    if cursor == 0 or count >= limit:
                        break
                
                return entries
            except Exception as e:
                print(f"⚠️  Redis list error: {e}")
        
        # Get from memory
        for key, data in list(self._memory_cache.items())[:limit]:
            entries.append({
                "key": key.split(":")[1][:16] + "...",
                "query": data.get("query", "Unknown")[:100] + "..." if len(data.get("query", "")) > 100 else data.get("query", "Unknown"),
                "cached_at": data.get("cached_at", "Unknown"),
                "elements_count": data.get("elements_count", 0)
            })
        
        return entries
    
    async def health_check(self) -> bool:
        """Check if Redis is healthy."""
        if self.redis_client:
            try:
                await self.redis_client.ping()
                return True
            except:
                return False
        return False