# Basic Usage Examples

This document provides basic examples for getting started with the Work Order Indexing System.

## Quick Start

### 1. Installation and Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install

# Verify installation
python work_order_cli.py --help
```

### 2. First Indexing

```bash
# Index work orders from 8090 integrations
python work_order_cli.py index --export work_orders.json

# Check what was discovered
python work_order_cli.py stats
```

### 3. Basic Operations

```bash
# List all work orders
python work_order_cli.py list

# Search for specific work orders
python work_order_cli.py search "bug"

# Show details of a specific work order
python work_order_cli.py show WO-1
```

## Python API Examples

### Basic Indexing

```python
import asyncio
from work_order_indexer import WorkOrderIndexer

async def basic_indexing():
    # Create indexer
    indexer = WorkOrderIndexer()
    
    # Index work orders
    stats = await indexer.index_work_orders()
    
    print(f"Indexed {stats['total_work_orders']} work orders")
    print(f"Duration: {stats['indexing_duration']:.2f} seconds")
    
    return indexer

# Run the example
indexer = asyncio.run(basic_indexing())
```

### Creating Work Orders

```python
from work_order_indexer import WorkOrder, WorkOrderStatus, WorkOrderPriority
from datetime import datetime

# Create a work order
work_order = WorkOrder(
    id="WO-123",
    title="Fix authentication bug",
    description="Users cannot log in with special characters in passwords",
    status=WorkOrderStatus.QUEUED,
    priority=WorkOrderPriority.HIGH,
    created_at=datetime.now(),
    updated_at=datetime.now(),
    assigned_to="developer@company.com",
    tags=["bug", "authentication", "urgent"],
    metadata={
        "component": "auth",
        "version": "2.1.0",
        "estimated_hours": 4
    }
)

print(f"Created work order: {work_order.title}")
print(f"Status: {work_order.status.value}")
print(f"Priority: {work_order.priority.value}")
```

### Adding Work Orders to Index

```python
from work_order_indexer import WorkOrderIndex, WorkOrder, WorkOrderStatus, WorkOrderPriority
from datetime import datetime

# Create index
index = WorkOrderIndex()

# Create work orders
work_orders = [
    WorkOrder(
        id="WO-1",
        title="Fix login bug",
        description="Users cannot log in",
        status=WorkOrderStatus.QUEUED,
        priority=WorkOrderPriority.HIGH,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        assigned_to="dev@company.com",
        tags=["bug", "login"]
    ),
    WorkOrder(
        id="WO-2",
        title="Add new feature",
        description="Implement user dashboard",
        status=WorkOrderStatus.IN_PROGRESS,
        priority=WorkOrderPriority.MEDIUM,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        assigned_to="frontend@company.com",
        tags=["feature", "dashboard"]
    )
]

# Add to index
for wo in work_orders:
    index.add_work_order(wo)

print(f"Added {len(work_orders)} work orders to index")
```

### Searching Work Orders

```python
# Search by text
results = index.search_work_orders("bug")
print(f"Found {len(results)} work orders containing 'bug'")

# Search by status
queued_orders = index.get_work_orders_by_status(WorkOrderStatus.QUEUED)
print(f"Found {len(queued_orders)} queued work orders")

# Search by priority
high_priority = index.get_work_orders_by_priority(WorkOrderPriority.HIGH)
print(f"Found {len(high_priority)} high priority work orders")

# Search by assignee
dev_orders = index.get_work_orders_by_assigned("dev@company.com")
print(f"Found {len(dev_orders)} work orders assigned to dev@company.com")

# Search by tag
bug_orders = index.get_work_orders_by_tag("bug")
print(f"Found {len(bug_orders)} work orders tagged as 'bug'")
```

### Getting Statistics

```python
# Get comprehensive statistics
stats = index.get_statistics()

print("Work Order Statistics:")
print(f"Total work orders: {stats['total_work_orders']}")
print(f"Status distribution: {stats['status_distribution']}")
print(f"Priority distribution: {stats['priority_distribution']}")
print(f"Assigned work orders: {stats['assigned_count']}")
print(f"Unique tags: {stats['tags_count']}")
print(f"Search index size: {stats['search_index_size']}")
```

### Export and Import

```python
# Export to JSON
json_data = index.export_to_json()
print("Exported work orders to JSON")

# Save to file
with open("work_orders.json", "w") as f:
    f.write(json_data)

# Import from JSON
new_index = WorkOrderIndex()
new_index.import_from_json(json_data)

# Verify import
imported_stats = new_index.get_statistics()
print(f"Imported {imported_stats['total_work_orders']} work orders")
```

## CLI Examples

### Daily Workflow

```bash
# Morning: Check queued work orders
python work_order_cli.py list --status queued --limit 10

# Search for urgent items
python work_order_cli.py search "urgent"

# Check work assigned to you
python work_order_cli.py list --assigned your-email@company.com

# Get overall statistics
python work_order_cli.py stats
```

### Data Management

```bash
# Create backup
python work_order_cli.py export --output backup_$(date +%Y%m%d).json

# Restore from backup
python work_order_cli.py import --input backup_20251023.json

# Index and export in one command
python work_order_cli.py index --export daily_export.json
```

### Filtering and Analysis

```bash
# Find all high priority work orders
python work_order_cli.py list --priority high

# Find work orders with specific tag
python work_order_cli.py list --tag "security"

# Search for work orders containing multiple terms
python work_order_cli.py search "dashboard feature"

# Get top 10 most recent work orders
python work_order_cli.py list --limit 10
```

## Error Handling Examples

### Basic Error Handling

```python
import asyncio
from work_order_indexer import WorkOrderIndexer

async def safe_indexing():
    try:
        indexer = WorkOrderIndexer()
        stats = await indexer.index_work_orders()
        print(f"Successfully indexed {stats['total_work_orders']} work orders")
    except Exception as e:
        print(f"Indexing failed: {e}")
        return None
    
    return indexer

# Run with error handling
indexer = asyncio.run(safe_indexing())
if indexer:
    print("Indexing completed successfully")
else:
    print("Indexing failed")
```

### Retry Logic

```python
import asyncio
import time
from work_order_indexer import WorkOrderIndexer

async def retry_indexing(max_retries=3):
    for attempt in range(max_retries):
        try:
            indexer = WorkOrderIndexer()
            stats = await indexer.index_work_orders()
            print(f"Indexing successful on attempt {attempt + 1}")
            return indexer
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Waiting {wait_time} seconds before retry...")
                await asyncio.sleep(wait_time)
            else:
                print("All attempts failed")
                raise
    
    return None

# Run with retry logic
indexer = asyncio.run(retry_indexing())
```

### Validation

```python
from work_order_indexer import WorkOrder, WorkOrderStatus, WorkOrderPriority
from datetime import datetime

def create_work_order_safely(data):
    try:
        # Validate required fields
        required_fields = ['id', 'title', 'description', 'status', 'priority']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate status
        if data['status'] not in [s.value for s in WorkOrderStatus]:
            raise ValueError(f"Invalid status: {data['status']}")
        
        # Validate priority
        if data['priority'] not in [p.value for p in WorkOrderPriority]:
            raise ValueError(f"Invalid priority: {data['priority']}")
        
        # Create work order
        work_order = WorkOrder(
            id=data['id'],
            title=data['title'],
            description=data['description'],
            status=WorkOrderStatus(data['status']),
            priority=WorkOrderPriority(data['priority']),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            assigned_to=data.get('assigned_to'),
            tags=data.get('tags', []),
            metadata=data.get('metadata', {})
        )
        
        return work_order
        
    except Exception as e:
        print(f"Error creating work order: {e}")
        return None

# Example usage
data = {
    'id': 'WO-123',
    'title': 'Fix bug',
    'description': 'Fix the bug',
    'status': 'queued',
    'priority': 'high',
    'assigned_to': 'dev@company.com',
    'tags': ['bug', 'urgent']
}

work_order = create_work_order_safely(data)
if work_order:
    print(f"Created work order: {work_order.title}")
else:
    print("Failed to create work order")
```

## Configuration Examples

### Environment Variables

```bash
# Set environment variables
export FACTORY_8090_BASE_URL="https://factory.8090.ai"
export WORK_ORDER_TIMEOUT="30"
export WORK_ORDER_HEADLESS="true"
export LOG_LEVEL="INFO"

# Run with environment variables
python work_order_cli.py index
```

### Configuration File

```python
# config.py
import os

class Config:
    BASE_URL = os.getenv('FACTORY_8090_BASE_URL', 'https://factory.8090.ai')
    TIMEOUT = int(os.getenv('WORK_ORDER_TIMEOUT', '30'))
    HEADLESS = os.getenv('WORK_ORDER_HEADLESS', 'true').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate(cls):
        if not cls.BASE_URL.startswith('http'):
            raise ValueError("BASE_URL must be a valid HTTP URL")
        if cls.TIMEOUT <= 0:
            raise ValueError("TIMEOUT must be positive")
        return True

# Use configuration
config = Config()
config.validate()

indexer = WorkOrderIndexer(base_url=config.BASE_URL)
```

## Best Practices

### Code Organization

```python
# work_order_manager.py
import asyncio
from typing import List, Optional
from work_order_indexer import WorkOrderIndexer, WorkOrder

class WorkOrderManager:
    def __init__(self, base_url: str = "https://factory.8090.ai"):
        self.indexer = WorkOrderIndexer(base_url)
        self._initialized = False
    
    async def initialize(self):
        """Initialize the manager"""
        if not self._initialized:
            await self.indexer.index_work_orders()
            self._initialized = True
    
    async def get_queued_work_orders(self) -> List[WorkOrder]:
        """Get queued work orders"""
        await self.initialize()
        return self.indexer.get_queued_work_orders()
    
    async def search_work_orders(self, query: str) -> List[WorkOrder]:
        """Search work orders"""
        await self.initialize()
        return self.indexer.search_work_orders(query)
    
    async def get_statistics(self):
        """Get statistics"""
        await self.initialize()
        return self.indexer.get_work_order_statistics()

# Usage
async def main():
    manager = WorkOrderManager()
    
    # Get queued work orders
    queued = await manager.get_queued_work_orders()
    print(f"Found {len(queued)} queued work orders")
    
    # Search for work orders
    results = await manager.search_work_orders("bug")
    print(f"Found {len(results)} work orders containing 'bug'")
    
    # Get statistics
    stats = await manager.get_statistics()
    print(f"Total work orders: {stats['total_work_orders']}")

asyncio.run(main())
```

### Resource Management

```python
import asyncio
from contextlib import asynccontextmanager
from work_order_indexer import WorkOrderIndexer

@asynccontextmanager
async def work_order_indexer(base_url: str = "https://factory.8090.ai"):
    """Context manager for work order indexer"""
    indexer = WorkOrderIndexer(base_url)
    try:
        yield indexer
    finally:
        # Cleanup if needed
        pass

# Usage with context manager
async def main():
    async with work_order_indexer() as indexer:
        stats = await indexer.index_work_orders()
        print(f"Indexed {stats['total_work_orders']} work orders")
        
        # Use indexer for other operations
        queued = indexer.get_queued_work_orders()
        print(f"Found {len(queued)} queued work orders")

asyncio.run(main())
```