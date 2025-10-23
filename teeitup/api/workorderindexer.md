# WorkOrderIndexer Class

The `WorkOrderIndexer` class is the main orchestrator that coordinates work order discovery, indexing, and management.

## Overview

The `WorkOrderIndexer` provides a high-level interface for:
- Coordinating work order discovery from 8090 integrations
- Managing the work order index
- Providing search and filtering capabilities
- Handling data export/import operations
- Generating statistics and reports

## Class Definition

```python
class WorkOrderIndexer:
    def __init__(self, base_url: str = "https://factory.8090.ai"):
        self.base_url = base_url
        self.index = WorkOrderIndex()
        self.discovery = WorkOrderDiscovery(base_url)
        self.last_index_time: Optional[datetime] = None
```

## Constructor

### `__init__(base_url: str = "https://factory.8090.ai")`

Initializes the work order indexer with the specified base URL.

**Parameters**:
- `base_url`: Base URL of the 8090 service (default: "https://factory.8090.ai")

**Side Effects**:
- Creates a new `WorkOrderIndex` instance
- Creates a new `WorkOrderDiscovery` instance
- Initializes `last_index_time` to None

**Example**:
```python
# Default configuration
indexer = WorkOrderIndexer()

# Custom base URL
indexer = WorkOrderIndexer(base_url="https://custom.8090.ai")
```

## Methods

### `async index_work_orders() -> Dict[str, Any]`

Main method for indexing work orders from 8090 integrations.

**Returns**: Dictionary containing indexing statistics:
- `total_work_orders`: Total number of work orders in index
- `status_distribution`: Count by status
- `priority_distribution`: Count by priority
- `assigned_count`: Number of unique assignees
- `tags_count`: Number of unique tags
- `search_index_size`: Size of search index
- `indexing_duration`: Time taken for indexing
- `discovered_count`: Number of work orders discovered
- `indexed_count`: Number of work orders indexed

**Process**:
1. Initializes discovery client
2. Discovers work orders from 8090 service
3. Adds discovered work orders to index
4. Updates last index time
5. Generates and returns statistics

**Example**:
```python
async def index_work_orders():
    indexer = WorkOrderIndexer()
    stats = await indexer.index_work_orders()
    
    print(f"Indexed {stats['total_work_orders']} work orders")
    print(f"Duration: {stats['indexing_duration']:.2f} seconds")
    print(f"Status distribution: {stats['status_distribution']}")
```

### `get_queued_work_orders() -> List[WorkOrder]`

Retrieves all queued work orders.

**Returns**: List of work orders with status `QUEUED`

**Example**:
```python
queued_orders = indexer.get_queued_work_orders()
print(f"Found {len(queued_orders)} queued work orders")
```

### `search_work_orders(query: str) -> List[WorkOrder]`

Searches work orders using full-text search.

**Parameters**:
- `query`: Search query string

**Returns**: List of matching work orders

**Example**:
```python
# Search for work orders containing "bug" and "authentication"
results = indexer.search_work_orders("bug authentication")

# Search for urgent work orders
urgent_results = indexer.search_work_orders("urgent")
```

### `get_work_order_statistics() -> Dict[str, Any]`

Gets comprehensive work order statistics.

**Returns**: Dictionary containing:
- All statistics from `WorkOrderIndex.get_statistics()`
- `last_index_time`: ISO timestamp of last indexing operation

**Example**:
```python
stats = indexer.get_work_order_statistics()
print(f"Total work orders: {stats['total_work_orders']}")
print(f"Last indexed: {stats['last_index_time']}")
```

### `export_work_orders(filepath: str) -> None`

Exports work orders to a JSON file.

**Parameters**:
- `filepath`: Path to the output JSON file

**Side Effects**:
- Creates or overwrites the specified file
- Logs the export operation

**Example**:
```python
# Export to file
indexer.export_work_orders("work_orders_backup.json")

# Export with timestamp
from datetime import datetime
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
indexer.export_work_orders(f"work_orders_{timestamp}.json")
```

### `import_work_orders(filepath: str) -> None`

Imports work orders from a JSON file.

**Parameters**:
- `filepath`: Path to the input JSON file

**Side Effects**:
- Adds imported work orders to the index
- Logs the import operation

**Example**:
```python
# Import from file
indexer.import_work_orders("work_orders_backup.json")

# Import and verify
indexer.import_work_orders("work_orders.json")
stats = indexer.get_work_order_statistics()
print(f"Imported work orders. Total: {stats['total_work_orders']}")
```

## Usage Examples

### Basic Indexing

```python
import asyncio
from work_order_indexer import WorkOrderIndexer

async def main():
    # Create indexer
    indexer = WorkOrderIndexer()
    
    # Index work orders
    stats = await indexer.index_work_orders()
    
    print(f"✅ Indexing completed!")
    print(f"📊 Total work orders: {stats['total_work_orders']}")
    print(f"⏱️  Duration: {stats['indexing_duration']:.2f} seconds")

asyncio.run(main())
```

### Search and Filter

```python
async def search_example():
    indexer = WorkOrderIndexer()
    
    # Index work orders first
    await indexer.index_work_orders()
    
    # Search for specific terms
    bug_orders = indexer.search_work_orders("bug")
    print(f"Found {len(bug_orders)} bug-related work orders")
    
    # Get queued work orders
    queued_orders = indexer.get_queued_work_orders()
    print(f"Found {len(queued_orders)} queued work orders")
    
    # Get statistics
    stats = indexer.get_work_order_statistics()
    print(f"Status distribution: {stats['status_distribution']}")

asyncio.run(search_example())
```

### Export and Import

```python
async def export_import_example():
    indexer = WorkOrderIndexer()
    
    # Index work orders
    await indexer.index_work_orders()
    
    # Export to file
    indexer.export_work_orders("work_orders_export.json")
    print("Work orders exported")
    
    # Create new indexer and import
    new_indexer = WorkOrderIndexer()
    new_indexer.import_work_orders("work_orders_export.json")
    
    # Verify import
    stats = new_indexer.get_work_order_statistics()
    print(f"Imported {stats['total_work_orders']} work orders")

asyncio.run(export_import_example())
```

### Error Handling

```python
async def safe_indexing():
    indexer = WorkOrderIndexer()
    
    try:
        stats = await indexer.index_work_orders()
        print(f"Successfully indexed {stats['total_work_orders']} work orders")
    except Exception as e:
        print(f"Indexing failed: {e}")
        # Handle error appropriately
        return
    
    # Continue with other operations
    queued_orders = indexer.get_queued_work_orders()
    print(f"Found {len(queued_orders)} queued work orders")
```

## Configuration

### Environment Variables

The indexer can be configured using environment variables:

```bash
export FACTORY_8090_BASE_URL="https://factory.8090.ai"
export WORK_ORDER_TIMEOUT="30"
export WORK_ORDER_HEADLESS="true"
```

### Custom Configuration

```python
# Custom base URL
indexer = WorkOrderIndexer(base_url="https://custom.8090.ai")

# Access underlying components
index = indexer.index  # WorkOrderIndex instance
discovery = indexer.discovery  # WorkOrderDiscovery instance
```

## Performance Considerations

### Indexing Performance
- **Discovery Time**: Depends on service response time
- **Indexing Time**: O(n) where n is number of work orders
- **Memory Usage**: O(n) for work order storage
- **Search Performance**: O(k) where k is query complexity

### Optimization Tips
1. **Batch Operations**: Index multiple work orders at once
2. **Caching**: Cache results for repeated queries
3. **Pagination**: Process large datasets in chunks
4. **Monitoring**: Track performance metrics

## Error Handling

### Common Errors

**Discovery Errors**:
- Network connectivity issues
- Service unavailability
- Authentication failures
- Rate limiting

**Indexing Errors**:
- Data parsing failures
- Invalid work order data
- Index corruption
- Memory issues

**Search Errors**:
- Invalid search queries
- Index not found
- Permission errors

### Error Recovery

```python
async def robust_indexing():
    indexer = WorkOrderIndexer()
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            stats = await indexer.index_work_orders()
            print(f"Indexing successful on attempt {attempt + 1}")
            break
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                print("All attempts failed")
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

## Logging

The indexer uses structured logging for all operations:

- **INFO**: Major operations (indexing start/end, export/import)
- **DEBUG**: Detailed operation information
- **ERROR**: Error conditions and failures
- **WARNING**: Non-fatal issues and fallbacks

## Thread Safety

The `WorkOrderIndexer` class is **not thread-safe**. For multi-threaded environments:

1. Use separate indexer instances per thread
2. Implement appropriate locking mechanisms
3. Consider using asyncio for concurrent operations

## Best Practices

1. **Resource Management**: Always use async context managers
2. **Error Handling**: Implement comprehensive error handling
3. **Logging**: Use structured logging for debugging
4. **Performance**: Monitor and optimize for your use case
5. **Data Validation**: Validate data before indexing
6. **Backup**: Regularly export data for backup purposes