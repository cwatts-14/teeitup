#!/usr/bin/env python3
"""
Example usage of Factory.8090.ai integration client.

This script demonstrates how to use the integration client to explore
and interact with the Factory.8090.ai service.
"""

import asyncio
import json
from factory_client import Factory8090Client


async def explore_service():
    """Explore the Factory.8090.ai service"""
    print("🔍 Exploring Factory.8090.ai service...")
    
    async with Factory8090Client() as client:
        # Step 1: Discover service information
        print("\n📋 Step 1: Discovering service information...")
        service_info = await client.discover_service_info()
        
        print(f"Service Name: {service_info.name}")
        print(f"Status: {service_info.status}")
        print(f"Capabilities: {service_info.capabilities}")
        print(f"API Endpoints: {service_info.api_endpoints}")
        
        # Step 2: Extract page data
        print("\n📄 Step 2: Extracting page data...")
        page_data = await client.extract_page_data()
        
        print(f"Page Title: {page_data['title']}")
        print(f"Page URL: {page_data['url']}")
        print(f"Content Length: {page_data['content_length']} characters")
        print(f"UI Elements: {page_data['elements']}")
        
        # Step 3: Test API endpoints (if any discovered)
        if service_info.api_endpoints:
            print("\n🔌 Step 3: Testing discovered API endpoints...")
            api_results = await client.test_api_endpoints(service_info.api_endpoints)
            
            for endpoint, result in api_results.items():
                if result.get('success'):
                    print(f"✅ {endpoint}: {result['status_code']} - {result['content_type']}")
                else:
                    print(f"❌ {endpoint}: {result.get('status_code', 'Error')}")
        else:
            print("\n🔌 Step 3: No API endpoints discovered for testing")
            
        # Step 4: Generate integration report
        print("\n📊 Step 4: Generating integration report...")
        report = {
            "service_discovery": service_info.dict(),
            "page_analysis": page_data,
            "api_testing": api_results if service_info.api_endpoints else {},
            "recommendations": generate_recommendations(service_info, page_data)
        }
        
        # Save report to file
        with open("factory_8090_integration_report.json", "w") as f:
            json.dump(report, f, indent=2)
            
        print("📁 Integration report saved to: factory_8090_integration_report.json")
        
        return report


def generate_recommendations(service_info, page_data):
    """Generate integration recommendations based on discovered information"""
    recommendations = []
    
    # Analyze service capabilities
    if not service_info.api_endpoints:
        recommendations.append({
            "type": "api_discovery",
            "priority": "high",
            "description": "No API endpoints discovered. Consider browser automation for integration.",
            "action": "Implement Playwright/Selenium automation for service interaction"
        })
    
    # Analyze page structure
    if page_data['elements']['forms'] > 0:
        recommendations.append({
            "type": "form_automation",
            "priority": "medium",
            "description": f"Found {page_data['elements']['forms']} forms. Consider form automation.",
            "action": "Implement form filling and submission automation"
        })
    
    if page_data['elements']['buttons'] > 0:
        recommendations.append({
            "type": "ui_automation",
            "priority": "medium",
            "description": f"Found {page_data['elements']['buttons']} buttons. Consider UI automation.",
            "action": "Implement button clicking and UI interaction automation"
        })
    
    # Service health recommendations
    if service_info.status != "healthy":
        recommendations.append({
            "type": "health_monitoring",
            "priority": "high",
            "description": f"Service status is {service_info.status}. Implement health monitoring.",
            "action": "Set up regular health checks and alerting"
        })
    
    # General recommendations
    recommendations.extend([
        {
            "type": "error_handling",
            "priority": "high",
            "description": "Implement robust error handling and retry mechanisms.",
            "action": "Add exponential backoff and comprehensive error logging"
        },
        {
            "type": "monitoring",
            "priority": "medium",
            "description": "Set up monitoring and alerting for the integration.",
            "action": "Implement metrics collection and alerting system"
        },
        {
            "type": "security",
            "priority": "high",
            "description": "Ensure secure credential management and data handling.",
            "action": "Implement secure authentication and data encryption"
        }
    ])
    
    return recommendations


async def main():
    """Main function"""
    try:
        print("🚀 Factory.8090.ai Integration Explorer")
        print("=" * 50)
        
        report = await explore_service()
        
        print("\n✅ Exploration completed successfully!")
        print(f"📊 Generated {len(report['recommendations'])} recommendations")
        
        # Display top recommendations
        high_priority = [r for r in report['recommendations'] if r['priority'] == 'high']
        if high_priority:
            print(f"\n🎯 High Priority Recommendations:")
            for i, rec in enumerate(high_priority, 1):
                print(f"{i}. {rec['description']}")
                print(f"   Action: {rec['action']}")
        
    except Exception as e:
        print(f"❌ Error during exploration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())