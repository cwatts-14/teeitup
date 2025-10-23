# Work Order Indexing for 8090 Integrations

A comprehensive system for discovering, indexing, and managing work orders from the Factory.8090.ai service.

## 🎯 Overview

This system provides:
- **Automatic discovery** of work orders from 8090 integrations
- **Full-text search** capabilities across work orders
- **Status and priority filtering** for work order management
- **Export/import** functionality for data portability
- **Real-time statistics** and monitoring
- **Command-line interface** for easy operation

## 🚀 Quick Start

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:
```bash
playwright install
```

### Basic Usage

1. **Index work orders from 8090 integrations:**
```bash
python work_order_cli.py index --export work_orders.json
```

2. **List queued work orders:**
```bash
python work_order_cli.py list --status queued --limit 10
```

3. **Search for specific work orders:**
```bash
python work_order_cli.py search "urgent bug fix"
```

4. **View statistics:**
```bash
python work_order_cli.py stats
```

## 📋 Features

### Work Order Discovery
- **Browser automation** to discover work orders from the 8090 service
- **API endpoint detection** for direct data access
- **JavaScript analysis** to find hidden work order data
- **Network traffic monitoring** to capture work order information

### Indexing and Search
- **Full-text search** across work order titles, descriptions, and tags
- **Status filtering** (queued, in_progress, completed, failed, etc.)
- **Priority filtering** (low, medium, high, urgent, critical)
- **Assignee filtering** to find work assigned to specific people
- **Tag-based filtering** for categorized work orders

### Data Management
- **JSON export/import** for data portability
- **Real-time statistics** and reporting
- **Work order details** with complete metadata
- **Timestamp tracking** for created/updated dates

## 🛠️ Components

### Core Classes

#### `WorkOrder`
Data structure representing a work order with:
- Basic information (ID, title, description)
- Status and priority
- Timestamps (created, updated, due date)
- Assignment information
- Tags and metadata

#### `WorkOrderIndex`
Searchable index of work orders with:
- Full-text search capabilities
- Status and priority indexing
- Assignee and tag indexing
- Statistics generation

#### `WorkOrderDiscovery`
Discovers work orders from 8090 integrations using:
- Browser automation with Playwright
- API endpoint discovery
- JavaScript analysis
- Network traffic monitoring

#### `WorkOrderIndexer`
Main orchestrator that:
- Coordinates discovery and indexing
- Provides high-level operations
- Manages data export/import

### CLI Commands

#### `index`
Index work orders from 8090 integrations
```bash
python work_order_cli.py index [--export FILE]
```

#### `list`
List work orders with optional filtering
```bash
python work_order_cli.py list [--status STATUS] [--priority PRIORITY] [--assigned USER] [--tag TAG] [--limit N]
```

#### `search`
Search work orders by text query
```bash
python work_order_cli.py search "query"
```

#### `stats`
Show work order statistics
```bash
python work_order_cli.py stats
```

#### `show`
Show details of a specific work order
```bash
python work_order_cli.py show WORK_ORDER_ID
```

#### `export`
Export work orders to JSON
```bash
python work_order_cli.py export --output FILE
```

#### `import`
Import work orders from JSON
```bash
python work_order_cli.py import --input FILE
```

## 📊 Work Order Status and Priority

### Status Values
- `queued` - Work order is queued for processing
- `in_progress` - Work order is currently being worked on
- `completed` - Work order has been completed
- `failed` - Work order failed during processing
- `cancelled` - Work order was cancelled
- `pending_approval` - Work order is waiting for approval
- `on_hold` - Work order is temporarily on hold

### Priority Values
- `low` - Low priority work order
- `medium` - Medium priority work order
- `high` - High priority work order
- `urgent` - Urgent work order
- `critical` - Critical work order

## 🔍 Search Capabilities

The system provides powerful search functionality:

### Full-Text Search
Search across work order titles, descriptions, and tags:
```python
results = indexer.search_work_orders("authentication bug")
```

### Status Filtering
Filter work orders by status:
```python
queued_orders = indexer.index.get_work_orders_by_status(WorkOrderStatus.QUEUED)
```

### Priority Filtering
Filter work orders by priority:
```python
urgent_orders = indexer.index.get_work_orders_by_priority(WorkOrderPriority.URGENT)
```

### Assignee Filtering
Find work orders assigned to specific people:
```python
assigned_orders = indexer.index.get_work_orders_by_assigned("developer@company.com")
```

### Tag Filtering
Filter work orders by tags:
```python
bug_orders = indexer.index.get_work_orders_by_tag("bug")
```

## 📈 Statistics and Reporting

The system provides comprehensive statistics:

### Basic Statistics
- Total number of work orders
- Status distribution
- Priority distribution
- Assignment information
- Tag usage

### Indexing Statistics
- Discovery duration
- Number of work orders discovered
- Number of work orders indexed
- Last indexing time

### Export Statistics
- Export timestamp
- Number of exported work orders
- File size and location

## 🔧 Configuration

### Environment Variables
- `FACTORY_8090_BASE_URL` - Base URL for the 8090 service (default: https://factory.8090.ai)
- `WORK_ORDER_TIMEOUT` - Timeout for operations in seconds (default: 30)
- `WORK_ORDER_HEADLESS` - Run browser in headless mode (default: true)

### Browser Configuration
The system uses Playwright for browser automation. You can configure:
- Browser type (Chromium, Firefox, WebKit)
- Headless mode
- Viewport size
- User agent

## 🚨 Error Handling

The system includes comprehensive error handling:

### Discovery Errors
- Network connectivity issues
- Service unavailability
- Authentication failures
- Rate limiting

### Indexing Errors
- Data parsing failures
- Invalid work order data
- Index corruption
- Memory issues

### Search Errors
- Invalid search queries
- Index not found
- Permission errors

## 📝 Logging

The system uses structured logging with:
- **JSON format** for easy parsing
- **Multiple log levels** (DEBUG, INFO, WARNING, ERROR)
- **Contextual information** for debugging
- **Performance metrics** for monitoring

## 🔒 Security Considerations

### Data Protection
- **No sensitive data** stored in plain text
- **Secure credential management** for authentication
- **Data encryption** for exported files
- **Access control** for work order data

### Network Security
- **HTTPS only** for all communications
- **Request signing** for API calls
- **Rate limiting** to prevent abuse
- **Input validation** for all data

## 🧪 Testing

### Unit Tests
```bash
python -m pytest tests/unit/
```

### Integration Tests
```bash
python -m pytest tests/integration/
```

### End-to-End Tests
```bash
python -m pytest tests/e2e/
```

## 📚 Examples

### Basic Indexing
```python
from work_order_indexer import WorkOrderIndexer

async def index_work_orders():
    indexer = WorkOrderIndexer()
    stats = await indexer.index_work_orders()
    print(f"Indexed {stats['total_work_orders']} work orders")
```

### Search and Filter
```python
# Search for urgent work orders
urgent_orders = indexer.search_work_orders("urgent")

# Filter by status
queued_orders = indexer.index.get_work_orders_by_status(WorkOrderStatus.QUEUED)

# Filter by priority
high_priority = indexer.index.get_work_orders_by_priority(WorkOrderPriority.HIGH)
```

### Export and Import
```python
# Export work orders
indexer.export_work_orders("backup.json")

# Import work orders
indexer.import_work_orders("backup.json")
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the examples
- Contact the development team

## 🔄 Changelog

### Version 1.0.0
- Initial release
- Work order discovery and indexing
- Full-text search capabilities
- CLI interface
- Export/import functionality
- Comprehensive statistics and reporting