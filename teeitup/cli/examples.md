# CLI Examples

This document provides practical examples of using the Work Order CLI for common scenarios.

## Getting Started

### First Time Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt
playwright install

# 2. Index work orders from 8090 integrations
python work_order_cli.py index --export initial_work_orders.json

# 3. View what was discovered
python work_order_cli.py stats
```

### Daily Workflow

```bash
# Morning routine - check queued work orders
python work_order_cli.py list --status queued --limit 10

# Search for urgent items
python work_order_cli.py search "urgent"

# Check work assigned to you
python work_order_cli.py list --assigned your-email@company.com
```

## Work Order Management

### Finding Work Orders

```bash
# Find all bug-related work orders
python work_order_cli.py search "bug"

# Find work orders by component
python work_order_cli.py search "authentication"

# Find work orders by status
python work_order_cli.py list --status in_progress

# Find high priority work orders
python work_order_cli.py list --priority high
```

### Detailed Analysis

```bash
# Get comprehensive statistics
python work_order_cli.py stats

# Show details of specific work order
python work_order_cli.py show WO-123

# Find work orders with specific tag
python work_order_cli.py list --tag "security"
```

## Data Management

### Backup and Restore

```bash
# Create daily backup
python work_order_cli.py export --output backup_$(date +%Y%m%d).json

# Create timestamped backup
python work_order_cli.py export --output work_orders_$(date +%Y%m%d_%H%M%S).json

# Restore from backup
python work_order_cli.py import --input backup_20251023.json
```

### Data Migration

```bash
# Export current data
python work_order_cli.py export --output migration_export.json

# Import into new system
python work_order_cli.py import --input migration_export.json

# Verify import
python work_order_cli.py stats
```

## Advanced Filtering

### Complex Queries

```bash
# Find urgent work orders assigned to specific person
python work_order_cli.py list --assigned developer@company.com | grep -i urgent

# Find work orders with multiple criteria
python work_order_cli.py list --status queued --priority high --limit 5

# Search for work orders containing multiple terms
python work_order_cli.py search "dashboard feature"
```

### Batch Operations

```bash
# Get all work orders and save to file
python work_order_cli.py list > all_work_orders.txt

# Get queued work orders and count them
python work_order_cli.py list --status queued | grep -c "ID:"

# Export and immediately import (refresh)
python work_order_cli.py export --output temp.json && python work_order_cli.py import --input temp.json
```

## Monitoring and Reporting

### Status Monitoring

```bash
# Check overall status distribution
python work_order_cli.py stats

# Monitor queued work orders
watch -n 30 "python work_order_cli.py list --status queued --limit 5"

# Check for urgent items
python work_order_cli.py search "urgent" | head -10
```

### Performance Monitoring

```bash
# Time the indexing operation
time python work_order_cli.py index

# Monitor indexing with verbose output
python work_order_cli.py index --export work_orders.json 2>&1 | tee indexing.log
```

## Integration Examples

### Script Integration

```bash
#!/bin/bash
# Daily work order report script

echo "=== Daily Work Order Report ==="
echo "Date: $(date)"
echo

echo "=== Statistics ==="
python work_order_cli.py stats
echo

echo "=== Queued Work Orders ==="
python work_order_cli.py list --status queued --limit 10
echo

echo "=== High Priority Items ==="
python work_order_cli.py list --priority high
echo

echo "=== Urgent Items ==="
python work_order_cli.py search "urgent"
```

### Cron Job Example

```bash
# Add to crontab for daily indexing at 9 AM
0 9 * * * cd /path/to/project && python work_order_cli.py index --export /backups/work_orders_$(date +\%Y\%m\%d).json
```

### CI/CD Integration

```bash
#!/bin/bash
# CI/CD pipeline script

# Index work orders
python work_order_cli.py index --export work_orders.json

# Check for critical issues
CRITICAL_COUNT=$(python work_order_cli.py list --priority critical | grep -c "ID:")
if [ $CRITICAL_COUNT -gt 0 ]; then
    echo "WARNING: $CRITICAL_COUNT critical work orders found"
    exit 1
fi

# Check for urgent items
URGENT_COUNT=$(python work_order_cli.py search "urgent" | grep -c "ID:")
if [ $URGENT_COUNT -gt 5 ]; then
    echo "WARNING: $URGENT_COUNT urgent work orders found"
fi
```

## Troubleshooting Examples

### Common Issues

```bash
# Check if work orders are indexed
python work_order_cli.py stats

# If no work orders, re-index
python work_order_cli.py index

# Check for specific work order
python work_order_cli.py show WO-123

# If work order not found, check all work orders
python work_order_cli.py list | grep WO-123
```

### Debugging

```bash
# Run with verbose output
python work_order_cli.py index 2>&1 | tee debug.log

# Check file permissions
ls -la work_orders.json

# Verify JSON format
python -m json.tool work_orders.json > /dev/null && echo "JSON is valid" || echo "JSON is invalid"
```

## Automation Examples

### Automated Reporting

```bash
#!/bin/bash
# Automated daily report

REPORT_FILE="daily_report_$(date +%Y%m%d).txt"
echo "Daily Work Order Report - $(date)" > $REPORT_FILE
echo "=================================" >> $REPORT_FILE
echo >> $REPORT_FILE

echo "Statistics:" >> $REPORT_FILE
python work_order_cli.py stats >> $REPORT_FILE
echo >> $REPORT_FILE

echo "Queued Work Orders:" >> $REPORT_FILE
python work_order_cli.py list --status queued >> $REPORT_FILE
echo >> $REPORT_FILE

echo "High Priority Items:" >> $REPORT_FILE
python work_order_cli.py list --priority high >> $REPORT_FILE

# Send report via email (if configured)
# mail -s "Daily Work Order Report" team@company.com < $REPORT_FILE
```

### Health Check Script

```bash
#!/bin/bash
# System health check

echo "Checking work order system health..."

# Check if CLI is working
if ! python work_order_cli.py stats > /dev/null 2>&1; then
    echo "ERROR: CLI is not working"
    exit 1
fi

# Check for critical work orders
CRITICAL=$(python work_order_cli.py list --priority critical | grep -c "ID:")
if [ $CRITICAL -gt 0 ]; then
    echo "WARNING: $CRITICAL critical work orders found"
fi

# Check for failed work orders
FAILED=$(python work_order_cli.py list --status failed | grep -c "ID:")
if [ $FAILED -gt 0 ]; then
    echo "WARNING: $FAILED failed work orders found"
fi

echo "Health check completed"
```

## Best Practices

### Regular Maintenance

```bash
# Daily: Check for urgent items
python work_order_cli.py search "urgent"

# Weekly: Full statistics review
python work_order_cli.py stats

# Monthly: Create comprehensive backup
python work_order_cli.py export --output monthly_backup_$(date +%Y%m).json
```

### Performance Optimization

```bash
# Use filters to reduce output
python work_order_cli.py list --status queued --limit 20

# Use search instead of listing all work orders
python work_order_cli.py search "specific term"

# Export only when needed
python work_order_cli.py export --output work_orders.json
```

### Error Prevention

```bash
# Always check status before operations
python work_order_cli.py stats

# Verify work order exists before showing details
python work_order_cli.py list | grep "WO-123" && python work_order_cli.py show WO-123

# Use absolute paths for file operations
python work_order_cli.py export --output /full/path/to/work_orders.json
```