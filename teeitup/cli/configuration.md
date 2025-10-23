# CLI Configuration

This document covers configuration options for the Work Order CLI, including environment variables, settings, and customization options.

## Environment Variables

### Core Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `FACTORY_8090_BASE_URL` | `https://factory.8090.ai` | Base URL of the 8090 service |
| `WORK_ORDER_TIMEOUT` | `30` | Timeout for operations in seconds |
| `WORK_ORDER_HEADLESS` | `true` | Run browser in headless mode |

### Logging Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `LOG_FORMAT` | `json` | Log format (json, text) |
| `LOG_FILE` | `None` | Log file path (if not set, logs to stdout) |

### Browser Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `BROWSER_TYPE` | `chromium` | Browser type (chromium, firefox, webkit) |
| `BROWSER_HEADLESS` | `true` | Run browser in headless mode |
| `BROWSER_VIEWPORT_WIDTH` | `1280` | Browser viewport width |
| `BROWSER_VIEWPORT_HEIGHT` | `720` | Browser viewport height |

## Configuration Files

### Environment File (.env)

Create a `.env` file in your project directory:

```bash
# .env
FACTORY_8090_BASE_URL=https://factory.8090.ai
WORK_ORDER_TIMEOUT=30
WORK_ORDER_HEADLESS=true
LOG_LEVEL=INFO
LOG_FORMAT=json
BROWSER_TYPE=chromium
BROWSER_HEADLESS=true
```

### Configuration File (config.yaml)

Create a `config.yaml` file for more complex configuration:

```yaml
# config.yaml
factory:
  base_url: "https://factory.8090.ai"
  timeout: 30
  headless: true

browser:
  type: "chromium"
  headless: true
  viewport:
    width: 1280
    height: 720
  user_agent: "Work Order Discovery Client/1.0"

logging:
  level: "INFO"
  format: "json"
  file: "work_orders.log"

indexing:
  max_work_orders: 1000
  batch_size: 100
  retry_attempts: 3
  retry_delay: 2

search:
  max_results: 100
  fuzzy_matching: true
  case_sensitive: false
```

## Command Line Options

### Global Options

```bash
python work_order_cli.py [global_options] <command> [command_options]
```

**Global Options**:
- `--config FILE`: Specify configuration file
- `--log-level LEVEL`: Set logging level
- `--log-file FILE`: Set log file path
- `--verbose`: Enable verbose output
- `--quiet`: Suppress output except errors

### Command-Specific Options

#### Index Command

```bash
python work_order_cli.py index [options]
```

**Options**:
- `--export FILE`: Export indexed work orders to JSON file
- `--timeout SECONDS`: Override timeout setting
- `--headless BOOLEAN`: Override headless mode
- `--max-work-orders N`: Limit number of work orders to index

#### List Command

```bash
python work_order_cli.py list [options]
```

**Options**:
- `--status STATUS`: Filter by status
- `--priority PRIORITY`: Filter by priority
- `--assigned USER`: Filter by assignee
- `--tag TAG`: Filter by tag
- `--limit N`: Limit number of results
- `--format FORMAT`: Output format (table, json, csv)
- `--sort FIELD`: Sort by field (created, updated, title, status, priority)

#### Search Command

```bash
python work_order_cli.py search [options] "query"
```

**Options**:
- `--case-sensitive`: Enable case-sensitive search
- `--fuzzy`: Enable fuzzy matching
- `--limit N`: Limit number of results
- `--format FORMAT`: Output format (table, json, csv)

## Customization Examples

### Development Configuration

```bash
# .env.development
FACTORY_8090_BASE_URL=https://dev.factory.8090.ai
WORK_ORDER_TIMEOUT=60
WORK_ORDER_HEADLESS=false
LOG_LEVEL=DEBUG
LOG_FORMAT=text
BROWSER_HEADLESS=false
```

### Production Configuration

```bash
# .env.production
FACTORY_8090_BASE_URL=https://factory.8090.ai
WORK_ORDER_TIMEOUT=30
WORK_ORDER_HEADLESS=true
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=/var/log/work_orders.log
BROWSER_HEADLESS=true
```

### Testing Configuration

```bash
# .env.testing
FACTORY_8090_BASE_URL=https://test.factory.8090.ai
WORK_ORDER_TIMEOUT=10
WORK_ORDER_HEADLESS=true
LOG_LEVEL=WARNING
LOG_FORMAT=text
BROWSER_HEADLESS=true
```

## Advanced Configuration

### Custom Browser Settings

```python
# custom_config.py
import os
from playwright.async_api import async_playwright

async def create_custom_browser():
    playwright = await async_playwright().start()
    
    # Custom browser options
    browser = await playwright.chromium.launch(
        headless=os.getenv('BROWSER_HEADLESS', 'true').lower() == 'true',
        args=[
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--disable-web-security',
            '--disable-features=VizDisplayCompositor'
        ]
    )
    
    # Custom page options
    page = await browser.new_page(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Custom Work Order Client/1.0'
    )
    
    return browser, page
```

### Custom Logging Configuration

```python
# custom_logging.py
import structlog
import logging

def setup_custom_logging():
    # Configure structured logging
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Set log level
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    logging.basicConfig(level=getattr(logging, log_level))
```

### Custom Search Configuration

```python
# custom_search.py
import re
from typing import List

class CustomSearchEngine:
    def __init__(self, case_sensitive=False, fuzzy_matching=True):
        self.case_sensitive = case_sensitive
        self.fuzzy_matching = fuzzy_matching
    
    def search(self, query: str, work_orders: List[WorkOrder]) -> List[WorkOrder]:
        if not self.case_sensitive:
            query = query.lower()
        
        results = []
        for wo in work_orders:
            if self._matches(wo, query):
                results.append(wo)
        
        return results
    
    def _matches(self, work_order: WorkOrder, query: str) -> bool:
        searchable_text = f"{work_order.title} {work_order.description} {' '.join(work_order.tags)}"
        
        if not self.case_sensitive:
            searchable_text = searchable_text.lower()
        
        if self.fuzzy_matching:
            # Implement fuzzy matching logic
            return self._fuzzy_match(searchable_text, query)
        else:
            return query in searchable_text
    
    def _fuzzy_match(self, text: str, query: str) -> bool:
        # Simple fuzzy matching implementation
        query_words = query.split()
        text_words = text.split()
        
        matches = 0
        for q_word in query_words:
            for t_word in text_words:
                if q_word in t_word or t_word in q_word:
                    matches += 1
                    break
        
        return matches >= len(query_words) * 0.7  # 70% match threshold
```

## Configuration Validation

### Environment Variable Validation

```python
# config_validation.py
import os
from typing import Optional

def validate_config():
    """Validate configuration settings"""
    errors = []
    
    # Validate base URL
    base_url = os.getenv('FACTORY_8090_BASE_URL')
    if not base_url or not base_url.startswith('http'):
        errors.append("FACTORY_8090_BASE_URL must be a valid HTTP URL")
    
    # Validate timeout
    try:
        timeout = int(os.getenv('WORK_ORDER_TIMEOUT', '30'))
        if timeout <= 0:
            errors.append("WORK_ORDER_TIMEOUT must be positive")
    except ValueError:
        errors.append("WORK_ORDER_TIMEOUT must be a valid integer")
    
    # Validate log level
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
    if log_level not in valid_levels:
        errors.append(f"LOG_LEVEL must be one of: {', '.join(valid_levels)}")
    
    if errors:
        raise ValueError(f"Configuration errors: {'; '.join(errors)}")
    
    return True
```

## Configuration Examples

### Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.9-slim

# Set environment variables
ENV FACTORY_8090_BASE_URL=https://factory.8090.ai
ENV WORK_ORDER_TIMEOUT=30
ENV WORK_ORDER_HEADLESS=true
ENV LOG_LEVEL=INFO
ENV LOG_FORMAT=json

# Copy application
COPY . /app
WORKDIR /app

# Install dependencies
RUN pip install -r requirements.txt
RUN playwright install

# Run application
CMD ["python", "work_order_cli.py", "index"]
```

### Kubernetes Configuration

```yaml
# k8s-configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: work-order-config
data:
  FACTORY_8090_BASE_URL: "https://factory.8090.ai"
  WORK_ORDER_TIMEOUT: "30"
  WORK_ORDER_HEADLESS: "true"
  LOG_LEVEL: "INFO"
  LOG_FORMAT: "json"
  BROWSER_HEADLESS: "true"
```

### Systemd Service Configuration

```ini
# /etc/systemd/system/work-order-cli.service
[Unit]
Description=Work Order CLI Service
After=network.target

[Service]
Type=oneshot
User=workorder
Group=workorder
WorkingDirectory=/opt/work-order-cli
Environment=FACTORY_8090_BASE_URL=https://factory.8090.ai
Environment=WORK_ORDER_TIMEOUT=30
Environment=WORK_ORDER_HEADLESS=true
Environment=LOG_LEVEL=INFO
Environment=LOG_FILE=/var/log/work-orders.log
ExecStart=/usr/bin/python3 work_order_cli.py index --export /var/backups/work_orders.json

[Install]
WantedBy=multi-user.target
```

## Best Practices

### Configuration Management

1. **Use Environment Variables**: For sensitive data and environment-specific settings
2. **Use Configuration Files**: For complex configurations and defaults
3. **Validate Configuration**: Always validate configuration on startup
4. **Document Settings**: Document all configuration options
5. **Use Defaults**: Provide sensible defaults for all settings

### Security Considerations

1. **Never Hardcode Credentials**: Use environment variables or secure vaults
2. **Validate URLs**: Ensure URLs are valid and secure
3. **Limit Permissions**: Use minimal required permissions
4. **Secure Logging**: Avoid logging sensitive information
5. **Regular Updates**: Keep configuration files updated

### Performance Optimization

1. **Tune Timeouts**: Set appropriate timeouts for your environment
2. **Optimize Browser Settings**: Use headless mode in production
3. **Configure Logging**: Use appropriate log levels
4. **Monitor Resources**: Track memory and CPU usage
5. **Batch Operations**: Use batch processing for large datasets