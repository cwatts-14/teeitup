# Advanced Usage Patterns

This document covers advanced patterns and techniques for using the Work Order Indexing System in complex scenarios.

## Asynchronous Patterns

### Concurrent Indexing

```python
import asyncio
from work_order_indexer import WorkOrderIndexer
from typing import List

async def concurrent_indexing(urls: List[str]) -> List[WorkOrderIndexer]:
    """Index work orders from multiple sources concurrently"""
    
    async def index_single_source(url: str) -> WorkOrderIndexer:
        indexer = WorkOrderIndexer(base_url=url)
        await indexer.index_work_orders()
        return indexer
    
    # Create tasks for concurrent execution
    tasks = [index_single_source(url) for url in urls]
    
    # Wait for all tasks to complete
    indexers = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter out exceptions
    successful_indexers = [idx for idx in indexers if isinstance(idx, WorkOrderIndexer)]
    
    return successful_indexers

# Usage
urls = [
    "https://factory.8090.ai",
    "https://backup.8090.ai",
    "https://test.8090.ai"
]

indexers = asyncio.run(concurrent_indexing(urls))
print(f"Successfully indexed from {len(indexers)} sources")
```

### Batch Processing

```python
import asyncio
from work_order_indexer import WorkOrderIndexer, WorkOrder
from typing import List

async def batch_process_work_orders(work_orders: List[WorkOrder], batch_size: int = 10):
    """Process work orders in batches"""
    
    async def process_batch(batch: List[WorkOrder]) -> List[WorkOrder]:
        """Process a single batch of work orders"""
        # Simulate processing (e.g., API calls, database updates)
        await asyncio.sleep(0.1)  # Simulate work
        
        # Update work order status
        for wo in batch:
            wo.status = WorkOrderStatus.IN_PROGRESS
            wo.updated_at = datetime.now()
        
        return batch
    
    # Split work orders into batches
    batches = [work_orders[i:i + batch_size] for i in range(0, len(work_orders), batch_size)]
    
    # Process batches concurrently
    tasks = [process_batch(batch) for batch in batches]
    results = await asyncio.gather(*tasks)
    
    # Flatten results
    processed_work_orders = [wo for batch in results for wo in batch]
    
    return processed_work_orders

# Usage
work_orders = [/* list of work orders */]
processed = await batch_process_work_orders(work_orders, batch_size=5)
print(f"Processed {len(processed)} work orders in batches")
```

## Custom Search Implementations

### Fuzzy Search

```python
from difflib import SequenceMatcher
from typing import List
from work_order_indexer import WorkOrder

class FuzzySearchEngine:
    def __init__(self, threshold: float = 0.6):
        self.threshold = threshold
    
    def search(self, query: str, work_orders: List[WorkOrder]) -> List[WorkOrder]:
        """Perform fuzzy search on work orders"""
        results = []
        query_lower = query.lower()
        
        for wo in work_orders:
            # Search in title
            title_score = self._calculate_similarity(query_lower, wo.title.lower())
            
            # Search in description
            desc_score = self._calculate_similarity(query_lower, wo.description.lower())
            
            # Search in tags
            tag_scores = [self._calculate_similarity(query_lower, tag.lower()) for tag in wo.tags]
            max_tag_score = max(tag_scores) if tag_scores else 0
            
            # Calculate overall score
            overall_score = max(title_score, desc_score, max_tag_score)
            
            if overall_score >= self.threshold:
                results.append((wo, overall_score))
        
        # Sort by score (highest first)
        results.sort(key=lambda x: x[1], reverse=True)
        
        return [wo for wo, score in results]
    
    def _calculate_similarity(self, a: str, b: str) -> float:
        """Calculate similarity between two strings"""
        return SequenceMatcher(None, a, b).ratio()

# Usage
fuzzy_search = FuzzySearchEngine(threshold=0.7)
results = fuzzy_search.search("auth bug", work_orders)
print(f"Found {len(results)} fuzzy matches")
```

### Advanced Filtering

```python
from typing import List, Optional, Callable
from work_order_indexer import WorkOrder, WorkOrderStatus, WorkOrderPriority
from datetime import datetime, timedelta

class AdvancedFilter:
    def __init__(self, work_orders: List[WorkOrder]):
        self.work_orders = work_orders
    
    def filter_by_status(self, status: WorkOrderStatus) -> 'AdvancedFilter':
        """Filter by status"""
        self.work_orders = [wo for wo in self.work_orders if wo.status == status]
        return self
    
    def filter_by_priority(self, priority: WorkOrderPriority) -> 'AdvancedFilter':
        """Filter by priority"""
        self.work_orders = [wo for wo in self.work_orders if wo.priority == priority]
        return self
    
    def filter_by_assignee(self, assignee: str) -> 'AdvancedFilter':
        """Filter by assignee"""
        self.work_orders = [wo for wo in self.work_orders if wo.assigned_to == assignee]
        return self
    
    def filter_by_tag(self, tag: str) -> 'AdvancedFilter':
        """Filter by tag"""
        self.work_orders = [wo for wo in self.work_orders if tag in wo.tags]
        return self
    
    def filter_by_date_range(self, start_date: datetime, end_date: datetime) -> 'AdvancedFilter':
        """Filter by date range"""
        self.work_orders = [
            wo for wo in self.work_orders 
            if start_date <= wo.created_at <= end_date
        ]
        return self
    
    def filter_by_custom(self, predicate: Callable[[WorkOrder], bool]) -> 'AdvancedFilter':
        """Filter by custom predicate"""
        self.work_orders = [wo for wo in self.work_orders if predicate(wo)]
        return self
    
    def get_results(self) -> List[WorkOrder]:
        """Get filtered results"""
        return self.work_orders

# Usage
filtered = (AdvancedFilter(work_orders)
    .filter_by_status(WorkOrderStatus.QUEUED)
    .filter_by_priority(WorkOrderPriority.HIGH)
    .filter_by_date_range(
        datetime.now() - timedelta(days=7),
        datetime.now()
    )
    .get_results())

print(f"Found {len(filtered)} work orders matching criteria")
```

## Event-Driven Architecture

### Work Order Events

```python
from typing import List, Callable
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

class WorkOrderEventType(Enum):
    CREATED = "created"
    UPDATED = "updated"
    STATUS_CHANGED = "status_changed"
    PRIORITY_CHANGED = "priority_changed"
    ASSIGNED = "assigned"
    COMPLETED = "completed"

@dataclass
class WorkOrderEvent:
    event_type: WorkOrderEventType
    work_order: WorkOrder
    timestamp: datetime
    metadata: dict = None

class WorkOrderEventBus:
    def __init__(self):
        self.subscribers: List[Callable[[WorkOrderEvent], None]] = []
    
    def subscribe(self, callback: Callable[[WorkOrderEvent], None]):
        """Subscribe to work order events"""
        self.subscribers.append(callback)
    
    def publish(self, event: WorkOrderEvent):
        """Publish a work order event"""
        for callback in self.subscribers:
            try:
                callback(event)
            except Exception as e:
                print(f"Error in event handler: {e}")
    
    def unsubscribe(self, callback: Callable[[WorkOrderEvent], None]):
        """Unsubscribe from work order events"""
        if callback in self.subscribers:
            self.subscribers.remove(callback)

# Event handlers
def log_event(event: WorkOrderEvent):
    print(f"Event: {event.event_type.value} - {event.work_order.title}")

def notify_team(event: WorkOrderEvent):
    if event.event_type == WorkOrderEventType.ASSIGNED:
        print(f"Notification: {event.work_order.title} assigned to {event.work_order.assigned_to}")

def update_dashboard(event: WorkOrderEvent):
    print(f"Dashboard update: {event.event_type.value} for {event.work_order.id}")

# Usage
event_bus = WorkOrderEventBus()
event_bus.subscribe(log_event)
event_bus.subscribe(notify_team)
event_bus.subscribe(update_dashboard)

# Publish events
event = WorkOrderEvent(
    event_type=WorkOrderEventType.CREATED,
    work_order=work_order,
    timestamp=datetime.now()
)
event_bus.publish(event)
```

### Observer Pattern

```python
from abc import ABC, abstractmethod
from typing import List
from work_order_indexer import WorkOrder

class WorkOrderObserver(ABC):
    @abstractmethod
    def update(self, work_order: WorkOrder):
        """Update observer with work order changes"""
        pass

class WorkOrderSubject:
    def __init__(self):
        self.observers: List[WorkOrderObserver] = []
        self.work_orders: List[WorkOrder] = []
    
    def attach(self, observer: WorkOrderObserver):
        """Attach an observer"""
        self.observers.append(observer)
    
    def detach(self, observer: WorkOrderObserver):
        """Detach an observer"""
        if observer in self.observers:
            self.observers.remove(observer)
    
    def notify(self, work_order: WorkOrder):
        """Notify all observers"""
        for observer in self.observers:
            observer.update(work_order)
    
    def add_work_order(self, work_order: WorkOrder):
        """Add work order and notify observers"""
        self.work_orders.append(work_order)
        self.notify(work_order)

# Concrete observers
class WorkOrderLogger(WorkOrderObserver):
    def update(self, work_order: WorkOrder):
        print(f"Log: New work order {work_order.id} - {work_order.title}")

class WorkOrderNotifier(WorkOrderObserver):
    def update(self, work_order: WorkOrder):
        if work_order.assigned_to:
            print(f"Notification: {work_order.title} assigned to {work_order.assigned_to}")

class WorkOrderDashboard(WorkOrderObserver):
    def update(self, work_order: WorkOrder):
        print(f"Dashboard: Updated with {work_order.title}")

# Usage
subject = WorkOrderSubject()
subject.attach(WorkOrderLogger())
subject.attach(WorkOrderNotifier())
subject.attach(WorkOrderDashboard())

# Add work order (triggers notifications)
subject.add_work_order(work_order)
```

## Caching Strategies

### Memory Cache

```python
from typing import Dict, Optional, Any
import time
from work_order_indexer import WorkOrder

class WorkOrderCache:
    def __init__(self, ttl: int = 300):  # 5 minutes TTL
        self.cache: Dict[str, Any] = {}
        self.ttl = ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any):
        """Set value in cache"""
        self.cache[key] = (value, time.time())
    
    def invalidate(self, key: str):
        """Invalidate cache entry"""
        if key in self.cache:
            del self.cache[key]
    
    def clear(self):
        """Clear all cache entries"""
        self.cache.clear()

# Cached work order indexer
class CachedWorkOrderIndexer(WorkOrderIndexer):
    def __init__(self, base_url: str = "https://factory.8090.ai", cache_ttl: int = 300):
        super().__init__(base_url)
        self.cache = WorkOrderCache(cache_ttl)
    
    async def get_cached_work_orders(self) -> List[WorkOrder]:
        """Get work orders with caching"""
        cache_key = "work_orders"
        cached_work_orders = self.cache.get(cache_key)
        
        if cached_work_orders is not None:
            return cached_work_orders
        
        # Cache miss - fetch from source
        await self.index_work_orders()
        work_orders = list(self.index.work_orders.values())
        
        # Cache the result
        self.cache.set(cache_key, work_orders)
        
        return work_orders
    
    def invalidate_cache(self):
        """Invalidate work orders cache"""
        self.cache.invalidate("work_orders")

# Usage
cached_indexer = CachedWorkOrderIndexer(cache_ttl=600)  # 10 minutes
work_orders = await cached_indexer.get_cached_work_orders()
```

### Redis Cache

```python
import redis
import json
from typing import List, Optional
from work_order_indexer import WorkOrder

class RedisWorkOrderCache:
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        self.redis_client = redis.Redis(host=host, port=port, db=db)
    
    def get_work_orders(self, key: str) -> Optional[List[WorkOrder]]:
        """Get work orders from Redis cache"""
        cached_data = self.redis_client.get(key)
        if cached_data:
            data = json.loads(cached_data)
            return [WorkOrder.from_dict(wo_data) for wo_data in data]
        return None
    
    def set_work_orders(self, key: str, work_orders: List[WorkOrder], ttl: int = 300):
        """Set work orders in Redis cache"""
        data = [wo.to_dict() for wo in work_orders]
        self.redis_client.setex(key, ttl, json.dumps(data))
    
    def invalidate(self, key: str):
        """Invalidate cache entry"""
        self.redis_client.delete(key)

# Usage
redis_cache = RedisWorkOrderCache()
cached_work_orders = redis_cache.get_work_orders("work_orders")
if not cached_work_orders:
    # Fetch from source and cache
    work_orders = await indexer.index_work_orders()
    redis_cache.set_work_orders("work_orders", work_orders, ttl=600)
```

## Performance Optimization

### Lazy Loading

```python
from typing import List, Optional
from work_order_indexer import WorkOrder

class LazyWorkOrderIndexer:
    def __init__(self, base_url: str = "https://factory.8090.ai"):
        self.base_url = base_url
        self._indexer: Optional[WorkOrderIndexer] = None
        self._work_orders: Optional[List[WorkOrder]] = None
    
    @property
    def indexer(self) -> WorkOrderIndexer:
        """Lazy initialization of indexer"""
        if self._indexer is None:
            self._indexer = WorkOrderIndexer(self.base_url)
        return self._indexer
    
    async def get_work_orders(self) -> List[WorkOrder]:
        """Lazy loading of work orders"""
        if self._work_orders is None:
            await self.indexer.index_work_orders()
            self._work_orders = list(self.indexer.index.work_orders.values())
        return self._work_orders
    
    def search_work_orders(self, query: str) -> List[WorkOrder]:
        """Search work orders (loads if needed)"""
        if self._work_orders is None:
            raise RuntimeError("Work orders not loaded. Call get_work_orders() first.")
        return self.indexer.search_work_orders(query)

# Usage
lazy_indexer = LazyWorkOrderIndexer()
work_orders = await lazy_indexer.get_work_orders()  # Loads on first access
```

### Connection Pooling

```python
import asyncio
from typing import List
from work_order_indexer import WorkOrderIndexer

class WorkOrderIndexerPool:
    def __init__(self, base_url: str, pool_size: int = 5):
        self.base_url = base_url
        self.pool_size = pool_size
        self.pool: List[WorkOrderIndexer] = []
        self.available: List[WorkOrderIndexer] = []
        self._lock = asyncio.Lock()
    
    async def initialize(self):
        """Initialize the connection pool"""
        for _ in range(self.pool_size):
            indexer = WorkOrderIndexer(self.base_url)
            await indexer.index_work_orders()
            self.pool.append(indexer)
            self.available.append(indexer)
    
    async def get_indexer(self) -> WorkOrderIndexer:
        """Get an available indexer from the pool"""
        async with self._lock:
            if not self.available:
                raise RuntimeError("No available indexers in pool")
            return self.available.pop()
    
    async def return_indexer(self, indexer: WorkOrderIndexer):
        """Return an indexer to the pool"""
        async with self._lock:
            self.available.append(indexer)
    
    async def close(self):
        """Close all indexers in the pool"""
        for indexer in self.pool:
            # Close any resources if needed
            pass

# Usage
pool = WorkOrderIndexerPool("https://factory.8090.ai", pool_size=3)
await pool.initialize()

# Use indexer from pool
indexer = await pool.get_indexer()
try:
    work_orders = indexer.get_queued_work_orders()
    print(f"Found {len(work_orders)} queued work orders")
finally:
    await pool.return_indexer(indexer)

await pool.close()
```

## Monitoring and Metrics

### Performance Metrics

```python
import time
from typing import Dict, Any
from work_order_indexer import WorkOrderIndexer

class MetricsCollector:
    def __init__(self):
        self.metrics: Dict[str, Any] = {}
        self.start_times: Dict[str, float] = {}
    
    def start_timer(self, operation: str):
        """Start timing an operation"""
        self.start_times[operation] = time.time()
    
    def end_timer(self, operation: str):
        """End timing an operation"""
        if operation in self.start_times:
            duration = time.time() - self.start_times[operation]
            self.metrics[f"{operation}_duration"] = duration
            del self.start_times[operation]
    
    def increment_counter(self, counter: str, value: int = 1):
        """Increment a counter"""
        if counter not in self.metrics:
            self.metrics[counter] = 0
        self.metrics[counter] += value
    
    def set_gauge(self, gauge: str, value: Any):
        """Set a gauge value"""
        self.metrics[gauge] = value
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all metrics"""
        return self.metrics.copy()

# Instrumented work order indexer
class InstrumentedWorkOrderIndexer(WorkOrderIndexer):
    def __init__(self, base_url: str = "https://factory.8090.ai"):
        super().__init__(base_url)
        self.metrics = MetricsCollector()
    
    async def index_work_orders(self) -> Dict[str, Any]:
        """Index work orders with metrics collection"""
        self.metrics.start_timer("indexing")
        self.metrics.increment_counter("indexing_attempts")
        
        try:
            stats = await super().index_work_orders()
            self.metrics.increment_counter("indexing_successes")
            self.metrics.set_gauge("total_work_orders", stats['total_work_orders'])
            return stats
        except Exception as e:
            self.metrics.increment_counter("indexing_failures")
            raise
        finally:
            self.metrics.end_timer("indexing")
    
    def search_work_orders(self, query: str) -> List[WorkOrder]:
        """Search work orders with metrics collection"""
        self.metrics.start_timer("search")
        self.metrics.increment_counter("search_queries")
        
        try:
            results = super().search_work_orders(query)
            self.metrics.set_gauge("search_results_count", len(results))
            return results
        finally:
            self.metrics.end_timer("search")

# Usage
indexer = InstrumentedWorkOrderIndexer()
stats = await indexer.index_work_orders()
print(f"Metrics: {indexer.metrics.get_metrics()}")
```

These advanced patterns provide powerful tools for building sophisticated work order management systems with proper error handling, performance optimization, and monitoring capabilities.