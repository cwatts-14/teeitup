# WorkOrderDiscovery Class

The `WorkOrderDiscovery` class handles the discovery of work orders from the Factory.8090.ai service using browser automation and API analysis.

## Overview

The `WorkOrderDiscovery` class provides comprehensive work order discovery capabilities through:
- Browser automation with Playwright
- API endpoint discovery and analysis
- JavaScript data extraction
- Network traffic monitoring
- Request/response interception

## Class Definition

```python
class WorkOrderDiscovery:
    def __init__(self, base_url: str = "https://factory.8090.ai"):
        self.base_url = base_url
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.session: Optional[httpx.AsyncClient] = None
```

## Initialization

### Constructor

```python
discovery = WorkOrderDiscovery(base_url="https://factory.8090.ai")
```

**Parameters**:
- `base_url`: Base URL of the 8090 service (default: "https://factory.8090.ai")

## Context Manager

The class supports async context manager protocol for proper resource management:

```python
async with WorkOrderDiscovery() as discovery:
    work_orders = await discovery.discover_work_orders()
```

## Methods

### `async initialize() -> None`

Initializes the discovery client with browser automation and HTTP client.

**Side Effects**:
- Launches Chromium browser in headless mode
- Creates HTTP client with appropriate headers
- Sets up request interception
- Logs initialization status

**Example**:
```python
discovery = WorkOrderDiscovery()
await discovery.initialize()
```

### `async close() -> None`

Closes the discovery client and cleans up resources.

**Side Effects**:
- Closes HTTP client session
- Closes browser instance
- Logs cleanup status

**Example**:
```python
await discovery.close()
```

### `async discover_work_orders() -> List[WorkOrder]`

Main method for discovering work orders from the 8090 service.

**Returns**: List of discovered work orders

**Process**:
1. Navigates to the service URL
2. Waits for page to load completely
3. Extracts work order data from the page
4. Follows work order related links
5. Discovers work orders from API endpoints
6. Returns all discovered work orders

**Example**:
```python
async with WorkOrderDiscovery() as discovery:
    work_orders = await discovery.discover_work_orders()
    print(f"Discovered {len(work_orders)} work orders")
```

### `async _extract_work_orders_from_page() -> List[WorkOrder]`

Extracts work order data from the current page using JavaScript analysis.

**Returns**: List of work orders found on the current page

**Process**:
1. Executes JavaScript to find work order data patterns
2. Looks for common work order data structures
3. Extracts data from global objects
4. Converts extracted data to WorkOrder objects

**Example**:
```python
# This method is called internally by discover_work_orders()
page_work_orders = await discovery._extract_work_orders_from_page()
```

### `async _discover_work_orders_from_apis() -> List[WorkOrder]`

Discovers work orders by testing common API endpoints.

**Returns**: List of work orders found via API calls

**API Endpoints Tested**:
- `/api/work-orders`
- `/api/work_orders`
- `/api/tasks`
- `/api/jobs`
- `/api/queue`
- `/api/orders`
- `/api/v1/work-orders`
- `/api/v1/tasks`
- `/api/v1/jobs`
- `/api/v2/work-orders`
- `/api/v2/tasks`
- `/api/v2/jobs`

**Example**:
```python
# This method is called internally by discover_work_orders()
api_work_orders = await discovery._discover_work_orders_from_apis()
```

### `async _extract_work_orders_from_dict(data: Dict[str, Any], source_url: str) -> List[WorkOrder]`

Extracts work orders from dictionary data structures.

**Parameters**:
- `data`: Dictionary containing potential work order data
- `source_url`: URL where the data was found

**Returns**: List of extracted work orders

**Data Patterns Searched**:
- `work_orders`, `workOrders`
- `tasks`, `jobs`, `orders`
- `queue`, `pending`, `assigned`
- `work_items`

**Example**:
```python
# This method is called internally during data processing
work_orders = await discovery._extract_work_orders_from_dict(data, "https://api.example.com/work-orders")
```

### `async _create_work_order_from_data(data: Dict[str, Any], source_url: str) -> Optional[WorkOrder]`

Creates a WorkOrder object from raw data dictionary.

**Parameters**:
- `data`: Raw data dictionary
- `source_url`: Source URL for metadata

**Returns**: WorkOrder object if successful, None otherwise

**Data Mapping**:
- `id` → work order ID (generates hash if missing)
- `title`/`name`/`subject` → work order title
- `description`/`details`/`summary` → work order description
- `status`/`state` → work order status
- `priority`/`urgency` → work order priority
- `assigned_to`/`assignee`/`owner` → assignee
- `tags`/`labels`/`categories` → tags list

**Example**:
```python
# This method is called internally during data processing
raw_data = {
    "id": "WO-123",
    "title": "Fix bug",
    "status": "queued",
    "priority": "high"
}
work_order = await discovery._create_work_order_from_data(raw_data, "https://api.example.com")
```

### `_parse_timestamp(timestamp: Any) -> datetime`

Parses timestamps from various formats.

**Parameters**:
- `timestamp`: Timestamp in various formats (string, int, float, datetime)

**Returns**: Parsed datetime object

**Supported Formats**:
- ISO 8601 strings
- Unix timestamps (int/float)
- Common date formats
- Uses dateutil parser as fallback

**Example**:
```python
# This method is called internally during data processing
timestamp = discovery._parse_timestamp("2025-10-23T10:30:00Z")
```

## Usage Examples

### Basic Discovery

```python
import asyncio
from work_order_indexer import WorkOrderDiscovery

async def discover_work_orders():
    async with WorkOrderDiscovery() as discovery:
        work_orders = await discovery.discover_work_orders()
        
        print(f"Discovered {len(work_orders)} work orders:")
        for wo in work_orders:
            print(f"- {wo.title} ({wo.status.value})")

asyncio.run(discover_work_orders())
```

### Custom Base URL

```python
async def discover_from_custom_url():
    async with WorkOrderDiscovery(base_url="https://custom.8090.ai") as discovery:
        work_orders = await discovery.discover_work_orders()
        return work_orders
```

### Error Handling

```python
async def safe_discovery():
    try:
        async with WorkOrderDiscovery() as discovery:
            work_orders = await discovery.discover_work_orders()
            return work_orders
    except Exception as e:
        print(f"Discovery failed: {e}")
        return []
```

## Configuration

### Environment Variables

The discovery client can be configured using environment variables:

```bash
export FACTORY_8090_BASE_URL="https://factory.8090.ai"
export WORK_ORDER_TIMEOUT="30"
export WORK_ORDER_HEADLESS="true"
```

### Browser Configuration

The browser automation uses Playwright with the following defaults:
- **Browser**: Chromium
- **Mode**: Headless
- **Timeout**: 30 seconds
- **User Agent**: "Work Order Discovery Client/1.0"

### HTTP Client Configuration

The HTTP client is configured with:
- **Base URL**: Factory.8090.ai
- **Timeout**: 30 seconds
- **Headers**: Accept JSON and HTML content
- **User Agent**: "Work Order Discovery Client/1.0"

## Error Handling

The discovery process handles various error conditions:

### Network Errors
- Connection timeouts
- DNS resolution failures
- SSL certificate issues
- HTTP error responses

### Browser Errors
- Page load failures
- JavaScript execution errors
- Element interaction failures
- Navigation timeouts

### Data Processing Errors
- Invalid JSON responses
- Malformed work order data
- Missing required fields
- Type conversion failures

## Logging

The discovery process uses structured logging with the following log levels:

- **INFO**: Major operations (initialization, discovery start/end)
- **DEBUG**: Detailed operation information
- **ERROR**: Error conditions and failures
- **WARNING**: Non-fatal issues and fallbacks

## Performance Considerations

### Timeout Settings
- **Page Load**: 30 seconds default
- **Network Requests**: 30 seconds default
- **JavaScript Execution**: 5 seconds default

### Resource Usage
- **Memory**: Browser automation uses significant memory
- **CPU**: JavaScript execution and page rendering
- **Network**: Multiple API calls and page navigation

### Optimization Tips
1. Use headless mode for better performance
2. Limit the number of links followed
3. Implement appropriate timeouts
4. Monitor resource usage in production

## Security Considerations

### Credential Management
- Never hardcode credentials
- Use environment variables for sensitive data
- Implement proper authentication handling

### Data Privacy
- Be mindful of sensitive work order data
- Implement appropriate access controls
- Follow data protection regulations

### Network Security
- Use HTTPS for all communications
- Validate SSL certificates
- Implement proper error handling to avoid information leakage