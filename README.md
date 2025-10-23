# Factory.8090.ai Integration Explorer

This project provides integration capabilities with the Factory.8090.ai service, including browser automation, API discovery, and service analysis tools.

## Overview

Factory.8090.ai appears to be a "8090 Software Factory" service that provides software development tools and capabilities. This integration explorer helps you understand the service and implement various integration approaches.

## Features

- 🔍 **Service Discovery**: Automatically discover service capabilities and API endpoints
- 🤖 **Browser Automation**: Interact with the service using Playwright automation
- 📊 **API Testing**: Test discovered endpoints and analyze responses
- 📋 **Comprehensive Reporting**: Generate detailed integration reports with recommendations
- 🛡️ **Error Handling**: Robust error handling and logging throughout

## Quick Start

### Prerequisites

- Python 3.8+
- pip or conda package manager

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

Run the example exploration script:

```bash
python example_usage.py
```

This will:
- Discover service information
- Extract page data
- Test any discovered API endpoints
- Generate a comprehensive integration report

### Using the Client Directly

```python
import asyncio
from factory_client import Factory8090Client

async def main():
    async with Factory8090Client() as client:
        # Discover service information
        service_info = await client.discover_service_info()
        print(f"Service: {service_info.name}")
        print(f"Status: {service_info.status}")
        
        # Extract page data
        page_data = await client.extract_page_data()
        print(f"Page title: {page_data['title']}")

asyncio.run(main())
```

## Project Structure

```
/workspace/
├── factory_client.py              # Main integration client
├── example_usage.py               # Example usage script
├── requirements.txt               # Python dependencies
├── factory_8090_integration_exploration.md  # Detailed exploration plan
├── README.md                      # This file
└── factory_8090_integration_report.json     # Generated report (after running)
```

## Integration Approaches

### 1. Browser Automation
- **Best for**: Services without public APIs
- **Tools**: Playwright, Selenium
- **Use cases**: Data extraction, form automation, UI testing

### 2. API Integration
- **Best for**: Services with discoverable REST APIs
- **Tools**: httpx, requests
- **Use cases**: Direct data access, real-time integration

### 3. Web Scraping
- **Best for**: Static content extraction
- **Tools**: BeautifulSoup, Scrapy
- **Use cases**: Content monitoring, data collection

## Configuration

The client can be configured with environment variables:

```bash
export FACTORY_8090_BASE_URL="https://factory.8090.ai"
export FACTORY_8090_TIMEOUT="30"
export FACTORY_8090_HEADLESS="true"
```

## Monitoring and Logging

The integration includes comprehensive logging using structlog:

- **Structured JSON logging** for easy parsing
- **Request/response tracking** for debugging
- **Error handling** with detailed context
- **Performance metrics** for optimization

## Security Considerations

- **Credential Management**: Use environment variables for sensitive data
- **Rate Limiting**: Respect service limits and implement backoff
- **Data Privacy**: Ensure compliance with data protection regulations
- **Error Handling**: Avoid exposing sensitive information in logs

## Troubleshooting

### Common Issues

1. **Browser Installation**: Ensure Playwright browsers are installed
   ```bash
   playwright install
   ```

2. **Network Issues**: Check firewall and proxy settings
3. **Service Unavailable**: Verify the service is accessible
4. **Authentication**: Check if authentication is required

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is provided as-is for exploration and integration purposes.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the generated integration report
3. Check the logs for detailed error information