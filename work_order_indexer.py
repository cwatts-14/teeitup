#!/usr/bin/env python3
"""
Work Order Indexer for 8090 Integrations

This module provides comprehensive work order indexing capabilities for the
Factory.8090.ai service, including discovery, indexing, and monitoring of
queued work orders.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import re
import hashlib

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


class WorkOrderStatus(Enum):
    """Work order status enumeration"""
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PENDING_APPROVAL = "pending_approval"
    ON_HOLD = "on_hold"


class WorkOrderPriority(Enum):
    """Work order priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


@dataclass
class WorkOrder:
    """Work order data structure"""
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
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['status'] = self.status.value
        data['priority'] = self.priority.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        if self.due_date:
            data['due_date'] = self.due_date.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkOrder':
        """Create from dictionary"""
        data['status'] = WorkOrderStatus(data['status'])
        data['priority'] = WorkOrderPriority(data['priority'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        if data.get('due_date'):
            data['due_date'] = datetime.fromisoformat(data['due_date'])
        return cls(**data)


class WorkOrderIndex:
    """Work order indexing and search system"""
    
    def __init__(self):
        self.work_orders: Dict[str, WorkOrder] = {}
        self.index_by_status: Dict[WorkOrderStatus, List[str]] = {}
        self.index_by_priority: Dict[WorkOrderPriority, List[str]] = {}
        self.index_by_assigned: Dict[str, List[str]] = {}
        self.index_by_tags: Dict[str, List[str]] = {}
        self.search_index: Dict[str, List[str]] = {}
        
        # Initialize index structures
        for status in WorkOrderStatus:
            self.index_by_status[status] = []
        for priority in WorkOrderPriority:
            self.index_by_priority[priority] = []
    
    def add_work_order(self, work_order: WorkOrder) -> None:
        """Add a work order to the index"""
        self.work_orders[work_order.id] = work_order
        
        # Update status index
        self.index_by_status[work_order.status].append(work_order.id)
        
        # Update priority index
        self.index_by_priority[work_order.priority].append(work_order.id)
        
        # Update assigned index
        if work_order.assigned_to:
            if work_order.assigned_to not in self.index_by_assigned:
                self.index_by_assigned[work_order.assigned_to] = []
            self.index_by_assigned[work_order.assigned_to].append(work_order.id)
        
        # Update tags index
        for tag in work_order.tags:
            if tag not in self.index_by_tags:
                self.index_by_tags[tag] = []
            self.index_by_tags[tag].append(work_order.id)
        
        # Update search index
        self._update_search_index(work_order)
        
        logger.info("Work order added to index", 
                   work_order_id=work_order.id, 
                   status=work_order.status.value)
    
    def _update_search_index(self, work_order: WorkOrder) -> None:
        """Update the search index for a work order"""
        searchable_text = f"{work_order.title} {work_order.description} {' '.join(work_order.tags)}"
        words = re.findall(r'\b\w+\b', searchable_text.lower())
        
        for word in words:
            if word not in self.search_index:
                self.search_index[word] = []
            if work_order.id not in self.search_index[word]:
                self.search_index[word].append(work_order.id)
    
    def get_work_order(self, work_order_id: str) -> Optional[WorkOrder]:
        """Get a work order by ID"""
        return self.work_orders.get(work_order_id)
    
    def search_work_orders(self, query: str) -> List[WorkOrder]:
        """Search work orders by text query"""
        query_words = re.findall(r'\b\w+\b', query.lower())
        matching_ids = set()
        
        for word in query_words:
            if word in self.search_index:
                if not matching_ids:
                    matching_ids = set(self.search_index[word])
                else:
                    matching_ids &= set(self.search_index[word])
        
        return [self.work_orders[wo_id] for wo_id in matching_ids if wo_id in self.work_orders]
    
    def get_work_orders_by_status(self, status: WorkOrderStatus) -> List[WorkOrder]:
        """Get work orders by status"""
        return [self.work_orders[wo_id] for wo_id in self.index_by_status[status] 
                if wo_id in self.work_orders]
    
    def get_work_orders_by_priority(self, priority: WorkOrderPriority) -> List[WorkOrder]:
        """Get work orders by priority"""
        return [self.work_orders[wo_id] for wo_id in self.index_by_priority[priority] 
                if wo_id in self.work_orders]
    
    def get_work_orders_by_assigned(self, assigned_to: str) -> List[WorkOrder]:
        """Get work orders by assignee"""
        wo_ids = self.index_by_assigned.get(assigned_to, [])
        return [self.work_orders[wo_id] for wo_id in wo_ids if wo_id in self.work_orders]
    
    def get_work_orders_by_tag(self, tag: str) -> List[WorkOrder]:
        """Get work orders by tag"""
        wo_ids = self.index_by_tags.get(tag, [])
        return [self.work_orders[wo_id] for wo_id in wo_ids if wo_id in self.work_orders]
    
    def get_queued_work_orders(self) -> List[WorkOrder]:
        """Get all queued work orders"""
        return self.get_work_orders_by_status(WorkOrderStatus.QUEUED)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get work order statistics"""
        total = len(self.work_orders)
        status_counts = {status.value: len(wo_list) for status, wo_list in self.index_by_status.items()}
        priority_counts = {priority.value: len(wo_list) for priority, wo_list in self.index_by_priority.items()}
        
        return {
            "total_work_orders": total,
            "status_distribution": status_counts,
            "priority_distribution": priority_counts,
            "assigned_count": len(self.index_by_assigned),
            "tags_count": len(self.index_by_tags),
            "search_index_size": len(self.search_index)
        }
    
    def export_to_json(self) -> str:
        """Export work orders to JSON"""
        data = {
            "work_orders": [wo.to_dict() for wo in self.work_orders.values()],
            "statistics": self.get_statistics(),
            "exported_at": datetime.now().isoformat()
        }
        return json.dumps(data, indent=2)
    
    def import_from_json(self, json_data: str) -> None:
        """Import work orders from JSON"""
        data = json.loads(json_data)
        
        for wo_data in data.get("work_orders", []):
            work_order = WorkOrder.from_dict(wo_data)
            self.add_work_order(work_order)
        
        logger.info("Work orders imported from JSON", count=len(data.get("work_orders", [])))


class WorkOrderDiscovery:
    """Work order discovery from 8090 integrations"""
    
    def __init__(self, base_url: str = "https://factory.8090.ai"):
        self.base_url = base_url
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.session: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def initialize(self):
        """Initialize the discovery client"""
        logger.info("Initializing work order discovery")
        
        # Initialize HTTP client
        self.session = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30,
            headers={
                "User-Agent": "Work Order Discovery Client/1.0",
                "Accept": "application/json, text/html, */*",
            }
        )
        
        # Initialize browser automation
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=True)
        self.page = await self.browser.new_page()
        
        # Set up request interception
        await self._setup_request_interception()
        
        logger.info("Work order discovery initialized")
    
    async def close(self):
        """Close the discovery client"""
        if self.session:
            await self.session.aclose()
        if self.browser:
            await self.browser.close()
        logger.info("Work order discovery closed")
    
    async def _setup_request_interception(self):
        """Set up request interception to capture work order data"""
        if not self.page:
            return
        
        async def handle_response(response):
            """Handle intercepted responses for work order data"""
            if response.url.startswith(self.base_url):
                try:
                    content_type = response.headers.get("content-type", "")
                    if "application/json" in content_type:
                        data = await response.json()
                        await self._process_api_response(response.url, data)
                except Exception as e:
                    logger.debug("Failed to process response", url=response.url, error=str(e))
        
        await self.page.on("response", handle_response)
    
    async def _process_api_response(self, url: str, data: Any) -> None:
        """Process API response for work order data"""
        logger.debug("Processing API response", url=url, data_type=type(data).__name__)
        
        # Look for work order patterns in the response
        if isinstance(data, dict):
            await self._extract_work_orders_from_dict(data, url)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    await self._extract_work_orders_from_dict(item, url)
    
    async def _extract_work_orders_from_dict(self, data: Dict[str, Any], source_url: str) -> List[WorkOrder]:
        """Extract work orders from dictionary data"""
        work_orders = []
        
        # Look for common work order patterns
        work_order_patterns = [
            "work_orders", "workOrders", "tasks", "jobs", "orders",
            "queue", "pending", "assigned", "work_items"
        ]
        
        for pattern in work_order_patterns:
            if pattern in data:
                items = data[pattern]
                if isinstance(items, list):
                    for item in items:
                        work_order = await self._create_work_order_from_data(item, source_url)
                        if work_order:
                            work_orders.append(work_order)
        
        return work_orders
    
    async def _create_work_order_from_data(self, data: Dict[str, Any], source_url: str) -> Optional[WorkOrder]:
        """Create a work order from data dictionary"""
        try:
            # Extract basic fields
            wo_id = str(data.get("id", data.get("_id", data.get("work_order_id", ""))))
            if not wo_id:
                wo_id = hashlib.md5(str(data).encode()).hexdigest()[:12]
            
            title = data.get("title", data.get("name", data.get("subject", "Untitled Work Order")))
            description = data.get("description", data.get("details", data.get("summary", "")))
            
            # Extract status
            status_str = data.get("status", data.get("state", "queued")).lower()
            status_mapping = {
                "queued": WorkOrderStatus.QUEUED,
                "pending": WorkOrderStatus.QUEUED,
                "in_progress": WorkOrderStatus.IN_PROGRESS,
                "active": WorkOrderStatus.IN_PROGRESS,
                "completed": WorkOrderStatus.COMPLETED,
                "done": WorkOrderStatus.COMPLETED,
                "failed": WorkOrderStatus.FAILED,
                "error": WorkOrderStatus.FAILED,
                "cancelled": WorkOrderStatus.CANCELLED,
                "cancelled": WorkOrderStatus.CANCELLED,
                "on_hold": WorkOrderStatus.ON_HOLD,
                "paused": WorkOrderStatus.ON_HOLD
            }
            status = status_mapping.get(status_str, WorkOrderStatus.QUEUED)
            
            # Extract priority
            priority_str = data.get("priority", data.get("urgency", "medium")).lower()
            priority_mapping = {
                "low": WorkOrderPriority.LOW,
                "medium": WorkOrderPriority.MEDIUM,
                "high": WorkOrderPriority.HIGH,
                "urgent": WorkOrderPriority.URGENT,
                "critical": WorkOrderPriority.CRITICAL
            }
            priority = priority_mapping.get(priority_str, WorkOrderPriority.MEDIUM)
            
            # Extract timestamps
            created_at = self._parse_timestamp(data.get("created_at", data.get("created", data.get("timestamp"))))
            updated_at = self._parse_timestamp(data.get("updated_at", data.get("updated", data.get("modified"))))
            due_date = self._parse_timestamp(data.get("due_date", data.get("deadline", data.get("due"))))
            
            # Extract assignee
            assigned_to = data.get("assigned_to", data.get("assignee", data.get("owner")))
            if assigned_to and isinstance(assigned_to, dict):
                assigned_to = assigned_to.get("name", assigned_to.get("email", str(assigned_to)))
            
            # Extract tags
            tags = data.get("tags", data.get("labels", data.get("categories", [])))
            if isinstance(tags, str):
                tags = [tag.strip() for tag in tags.split(",")]
            elif not isinstance(tags, list):
                tags = []
            
            # Extract metadata
            metadata = {k: v for k, v in data.items() 
                       if k not in ["id", "title", "description", "status", "priority", 
                                  "created_at", "updated_at", "due_date", "assigned_to", "tags"]}
            metadata["source_url"] = source_url
            
            work_order = WorkOrder(
                id=wo_id,
                title=title,
                description=description,
                status=status,
                priority=priority,
                created_at=created_at,
                updated_at=updated_at,
                assigned_to=assigned_to,
                due_date=due_date,
                tags=tags,
                metadata=metadata
            )
            
            logger.debug("Created work order from data", work_order_id=wo_id, title=title)
            return work_order
            
        except Exception as e:
            logger.error("Failed to create work order from data", error=str(e), data=data)
            return None
    
    def _parse_timestamp(self, timestamp: Any) -> datetime:
        """Parse timestamp from various formats"""
        if not timestamp:
            return datetime.now()
        
        if isinstance(timestamp, datetime):
            return timestamp
        
        if isinstance(timestamp, (int, float)):
            # Unix timestamp
            return datetime.fromtimestamp(timestamp)
        
        if isinstance(timestamp, str):
            # Try various ISO formats
            formats = [
                "%Y-%m-%dT%H:%M:%S.%fZ",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d"
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(timestamp, fmt)
                except ValueError:
                    continue
            
            # Try parsing with dateutil if available
            try:
                from dateutil import parser
                return parser.parse(timestamp)
            except ImportError:
                pass
        
        return datetime.now()
    
    async def discover_work_orders(self) -> List[WorkOrder]:
        """Discover work orders from the 8090 service"""
        logger.info("Starting work order discovery")
        
        if not self.page:
            raise RuntimeError("Discovery client not initialized")
        
        work_orders = []
        
        try:
            # Navigate to the service
            await self.page.goto(self.base_url)
            await self.page.wait_for_load_state("networkidle")
            
            # Wait for potential work order data to load
            await asyncio.sleep(2)
            
            # Look for work order data in the page
            page_work_orders = await self._extract_work_orders_from_page()
            work_orders.extend(page_work_orders)
            
            # Try to find and click on work order related elements
            work_order_links = await self.page.query_selector_all("a[href*='work'], a[href*='order'], a[href*='task'], a[href*='job']")
            
            for link in work_order_links[:5]:  # Limit to first 5 links
                try:
                    await link.click()
                    await self.page.wait_for_load_state("networkidle")
                    
                    # Extract work orders from the new page
                    page_work_orders = await self._extract_work_orders_from_page()
                    work_orders.extend(page_work_orders)
                    
                    # Go back
                    await self.page.go_back()
                    await self.page.wait_for_load_state("networkidle")
                    
                except Exception as e:
                    logger.debug("Failed to process work order link", error=str(e))
                    continue
            
            # Look for API endpoints that might contain work order data
            api_work_orders = await self._discover_work_orders_from_apis()
            work_orders.extend(api_work_orders)
            
        except Exception as e:
            logger.error("Work order discovery failed", error=str(e))
        
        logger.info("Work order discovery completed", count=len(work_orders))
        return work_orders
    
    async def _extract_work_orders_from_page(self) -> List[WorkOrder]:
        """Extract work orders from the current page"""
        work_orders = []
        
        try:
            # Look for work order data in JavaScript variables
            js_data = await self.page.evaluate("""
                () => {
                    const data = {};
                    
                    // Look for common work order data patterns
                    const patterns = ['workOrders', 'work_orders', 'tasks', 'jobs', 'queue'];
                    
                    for (const pattern of patterns) {
                        if (window[pattern]) {
                            data[pattern] = window[pattern];
                        }
                    }
                    
                    // Look for data in common global objects
                    if (window.app && window.app.data) {
                        data.app_data = window.app.data;
                    }
                    
                    if (window.state && window.state.workOrders) {
                        data.state_work_orders = window.state.workOrders;
                    }
                    
                    return data;
                }
            """)
            
            if js_data:
                work_orders = await self._extract_work_orders_from_dict(js_data, self.page.url)
            
        except Exception as e:
            logger.debug("Failed to extract work orders from page", error=str(e))
        
        return work_orders
    
    async def _discover_work_orders_from_apis(self) -> List[WorkOrder]:
        """Discover work orders from API endpoints"""
        work_orders = []
        
        if not self.session:
            return work_orders
        
        # Common API endpoints that might contain work order data
        api_endpoints = [
            "/api/work-orders",
            "/api/work_orders",
            "/api/tasks",
            "/api/jobs",
            "/api/queue",
            "/api/orders",
            "/api/v1/work-orders",
            "/api/v1/tasks",
            "/api/v1/jobs",
            "/api/v2/work-orders",
            "/api/v2/tasks",
            "/api/v2/jobs"
        ]
        
        for endpoint in api_endpoints:
            try:
                response = await self.session.get(endpoint)
                if response.status_code == 200:
                    data = response.json()
                    endpoint_work_orders = await self._extract_work_orders_from_dict(data, endpoint)
                    work_orders.extend(endpoint_work_orders)
                    
            except Exception as e:
                logger.debug("Failed to fetch from API endpoint", endpoint=endpoint, error=str(e))
        
        return work_orders


class WorkOrderIndexer:
    """Main work order indexing system"""
    
    def __init__(self, base_url: str = "https://factory.8090.ai"):
        self.base_url = base_url
        self.index = WorkOrderIndex()
        self.discovery = WorkOrderDiscovery(base_url)
        self.last_index_time: Optional[datetime] = None
    
    async def index_work_orders(self) -> Dict[str, Any]:
        """Index all work orders from 8090 integrations"""
        logger.info("Starting work order indexing")
        
        start_time = datetime.now()
        
        try:
            async with self.discovery as discovery:
                # Discover work orders
                work_orders = await discovery.discover_work_orders()
                
                # Add to index
                for work_order in work_orders:
                    self.index.add_work_order(work_order)
                
                # Update last index time
                self.last_index_time = datetime.now()
                
                # Generate statistics
                stats = self.index.get_statistics()
                stats["indexing_duration"] = (self.last_index_time - start_time).total_seconds()
                stats["discovered_count"] = len(work_orders)
                stats["indexed_count"] = len(self.index.work_orders)
                
                logger.info("Work order indexing completed", **stats)
                return stats
                
        except Exception as e:
            logger.error("Work order indexing failed", error=str(e))
            raise
    
    def get_queued_work_orders(self) -> List[WorkOrder]:
        """Get all queued work orders"""
        return self.index.get_queued_work_orders()
    
    def search_work_orders(self, query: str) -> List[WorkOrder]:
        """Search work orders"""
        return self.index.search_work_orders(query)
    
    def get_work_order_statistics(self) -> Dict[str, Any]:
        """Get work order statistics"""
        stats = self.index.get_statistics()
        stats["last_index_time"] = self.last_index_time.isoformat() if self.last_index_time else None
        return stats
    
    def export_work_orders(self, filepath: str) -> None:
        """Export work orders to JSON file"""
        json_data = self.index.export_to_json()
        with open(filepath, 'w') as f:
            f.write(json_data)
        logger.info("Work orders exported", filepath=filepath)
    
    def import_work_orders(self, filepath: str) -> None:
        """Import work orders from JSON file"""
        with open(filepath, 'r') as f:
            json_data = f.read()
        self.index.import_from_json(json_data)
        logger.info("Work orders imported", filepath=filepath)


async def main():
    """Main function to demonstrate work order indexing"""
    logger.info("Starting work order indexing for 8090 integrations")
    
    indexer = WorkOrderIndexer()
    
    try:
        # Index work orders
        stats = await indexer.index_work_orders()
        
        print(f"✅ Work order indexing completed!")
        print(f"📊 Statistics: {json.dumps(stats, indent=2)}")
        
        # Get queued work orders
        queued_orders = indexer.get_queued_work_orders()
        print(f"\n📋 Queued work orders: {len(queued_orders)}")
        
        for order in queued_orders[:5]:  # Show first 5
            print(f"  - {order.title} ({order.status.value}) - {order.priority.value}")
        
        # Export results
        indexer.export_work_orders("work_orders_index.json")
        print(f"\n📁 Work orders exported to: work_orders_index.json")
        
    except Exception as e:
        logger.error("Work order indexing failed", error=str(e))
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())