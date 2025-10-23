#!/usr/bin/env python3
"""
Example Work Order Indexing for 8090 Integrations

This script demonstrates how to use the work order indexer to discover,
index, and manage work orders from the Factory.8090.ai service.
"""

import asyncio
import json
from datetime import datetime
from work_order_indexer import WorkOrderIndexer, WorkOrder, WorkOrderStatus, WorkOrderPriority


async def demonstrate_work_order_indexing():
    """Demonstrate work order indexing capabilities"""
    print("🚀 Work Order Indexing Demo for 8090 Integrations")
    print("=" * 60)
    
    # Initialize the indexer
    indexer = WorkOrderIndexer()
    
    try:
        # Step 1: Index work orders from 8090 integrations
        print("\n📋 Step 1: Indexing work orders from 8090 integrations...")
        stats = await indexer.index_work_orders()
        
        print(f"✅ Indexing completed!")
        print(f"📊 Total work orders: {stats['total_work_orders']}")
        print(f"⏱️  Duration: {stats['indexing_duration']:.2f} seconds")
        print(f"🔍 Discovered: {stats['discovered_count']}")
        print(f"📝 Indexed: {stats['indexed_count']}")
        
        # Step 2: Show queued work orders
        print("\n📋 Step 2: Queued work orders...")
        queued_orders = indexer.get_queued_work_orders()
        
        if queued_orders:
            print(f"Found {len(queued_orders)} queued work orders:")
            for i, order in enumerate(queued_orders[:5], 1):  # Show first 5
                print(f"  {i}. {order.title} ({order.priority.value})")
                if order.assigned_to:
                    print(f"     Assigned to: {order.assigned_to}")
                if order.tags:
                    print(f"     Tags: {', '.join(order.tags)}")
        else:
            print("No queued work orders found")
        
        # Step 3: Search work orders
        print("\n🔍 Step 3: Searching work orders...")
        search_queries = ["urgent", "task", "bug", "feature"]
        
        for query in search_queries:
            results = indexer.search_work_orders(query)
            print(f"Search '{query}': {len(results)} results")
        
        # Step 4: Show statistics
        print("\n📊 Step 4: Work order statistics...")
        stats = indexer.get_work_order_statistics()
        
        print(f"Total work orders: {stats['total_work_orders']}")
        print(f"Last indexed: {stats['last_index_time'] or 'Never'}")
        
        print("\nStatus distribution:")
        for status, count in stats['status_distribution'].items():
            if count > 0:
                print(f"  {status}: {count}")
        
        print("\nPriority distribution:")
        for priority, count in stats['priority_distribution'].items():
            if count > 0:
                print(f"  {priority}: {count}")
        
        # Step 5: Export work orders
        print("\n💾 Step 5: Exporting work orders...")
        export_file = f"work_orders_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        indexer.export_work_orders(export_file)
        print(f"✅ Exported to: {export_file}")
        
        # Step 6: Demonstrate filtering
        print("\n🔍 Step 6: Filtering work orders...")
        
        # Filter by status
        in_progress_orders = indexer.index.get_work_orders_by_status(WorkOrderStatus.IN_PROGRESS)
        print(f"In progress work orders: {len(in_progress_orders)}")
        
        # Filter by priority
        high_priority_orders = indexer.index.get_work_orders_by_priority(WorkOrderPriority.HIGH)
        print(f"High priority work orders: {len(high_priority_orders)}")
        
        # Filter by tags
        if stats['tags_count'] > 0:
            all_tags = list(indexer.index.index_by_tags.keys())
            if all_tags:
                tag = all_tags[0]
                tagged_orders = indexer.index.get_work_orders_by_tag(tag)
                print(f"Work orders with tag '{tag}': {len(tagged_orders)}")
        
        print("\n✅ Demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


def demonstrate_manual_work_order_creation():
    """Demonstrate creating work orders manually"""
    print("\n🛠️  Manual Work Order Creation Demo")
    print("=" * 40)
    
    # Create a new indexer
    indexer = WorkOrderIndexer()
    
    # Create some sample work orders
    sample_work_orders = [
        WorkOrder(
            id="wo_001",
            title="Fix login authentication bug",
            description="Users are unable to log in with special characters in passwords",
            status=WorkOrderStatus.QUEUED,
            priority=WorkOrderPriority.HIGH,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            assigned_to="developer@company.com",
            tags=["bug", "authentication", "urgent"],
            metadata={"component": "auth", "version": "2.1.0"}
        ),
        WorkOrder(
            id="wo_002",
            title="Implement new dashboard feature",
            description="Add a new analytics dashboard for user metrics",
            status=WorkOrderStatus.IN_PROGRESS,
            priority=WorkOrderPriority.MEDIUM,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            assigned_to="frontend@company.com",
            tags=["feature", "dashboard", "analytics"],
            metadata={"component": "frontend", "version": "2.2.0"}
        ),
        WorkOrder(
            id="wo_003",
            title="Update documentation",
            description="Update API documentation for new endpoints",
            status=WorkOrderStatus.QUEUED,
            priority=WorkOrderPriority.LOW,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            assigned_to="docs@company.com",
            tags=["documentation", "api"],
            metadata={"component": "docs", "version": "2.1.0"}
        )
    ]
    
    # Add work orders to index
    for wo in sample_work_orders:
        indexer.index.add_work_order(wo)
        print(f"✅ Added work order: {wo.title}")
    
    # Show statistics
    stats = indexer.get_work_order_statistics()
    print(f"\n📊 Index statistics:")
    print(f"Total work orders: {stats['total_work_orders']}")
    
    # Search for work orders
    search_results = indexer.search_work_orders("dashboard")
    print(f"\n🔍 Search 'dashboard': {len(search_results)} results")
    for wo in search_results:
        print(f"  - {wo.title} ({wo.status.value})")
    
    # Export the index
    indexer.export_work_orders("sample_work_orders.json")
    print(f"\n💾 Exported sample work orders to: sample_work_orders.json")


async def main():
    """Main function"""
    print("🎯 Work Order Indexing Examples")
    print("=" * 50)
    
    # Run the main demonstration
    await demonstrate_work_order_indexing()
    
    # Run the manual creation demonstration
    demonstrate_manual_work_order_creation()
    
    print("\n🎉 All examples completed!")
    print("\nNext steps:")
    print("1. Run 'python work_order_cli.py index' to index real work orders")
    print("2. Run 'python work_order_cli.py list --status queued' to see queued orders")
    print("3. Run 'python work_order_cli.py search \"urgent\"' to search for urgent work")
    print("4. Run 'python work_order_cli.py stats' to see statistics")


if __name__ == "__main__":
    asyncio.run(main())