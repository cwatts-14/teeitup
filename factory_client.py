#!/usr/bin/env python3
"""
Factory.8090.ai Integration Client

This module provides integration capabilities with the 8090 Software Factory service.
It includes both browser automation and potential API client functionality.
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin

import httpx
import structlog
from playwright.async_api import async_playwright, Browser, Page
from pydantic import BaseModel, Field

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

logger = structlog.get_logger()


class FactoryServiceInfo(BaseModel):
    """Model for factory service information"""
    name: str = Field(..., description="Service name")
    version: Optional[str] = Field(None, description="Service version")
    status: str = Field(..., description="Service status")
    capabilities: List[str] = Field(default_factory=list, description="Available capabilities")
    api_endpoints: List[str] = Field(default_factory=list, description="Discovered API endpoints")


class Factory8090Client:
    """
    Client for integrating with Factory.8090.ai service.
    
    This client provides both browser automation and API integration capabilities.
    """
    
    def __init__(self, base_url: str = "https://factory.8090.ai", timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
        self.session: Optional[httpx.AsyncClient] = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
        
    async def initialize(self):
        """Initialize the client and browser automation"""
        logger.info("Initializing Factory.8090.ai client")
        
        # Initialize HTTP client
        self.session = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={
                "User-Agent": "Factory.8090.ai Integration Client/1.0",
                "Accept": "application/json, text/html, */*",
            }
        )
        
        # Initialize browser automation
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=True)
        self.page = await self.browser.new_page()
        
        # Set up request interception to capture API calls
        await self._setup_request_interception()
        
        logger.info("Client initialized successfully")
        
    async def close(self):
        """Close the client and cleanup resources"""
        logger.info("Closing Factory.8090.ai client")
        
        if self.session:
            await self.session.aclose()
            
        if self.browser:
            await self.browser.close()
            
        logger.info("Client closed")
        
    async def _setup_request_interception(self):
        """Set up request interception to capture API calls"""
        if not self.page:
            return
            
        async def handle_request(request):
            """Handle intercepted requests"""
            if request.url.startswith(self.base_url):
                logger.info("Intercepted request", url=request.url, method=request.method)
                
        async def handle_response(response):
            """Handle intercepted responses"""
            if response.url.startswith(self.base_url):
                logger.info("Intercepted response", 
                          url=response.url, 
                          status=response.status,
                          content_type=response.headers.get("content-type"))
                
        await self.page.route("**/*", handle_request)
        await self.page.on("response", handle_response)
        
    async def discover_service_info(self) -> FactoryServiceInfo:
        """
        Discover service information through browser automation and network analysis.
        
        Returns:
            FactoryServiceInfo: Discovered service information
        """
        logger.info("Starting service discovery")
        
        if not self.page:
            raise RuntimeError("Client not initialized. Call initialize() first.")
            
        # Navigate to the service
        await self.page.goto(self.base_url)
        await self.page.wait_for_load_state("networkidle")
        
        # Extract basic information from the page
        title = await self.page.title()
        logger.info("Page title", title=title)
        
        # Look for any API endpoints or service information
        api_endpoints = []
        capabilities = []
        
        # Check for common API patterns in the page source
        content = await self.page.content()
        
        # Look for API endpoints in JavaScript or configuration
        import re
        api_patterns = [
            r'["\']([^"\']*api[^"\']*)["\']',
            r'["\']([^"\']*endpoint[^"\']*)["\']',
            r'["\']([^"\']*service[^"\']*)["\']',
        ]
        
        for pattern in api_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            api_endpoints.extend(matches)
            
        # Look for service capabilities
        capability_patterns = [
            r'["\']([^"\']*capability[^"\']*)["\']',
            r'["\']([^"\']*feature[^"\']*)["\']',
            r'["\']([^"\']*function[^"\']*)["\']',
        ]
        
        for pattern in capability_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            capabilities.extend(matches)
            
        # Check service health
        health_status = await self._check_health()
        
        service_info = FactoryServiceInfo(
            name="8090 Software Factory",
            status=health_status,
            capabilities=list(set(capabilities)),
            api_endpoints=list(set(api_endpoints))
        )
        
        logger.info("Service discovery completed", service_info=service_info.dict())
        return service_info
        
    async def _check_health(self) -> str:
        """Check service health status"""
        try:
            if self.session:
                response = await self.session.get("/")
                if response.status_code == 200:
                    return "healthy"
                else:
                    return f"unhealthy (status: {response.status_code})"
        except Exception as e:
            logger.error("Health check failed", error=str(e))
            return f"unhealthy (error: {str(e)})"
            
        return "unknown"
        
    async def test_api_endpoints(self, endpoints: List[str]) -> Dict[str, Any]:
        """
        Test discovered API endpoints.
        
        Args:
            endpoints: List of API endpoints to test
            
        Returns:
            Dict containing test results for each endpoint
        """
        results = {}
        
        if not self.session:
            logger.warning("No HTTP session available for API testing")
            return results
            
        for endpoint in endpoints:
            try:
                logger.info("Testing endpoint", endpoint=endpoint)
                
                # Try different HTTP methods
                for method in ["GET", "POST", "PUT", "DELETE"]:
                    try:
                        response = await self.session.request(method, endpoint)
                        results[f"{method} {endpoint}"] = {
                            "status_code": response.status_code,
                            "headers": dict(response.headers),
                            "content_type": response.headers.get("content-type"),
                            "success": 200 <= response.status_code < 300
                        }
                        
                        if response.status_code == 200:
                            logger.info("Successful API call", 
                                      method=method, 
                                      endpoint=endpoint,
                                      status=response.status_code)
                            break
                            
                    except Exception as e:
                        logger.debug("API call failed", 
                                   method=method, 
                                   endpoint=endpoint, 
                                   error=str(e))
                        
            except Exception as e:
                logger.error("Endpoint test failed", endpoint=endpoint, error=str(e))
                results[endpoint] = {"error": str(e)}
                
        return results
        
    async def extract_page_data(self) -> Dict[str, Any]:
        """
        Extract data from the current page.
        
        Returns:
            Dict containing extracted page data
        """
        if not self.page:
            raise RuntimeError("No page available")
            
        data = {
            "title": await self.page.title(),
            "url": self.page.url,
            "content_length": len(await self.page.content()),
            "elements": {}
        }
        
        # Extract specific elements
        try:
            # Look for common UI elements
            buttons = await self.page.query_selector_all("button")
            inputs = await self.page.query_selector_all("input")
            forms = await self.page.query_selector_all("form")
            
            data["elements"] = {
                "buttons": len(buttons),
                "inputs": len(inputs),
                "forms": len(forms)
            }
            
            # Extract text content
            body_text = await self.page.evaluate("document.body.innerText")
            data["text_content"] = body_text[:1000]  # First 1000 characters
            
        except Exception as e:
            logger.error("Failed to extract page data", error=str(e))
            
        return data


async def main():
    """Main function to demonstrate the integration client"""
    logger.info("Starting Factory.8090.ai integration exploration")
    
    async with Factory8090Client() as client:
        # Discover service information
        service_info = await client.discover_service_info()
        print(f"Service Info: {service_info.dict()}")
        
        # Extract page data
        page_data = await client.extract_page_data()
        print(f"Page Data: {json.dumps(page_data, indent=2)}")
        
        # Test discovered API endpoints
        if service_info.api_endpoints:
            api_results = await client.test_api_endpoints(service_info.api_endpoints)
            print(f"API Test Results: {json.dumps(api_results, indent=2)}")
        else:
            print("No API endpoints discovered")


if __name__ == "__main__":
    asyncio.run(main())