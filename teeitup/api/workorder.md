# WorkOrder Class

The `WorkOrder` class is the core data structure representing a work order in the system.

## Overview

A `WorkOrder` represents a single work item with all its associated metadata, status, priority, and assignment information.

## Class Definition

```python
@dataclass
class WorkOrder:
    id: str
    title: str
    description: str
    status: WorkOrderStatus
    priority: WorkOrderPriority
    created_at: datetime
    updated_at: datetime
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    tags: List[str] = None
    metadata: Dict[str, Any] = None
    source: str = "8090_factory"
```

## Fields

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Unique identifier for the work order |
| `title` | `str` | Human-readable title of the work order |
| `description` | `str` | Detailed description of the work order |
| `status` | `WorkOrderStatus` | Current status of the work order |
| `priority` | `WorkOrderPriority` | Priority level of the work order |
| `created_at` | `datetime` | When the work order was created |
| `updated_at` | `datetime` | When the work order was last updated |

### Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `assigned_to` | `Optional[str]` | `None` | Email or identifier of the assignee |
| `due_date` | `Optional[datetime]` | `None` | When the work order is due |
| `tags` | `List[str]` | `[]` | List of tags for categorization |
| `metadata` | `Dict[str, Any]` | `{}` | Additional metadata |
| `source` | `str` | `"8090_factory"` | Source system identifier |

## Methods

### `to_dict() -> Dict[str, Any]`

Converts the work order to a dictionary for serialization.

**Returns**: Dictionary representation of the work order

**Example**:
```python
work_order = WorkOrder(...)
data = work_order.to_dict()
# Returns: {
#     "id": "WO-1",
#     "title": "Fix bug",
#     "status": "queued",
#     "priority": "high",
#     "created_at": "2025-10-23T10:30:00",
#     ...
# }
```

### `from_dict(data: Dict[str, Any]) -> WorkOrder`

Creates a work order from a dictionary (class method).

**Parameters**:
- `data`: Dictionary containing work order data

**Returns**: New `WorkOrder` instance

**Example**:
```python
data = {
    "id": "WO-1",
    "title": "Fix bug",
    "status": "queued",
    "priority": "high",
    "created_at": "2025-10-23T10:30:00",
    "updated_at": "2025-10-23T10:30:00"
}
work_order = WorkOrder.from_dict(data)
```

## Status Values

The `status` field uses the `WorkOrderStatus` enum:

- `QUEUED` - Work order is queued for processing
- `IN_PROGRESS` - Work order is currently being worked on
- `COMPLETED` - Work order has been completed
- `FAILED` - Work order failed during processing
- `CANCELLED` - Work order was cancelled
- `PENDING_APPROVAL` - Work order is waiting for approval
- `ON_HOLD` - Work order is temporarily on hold

## Priority Values

The `priority` field uses the `WorkOrderPriority` enum:

- `LOW` - Low priority work order
- `MEDIUM` - Medium priority work order
- `HIGH` - High priority work order
- `URGENT` - Urgent work order
- `CRITICAL` - Critical work order

## Usage Examples

### Creating a Work Order

```python
from datetime import datetime
from work_order_indexer import WorkOrder, WorkOrderStatus, WorkOrderPriority

# Create a new work order
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
```

### Serialization

```python
# Convert to dictionary for JSON serialization
data = work_order.to_dict()

# Save to file
import json
with open("work_order.json", "w") as f:
    json.dump(data, f, indent=2)

# Load from file
with open("work_order.json", "r") as f:
    data = json.load(f)
    work_order = WorkOrder.from_dict(data)
```

### Accessing Fields

```python
# Access basic information
print(f"Work Order: {work_order.title}")
print(f"Status: {work_order.status.value}")
print(f"Priority: {work_order.priority.value}")

# Check if assigned
if work_order.assigned_to:
    print(f"Assigned to: {work_order.assigned_to}")

# Check tags
if "urgent" in work_order.tags:
    print("This is an urgent work order")

# Access metadata
if "estimated_hours" in work_order.metadata:
    hours = work_order.metadata["estimated_hours"]
    print(f"Estimated hours: {hours}")
```

## Data Validation

The `WorkOrder` class includes automatic validation:

- **Required fields**: All required fields must be provided
- **Type validation**: Fields are validated against their expected types
- **Enum validation**: Status and priority must be valid enum values
- **Default values**: Optional fields are automatically initialized with defaults

## Error Handling

Common errors when working with `WorkOrder`:

- **Invalid status**: `ValueError` if status is not a valid `WorkOrderStatus`
- **Invalid priority**: `ValueError` if priority is not a valid `WorkOrderPriority`
- **Invalid datetime**: `ValueError` if datetime strings cannot be parsed
- **Missing required fields**: `TypeError` if required fields are missing

## Best Practices

1. **Use descriptive titles**: Make titles clear and specific
2. **Include detailed descriptions**: Provide enough context for assignees
3. **Use appropriate tags**: Tag work orders for easy filtering and categorization
4. **Set realistic due dates**: Use due dates to help with prioritization
5. **Keep metadata minimal**: Only include essential metadata to avoid bloat
6. **Update timestamps**: Always update `updated_at` when modifying work orders