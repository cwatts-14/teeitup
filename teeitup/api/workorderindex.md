# WorkOrderIndex Class

The `WorkOrderIndex` class provides indexing and search capabilities for work orders.

## Overview

The `WorkOrderIndex` is a multi-dimensional indexing system that enables fast searching and filtering of work orders by various criteria including status, priority, assignee, tags, and full-text content.

## Class Definition

```python
class WorkOrderIndex:
    def __init__(self):
        self.work_orders: Dict[str, WorkOrder] = {}
        self.index_by_status: Dict[WorkOrderStatus, List[str]] = {}
        self.index_by_priority: Dict[WorkOrderPriority, List[str]] = {}
        self.index_by_assigned: Dict[str, List[str]] = {}
        self.index_by_tags: Dict[str, List[str]] = {}
        self.search_index: Dict[str, List[str]] = {}
```

## Index Structure

The index maintains multiple data structures for efficient querying:

- **`work_orders`**: Primary storage of work order objects by ID
- **`index_by_status`**: Maps status values to lists of work order IDs
- **`index_by_priority`**: Maps priority values to lists of work order IDs
- **`index_by_assigned`**: Maps assignee emails to lists of work order IDs
- **`index_by_tags`**: Maps tag names to lists of work order IDs
- **`search_index`**: Maps search terms to lists of work order IDs

## Methods

### `add_work_order(work_order: WorkOrder) -> None`

Adds a work order to the index and updates all relevant indexes.

**Parameters**:
- `work_order`: The work order to add

**Side Effects**:
- Updates all index structures
- Logs the addition with structured logging

**Example**:
```python
index = WorkOrderIndex()
work_order = WorkOrder(...)
index.add_work_order(work_order)
```

### `get_work_order(work_order_id: str) -> Optional[WorkOrder]`

Retrieves a work order by its ID.

**Parameters**:
- `work_order_id`: The unique identifier of the work order

**Returns**: The work order if found, `None` otherwise

**Example**:
```python
work_order = index.get_work_order("WO-123")
if work_order:
    print(f"Found: {work_order.title}")
else:
    print("Work order not found")
```

### `search_work_orders(query: str) -> List[WorkOrder]`

Performs full-text search across work order titles, descriptions, and tags.

**Parameters**:
- `query`: Search query string

**Returns**: List of matching work orders

**Search Behavior**:
- Tokenizes the query into individual words
- Finds work orders that contain ALL query words
- Case-insensitive matching
- Searches across title, description, and tags

**Example**:
```python
# Find work orders containing both "bug" and "authentication"
results = index.search_work_orders("bug authentication")

# Find work orders containing "urgent"
results = index.search_work_orders("urgent")
```

### `get_work_orders_by_status(status: WorkOrderStatus) -> List[WorkOrder]`

Retrieves all work orders with a specific status.

**Parameters**:
- `status`: The status to filter by

**Returns**: List of work orders with the specified status

**Example**:
```python
queued_orders = index.get_work_orders_by_status(WorkOrderStatus.QUEUED)
in_progress_orders = index.get_work_orders_by_status(WorkOrderStatus.IN_PROGRESS)
```

### `get_work_orders_by_priority(priority: WorkOrderPriority) -> List[WorkOrder]`

Retrieves all work orders with a specific priority.

**Parameters**:
- `priority`: The priority to filter by

**Returns**: List of work orders with the specified priority

**Example**:
```python
high_priority = index.get_work_orders_by_priority(WorkOrderPriority.HIGH)
urgent_orders = index.get_work_orders_by_priority(WorkOrderPriority.URGENT)
```

### `get_work_orders_by_assigned(assigned_to: str) -> List[WorkOrder]`

Retrieves all work orders assigned to a specific person.

**Parameters**:
- `assigned_to`: Email or identifier of the assignee

**Returns**: List of work orders assigned to the specified person

**Example**:
```python
developer_orders = index.get_work_orders_by_assigned("developer@company.com")
```

### `get_work_orders_by_tag(tag: str) -> List[WorkOrder]`

Retrieves all work orders with a specific tag.

**Parameters**:
- `tag`: The tag to filter by

**Returns**: List of work orders with the specified tag

**Example**:
```python
bug_orders = index.get_work_orders_by_tag("bug")
urgent_orders = index.get_work_orders_by_tag("urgent")
```

### `get_queued_work_orders() -> List[WorkOrder]`

Convenience method to get all queued work orders.

**Returns**: List of work orders with status `QUEUED`

**Example**:
```python
queued_orders = index.get_queued_work_orders()
print(f"Found {len(queued_orders)} queued work orders")
```

### `get_statistics() -> Dict[str, Any]`

Generates comprehensive statistics about the indexed work orders.

**Returns**: Dictionary containing:
- `total_work_orders`: Total number of work orders
- `status_distribution`: Count of work orders by status
- `priority_distribution`: Count of work orders by priority
- `assigned_count`: Number of unique assignees
- `tags_count`: Number of unique tags
- `search_index_size`: Number of search terms in the index

**Example**:
```python
stats = index.get_statistics()
print(f"Total work orders: {stats['total_work_orders']}")
print(f"Queued: {stats['status_distribution']['queued']}")
print(f"High priority: {stats['priority_distribution']['high']}")
```

### `export_to_json() -> str`

Exports all work orders and statistics to JSON format.

**Returns**: JSON string containing work orders and statistics

**Example**:
```python
json_data = index.export_to_json()
with open("work_orders.json", "w") as f:
    f.write(json_data)
```

### `import_from_json(json_data: str) -> None`

Imports work orders from JSON data.

**Parameters**:
- `json_data`: JSON string containing work order data

**Side Effects**:
- Adds all work orders from the JSON to the index
- Logs the import operation

**Example**:
```python
with open("work_orders.json", "r") as f:
    json_data = f.read()
index.import_from_json(json_data)
```

## Usage Examples

### Basic Indexing

```python
from work_order_indexer import WorkOrderIndex, WorkOrder, WorkOrderStatus, WorkOrderPriority
from datetime import datetime

# Create index
index = WorkOrderIndex()

# Create work orders
work_order1 = WorkOrder(
    id="WO-1",
    title="Fix authentication bug",
    description="Users cannot log in with special characters",
    status=WorkOrderStatus.QUEUED,
    priority=WorkOrderPriority.HIGH,
    created_at=datetime.now(),
    updated_at=datetime.now(),
    assigned_to="developer@company.com",
    tags=["bug", "authentication"]
)

work_order2 = WorkOrder(
    id="WO-2",
    title="Implement new feature",
    description="Add user dashboard functionality",
    status=WorkOrderStatus.IN_PROGRESS,
    priority=WorkOrderPriority.MEDIUM,
    created_at=datetime.now(),
    updated_at=datetime.now(),
    assigned_to="frontend@company.com",
    tags=["feature", "dashboard"]
)

# Add to index
index.add_work_order(work_order1)
index.add_work_order(work_order2)
```

### Searching and Filtering

```python
# Full-text search
results = index.search_work_orders("authentication")
print(f"Found {len(results)} work orders containing 'authentication'")

# Status filtering
queued_orders = index.get_work_orders_by_status(WorkOrderStatus.QUEUED)
print(f"Found {len(queued_orders)} queued work orders")

# Priority filtering
high_priority = index.get_work_orders_by_priority(WorkOrderPriority.HIGH)
print(f"Found {len(high_priority)} high priority work orders")

# Assignee filtering
dev_orders = index.get_work_orders_by_assigned("developer@company.com")
print(f"Found {len(dev_orders)} work orders assigned to developer")

# Tag filtering
bug_orders = index.get_work_orders_by_tag("bug")
print(f"Found {len(bug_orders)} work orders tagged as 'bug'")
```

### Statistics and Export

```python
# Get statistics
stats = index.get_statistics()
print(f"Total work orders: {stats['total_work_orders']}")
print(f"Status distribution: {stats['status_distribution']}")
print(f"Priority distribution: {stats['priority_distribution']}")

# Export to JSON
json_data = index.export_to_json()
with open("work_orders_backup.json", "w") as f:
    f.write(json_data)
```

## Performance Characteristics

- **Add Operation**: O(1) for work order addition
- **Status/Priority Lookup**: O(1) for indexed lookups
- **Search Operation**: O(k) where k is the number of query words
- **Memory Usage**: O(n) where n is the total number of work orders
- **Index Size**: O(n * m) where m is the average number of searchable terms per work order

## Thread Safety

The `WorkOrderIndex` class is **not thread-safe**. If you need to use it in a multi-threaded environment, you should implement appropriate locking mechanisms.

## Error Handling

The index handles errors gracefully:

- **Invalid work order IDs**: Returns `None` for non-existent IDs
- **Empty search results**: Returns empty list for queries with no matches
- **Invalid enum values**: Raises `ValueError` for invalid status/priority values
- **JSON parsing errors**: Raises `JSONDecodeError` for malformed JSON data