#!/usr/bin/env python3
"""
Work Order CLI Tool for 8090 Integrations

A command-line interface for indexing and managing work orders from the
Factory.8090.ai service.
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime
from typing import List, Optional

from work_order_indexer import WorkOrderIndexer, WorkOrderStatus, WorkOrderPriority


class WorkOrderCLI:
    """Command-line interface for work order management"""
    
    def __init__(self):
        self.indexer = WorkOrderIndexer()
    
    async def index_command(self, args) -> None:
        """Index work orders from 8090 integrations"""
        print("🔍 Indexing work orders from 8090 integrations...")
        
        try:
            stats = await self.indexer.index_work_orders()
            
            print(f"✅ Indexing completed!")
            print(f"📊 Total work orders: {stats['total_work_orders']}")
            print(f"⏱️  Duration: {stats['indexing_duration']:.2f} seconds")
            print(f"🔍 Discovered: {stats['discovered_count']}")
            print(f"📝 Indexed: {stats['indexed_count']}")
            
            # Show status distribution
            print(f"\n📈 Status Distribution:")
            for status, count in stats['status_distribution'].items():
                if count > 0:
                    print(f"  {status}: {count}")
            
            # Show priority distribution
            print(f"\n🎯 Priority Distribution:")
            for priority, count in stats['priority_distribution'].items():
                if count > 0:
                    print(f"  {priority}: {count}")
            
            # Export if requested
            if args.export:
                self.indexer.export_work_orders(args.export)
                print(f"\n📁 Exported to: {args.export}")
            
        except Exception as e:
            print(f"❌ Error during indexing: {e}")
            sys.exit(1)
    
    def list_command(self, args) -> None:
        """List work orders"""
        if args.status:
            try:
                status = WorkOrderStatus(args.status)
                work_orders = self.indexer.index.get_work_orders_by_status(status)
            except ValueError:
                print(f"❌ Invalid status: {args.status}")
                print(f"Valid statuses: {', '.join([s.value for s in WorkOrderStatus])}")
                sys.exit(1)
        elif args.priority:
            try:
                priority = WorkOrderPriority(args.priority)
                work_orders = self.indexer.index.get_work_orders_by_priority(priority)
            except ValueError:
                print(f"❌ Invalid priority: {args.priority}")
                print(f"Valid priorities: {', '.join([p.value for p in WorkOrderPriority])}")
                sys.exit(1)
        elif args.assigned:
            work_orders = self.indexer.index.get_work_orders_by_assigned(args.assigned)
        elif args.tag:
            work_orders = self.indexer.index.get_work_orders_by_tag(args.tag)
        else:
            work_orders = list(self.indexer.index.work_orders.values())
        
        if not work_orders:
            print("📭 No work orders found")
            return
        
        # Sort by created date (newest first)
        work_orders.sort(key=lambda x: x.created_at, reverse=True)
        
        # Limit results
        if args.limit:
            work_orders = work_orders[:args.limit]
        
        print(f"📋 Found {len(work_orders)} work orders:")
        print()
        
        for i, wo in enumerate(work_orders, 1):
            print(f"{i:3d}. {wo.title}")
            print(f"     ID: {wo.id}")
            print(f"     Status: {wo.status.value}")
            print(f"     Priority: {wo.priority.value}")
            print(f"     Created: {wo.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            if wo.assigned_to:
                print(f"     Assigned: {wo.assigned_to}")
            if wo.tags:
                print(f"     Tags: {', '.join(wo.tags)}")
            if wo.description:
                desc = wo.description[:100] + "..." if len(wo.description) > 100 else wo.description
                print(f"     Description: {desc}")
            print()
    
    def search_command(self, args) -> None:
        """Search work orders"""
        if not args.query:
            print("❌ Search query is required")
            sys.exit(1)
        
        print(f"🔍 Searching for: '{args.query}'")
        
        work_orders = self.indexer.search_work_orders(args.query)
        
        if not work_orders:
            print("📭 No work orders found matching your search")
            return
        
        print(f"📋 Found {len(work_orders)} matching work orders:")
        print()
        
        for i, wo in enumerate(work_orders, 1):
            print(f"{i:3d}. {wo.title}")
            print(f"     ID: {wo.id}")
            print(f"     Status: {wo.status.value}")
            print(f"     Priority: {wo.priority.value}")
            print(f"     Created: {wo.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            if wo.assigned_to:
                print(f"     Assigned: {wo.assigned_to}")
            print()
    
    def stats_command(self, args) -> None:
        """Show work order statistics"""
        stats = self.indexer.get_work_order_statistics()
        
        print("📊 Work Order Statistics")
        print("=" * 30)
        print(f"Total work orders: {stats['total_work_orders']}")
        print(f"Last indexed: {stats['last_index_time'] or 'Never'}")
        print()
        
        print("📈 Status Distribution:")
        for status, count in stats['status_distribution'].items():
            if count > 0:
                print(f"  {status}: {count}")
        print()
        
        print("🎯 Priority Distribution:")
        for priority, count in stats['priority_distribution'].items():
            if count > 0:
                print(f"  {priority}: {count}")
        print()
        
        print("👥 Assignment Info:")
        print(f"  Assigned work orders: {stats['assigned_count']}")
        print(f"  Unique tags: {stats['tags_count']}")
        print(f"  Search index size: {stats['search_index_size']}")
    
    def export_command(self, args) -> None:
        """Export work orders to JSON"""
        if not args.output:
            print("❌ Output file is required")
            sys.exit(1)
        
        self.indexer.export_work_orders(args.output)
        print(f"✅ Work orders exported to: {args.output}")
    
    def import_command(self, args) -> None:
        """Import work orders from JSON"""
        if not args.input:
            print("❌ Input file is required")
            sys.exit(1)
        
        self.indexer.import_work_orders(args.input)
        print(f"✅ Work orders imported from: {args.input}")
    
    def show_command(self, args) -> None:
        """Show details of a specific work order"""
        if not args.work_order_id:
            print("❌ Work order ID is required")
            sys.exit(1)
        
        work_order = self.indexer.index.get_work_order(args.work_order_id)
        
        if not work_order:
            print(f"❌ Work order not found: {args.work_order_id}")
            sys.exit(1)
        
        print(f"📋 Work Order Details")
        print("=" * 30)
        print(f"ID: {work_order.id}")
        print(f"Title: {work_order.title}")
        print(f"Description: {work_order.description}")
        print(f"Status: {work_order.status.value}")
        print(f"Priority: {work_order.priority.value}")
        print(f"Created: {work_order.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Updated: {work_order.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if work_order.assigned_to:
            print(f"Assigned to: {work_order.assigned_to}")
        
        if work_order.due_date:
            print(f"Due date: {work_order.due_date.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if work_order.tags:
            print(f"Tags: {', '.join(work_order.tags)}")
        
        if work_order.metadata:
            print(f"Metadata: {json.dumps(work_order.metadata, indent=2)}")


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Work Order CLI for 8090 Integrations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s index --export work_orders.json
  %(prog)s list --status queued --limit 10
  %(prog)s search "urgent task"
  %(prog)s stats
  %(prog)s show work_order_123
  %(prog)s export --output backup.json
  %(prog)s import --input backup.json
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Index command
    index_parser = subparsers.add_parser('index', help='Index work orders from 8090 integrations')
    index_parser.add_argument('--export', help='Export indexed work orders to JSON file')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List work orders')
    list_parser.add_argument('--status', help='Filter by status')
    list_parser.add_argument('--priority', help='Filter by priority')
    list_parser.add_argument('--assigned', help='Filter by assignee')
    list_parser.add_argument('--tag', help='Filter by tag')
    list_parser.add_argument('--limit', type=int, help='Limit number of results')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search work orders')
    search_parser.add_argument('query', help='Search query')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show work order statistics')
    
    # Show command
    show_parser = subparsers.add_parser('show', help='Show work order details')
    show_parser.add_argument('work_order_id', help='Work order ID')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export work orders to JSON')
    export_parser.add_argument('--output', required=True, help='Output file path')
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import work orders from JSON')
    import_parser.add_argument('--input', required=True, help='Input file path')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    cli = WorkOrderCLI()
    
    try:
        if args.command == 'index':
            asyncio.run(cli.index_command(args))
        elif args.command == 'list':
            cli.list_command(args)
        elif args.command == 'search':
            cli.search_command(args)
        elif args.command == 'stats':
            cli.stats_command(args)
        elif args.command == 'show':
            cli.show_command(args)
        elif args.command == 'export':
            cli.export_command(args)
        elif args.command == 'import':
            cli.import_command(args)
        else:
            print(f"❌ Unknown command: {args.command}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()