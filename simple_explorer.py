#!/usr/bin/env python3
"""
Simple Factory.8090.ai Integration Explorer

A simplified version that works with basic Python packages to explore
the Factory.8090.ai service.
"""

import json
import re
import urllib.request
import urllib.parse
from typing import Dict, List, Any


class SimpleFactoryExplorer:
    """Simple explorer for Factory.8090.ai service"""
    
    def __init__(self, base_url: str = "https://factory.8090.ai"):
        self.base_url = base_url
        
    def fetch_page_content(self) -> Dict[str, Any]:
        """Fetch and analyze the main page content"""
        print(f"🔍 Fetching content from {self.base_url}")
        
        try:
            # Create request with proper headers
            req = urllib.request.Request(
                self.base_url,
                headers={
                    'User-Agent': 'Factory.8090.ai Integration Explorer/1.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                }
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                content = response.read()
                
                # Try to decode as UTF-8
                try:
                    html_content = content.decode('utf-8')
                except UnicodeDecodeError:
                    html_content = content.decode('utf-8', errors='ignore')
                
                return {
                    'status_code': response.getcode(),
                    'headers': dict(response.headers),
                    'content_length': len(content),
                    'content': html_content,
                    'success': True
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'status_code': None
            }
    
    def analyze_content(self, content: str) -> Dict[str, Any]:
        """Analyze the HTML content for integration opportunities"""
        analysis = {
            'title': '',
            'meta_tags': {},
            'scripts': [],
            'api_endpoints': [],
            'forms': [],
            'links': [],
            'potential_apis': [],
            'service_info': {}
        }
        
        # Extract title
        title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
        if title_match:
            analysis['title'] = title_match.group(1).strip()
        
        # Extract meta tags
        meta_pattern = r'<meta[^>]*name=["\']([^"\']*)["\'][^>]*content=["\']([^"\']*)["\'][^>]*>'
        for match in re.finditer(meta_pattern, content, re.IGNORECASE):
            analysis['meta_tags'][match.group(1)] = match.group(2)
        
        # Extract script sources
        script_pattern = r'<script[^>]*src=["\']([^"\']*)["\'][^>]*>'
        for match in re.finditer(script_pattern, content, re.IGNORECASE):
            analysis['scripts'].append(match.group(1))
        
        # Look for potential API endpoints
        api_patterns = [
            r'["\']([^"\']*api[^"\']*)["\']',
            r'["\']([^"\']*endpoint[^"\']*)["\']',
            r'["\']([^"\']*service[^"\']*)["\']',
            r'["\']([^"\']*v\d+[^"\']*)["\']',  # Versioned APIs
        ]
        
        for pattern in api_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            analysis['potential_apis'].extend(matches)
        
        # Extract forms
        form_pattern = r'<form[^>]*>(.*?)</form>'
        for match in re.finditer(form_pattern, content, re.IGNORECASE | re.DOTALL):
            form_content = match.group(1)
            form_info = {
                'action': '',
                'method': 'GET',
                'inputs': []
            }
            
            # Extract form action
            action_match = re.search(r'action=["\']([^"\']*)["\']', form_content, re.IGNORECASE)
            if action_match:
                form_info['action'] = action_match.group(1)
            
            # Extract form method
            method_match = re.search(r'method=["\']([^"\']*)["\']', form_content, re.IGNORECASE)
            if method_match:
                form_info['method'] = method_match.group(1).upper()
            
            # Extract input fields
            input_pattern = r'<input[^>]*name=["\']([^"\']*)["\'][^>]*>'
            for input_match in re.finditer(input_pattern, form_content, re.IGNORECASE):
                form_info['inputs'].append(input_match.group(1))
            
            analysis['forms'].append(form_info)
        
        # Extract links
        link_pattern = r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>'
        for match in re.finditer(link_pattern, content, re.IGNORECASE):
            analysis['links'].append(match.group(1))
        
        # Look for service information
        service_patterns = {
            'version': r'version["\']?\s*[:=]\s*["\']([^"\']*)["\']',
            'name': r'name["\']?\s*[:=]\s*["\']([^"\']*)["\']',
            'description': r'description["\']?\s*[:=]\s*["\']([^"\']*)["\']',
        }
        
        for key, pattern in service_patterns.items():
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                analysis['service_info'][key] = match.group(1)
        
        return analysis
    
    def test_endpoints(self, endpoints: List[str]) -> Dict[str, Any]:
        """Test potential API endpoints"""
        results = {}
        
        for endpoint in endpoints[:10]:  # Limit to first 10 endpoints
            if not endpoint.startswith('http'):
                endpoint = urllib.parse.urljoin(self.base_url, endpoint)
            
            try:
                req = urllib.request.Request(
                    endpoint,
                    headers={'User-Agent': 'Factory.8090.ai Integration Explorer/1.0'}
                )
                
                with urllib.request.urlopen(req, timeout=10) as response:
                    results[endpoint] = {
                        'status_code': response.getcode(),
                        'content_type': response.headers.get('content-type', ''),
                        'success': 200 <= response.getcode() < 300,
                        'size': len(response.read())
                    }
                    
            except Exception as e:
                results[endpoint] = {
                    'error': str(e),
                    'success': False
                }
        
        return results
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive integration report"""
        print("📊 Generating integration report...")
        
        # Fetch page content
        page_data = self.fetch_page_content()
        
        if not page_data['success']:
            return {
                'error': 'Failed to fetch page content',
                'details': page_data
            }
        
        # Analyze content
        analysis = self.analyze_content(page_data['content'])
        
        # Test potential endpoints
        api_results = {}
        if analysis['potential_apis']:
            api_results = self.test_endpoints(analysis['potential_apis'])
        
        # Generate recommendations
        recommendations = self.generate_recommendations(analysis, api_results)
        
        report = {
            'service_info': {
                'url': self.base_url,
                'title': analysis['title'],
                'status_code': page_data['status_code'],
                'content_length': page_data['content_length'],
                'service_details': analysis['service_info']
            },
            'content_analysis': analysis,
            'api_testing': api_results,
            'recommendations': recommendations,
            'integration_opportunities': self.identify_integration_opportunities(analysis, api_results)
        }
        
        return report
    
    def generate_recommendations(self, analysis: Dict, api_results: Dict) -> List[Dict]:
        """Generate integration recommendations"""
        recommendations = []
        
        # Check for API endpoints
        if not analysis['potential_apis']:
            recommendations.append({
                'type': 'api_discovery',
                'priority': 'high',
                'description': 'No obvious API endpoints found. Consider browser automation.',
                'action': 'Implement Playwright or Selenium for service interaction'
            })
        else:
            successful_apis = [k for k, v in api_results.items() if v.get('success')]
            if successful_apis:
                recommendations.append({
                    'type': 'api_integration',
                    'priority': 'high',
                    'description': f'Found {len(successful_apis)} working API endpoints.',
                    'action': 'Implement REST client for discovered endpoints'
                })
        
        # Check for forms
        if analysis['forms']:
            recommendations.append({
                'type': 'form_automation',
                'priority': 'medium',
                'description': f'Found {len(analysis["forms"])} forms for automation.',
                'action': 'Implement form filling and submission automation'
            })
        
        # Check for JavaScript
        if analysis['scripts']:
            recommendations.append({
                'type': 'javascript_analysis',
                'priority': 'medium',
                'description': f'Found {len(analysis["scripts"])} JavaScript files. May contain API calls.',
                'action': 'Analyze JavaScript files for hidden API endpoints'
            })
        
        # General recommendations
        recommendations.extend([
            {
                'type': 'monitoring',
                'priority': 'high',
                'description': 'Implement service monitoring and health checks.',
                'action': 'Set up regular health checks and alerting'
            },
            {
                'type': 'security',
                'priority': 'high',
                'description': 'Ensure secure integration practices.',
                'action': 'Implement proper authentication and data encryption'
            }
        ])
        
        return recommendations
    
    def identify_integration_opportunities(self, analysis: Dict, api_results: Dict) -> List[Dict]:
        """Identify specific integration opportunities"""
        opportunities = []
        
        # API integration opportunities
        successful_apis = [k for k, v in api_results.items() if v.get('success')]
        if successful_apis:
            opportunities.append({
                'type': 'REST API Integration',
                'endpoints': successful_apis,
                'complexity': 'Medium',
                'description': 'Direct API integration using HTTP clients'
            })
        
        # Form automation opportunities
        if analysis['forms']:
            opportunities.append({
                'type': 'Form Automation',
                'forms': analysis['forms'],
                'complexity': 'Medium',
                'description': 'Automate form interactions using browser automation'
            })
        
        # Web scraping opportunities
        if analysis['links']:
            opportunities.append({
                'type': 'Web Scraping',
                'links': analysis['links'][:10],  # First 10 links
                'complexity': 'Low',
                'description': 'Extract data from web pages'
            })
        
        return opportunities


def main():
    """Main function to run the exploration"""
    print("🚀 Factory.8090.ai Integration Explorer")
    print("=" * 50)
    
    explorer = SimpleFactoryExplorer()
    report = explorer.generate_report()
    
    # Save report
    with open('factory_8090_integration_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    # Display summary
    print(f"\n✅ Exploration completed!")
    print(f"📄 Service: {report['service_info']['title']}")
    print(f"🌐 Status: {report['service_info']['status_code']}")
    print(f"📊 Content Length: {report['service_info']['content_length']} bytes")
    
    if 'content_analysis' in report:
        analysis = report['content_analysis']
        print(f"🔗 Links Found: {len(analysis['links'])}")
        print(f"📝 Forms Found: {len(analysis['forms'])}")
        print(f"📜 Scripts Found: {len(analysis['scripts'])}")
        print(f"🔌 Potential APIs: {len(analysis['potential_apis'])}")
    
    print(f"💡 Recommendations: {len(report['recommendations'])}")
    print(f"🎯 Integration Opportunities: {len(report['integration_opportunities'])}")
    
    print(f"\n📁 Detailed report saved to: factory_8090_integration_report.json")
    
    # Show high priority recommendations
    high_priority = [r for r in report['recommendations'] if r['priority'] == 'high']
    if high_priority:
        print(f"\n🎯 High Priority Recommendations:")
        for i, rec in enumerate(high_priority, 1):
            print(f"{i}. {rec['description']}")
            print(f"   Action: {rec['action']}")


if __name__ == "__main__":
    main()