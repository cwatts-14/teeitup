# CLI Commands Reference

The Work Order CLI provides a comprehensive command-line interface for managing work orders from 8090 integrations.

## Command Structure

```bash
python work_order_cli.py <command> [options]
```

## Available Commands

### `index` - Index Work Orders

Indexes work orders from 8090 integrations and optionally exports them.

```bash
python work_order_cli.py index [--export FILE]
```

**Options**:
- `--export FILE`: Export indexed work orders to JSON file

**Example**:
```bash
# Index work orders
python work_order_cli.py index

# Index and export to file
python work_order_cli.py index --export work_orders.json
```

### `list` - List Work Orders

Lists work orders with optional filtering.

```bash
python work_order_cli.py list [--status STATUS] [--priority PRIORITY] [--assigned USER] [--tag TAG] [--limit N]
```

**Options**:
- `--status STATUS`: Filter by status
- `--priority PRIORITY`: Filter by priority
- `--assigned USER`: Filter by assignee email
- `--tag TAG`: Filter by tag
- `--limit N`: Limit number of results

### `search` - Search Work Orders

Searches work orders using full-text search.

```bash
python work_order_cli.py search "query"
```

### `stats` - Show Statistics

Displays comprehensive work order statistics.

```bash
python work_order_cli.py stats
```

### `show` - Show Work Order Details

Shows detailed information about a specific work order.

```bash
python work_order_cli.py show WORK_ORDER_ID
```

### `export` - Export Work Orders

Exports work orders to a JSON file.

```bash
python work_order_cli.py export --output FILE
```

### `import` - Import Work Orders

Imports work orders from a JSON file.

```bash
python work_order_cli.py import --input FILE
```

## Complete Examples

### Basic Workflow

```bash
# 1. Index work orders
python work_order_cli.py index --export work_orders.json

# 2. View statistics
python work_order_cli.py stats

# 3. List queued work orders
python work_order_cli.py list --status queued

# 4. Search for specific work orders
python work_order_cli.py search "urgent bug"

# 5. Show details of a specific work order
python work_order_cli.py show WO-123
```

### Filtering Examples

```bash
# Find all high priority work orders
python work_order_cli.py list --priority high

# Find work orders assigned to specific developer
python work_order_cli.py list --assigned developer@company.com

# Find work orders with specific tag
python work_order_cli.py list --tag bug

# Get top 10 most recent work orders
python work_order_cli.py list --limit 10
```

## Error Handling

### Common Error Messages

- Invalid status/priority values
- Work order not found
- Missing required arguments
- File not found errors

### Exit Codes

- `0`: Success
- `1`: General error
- `1`: Keyboard interrupt (Ctrl+C)