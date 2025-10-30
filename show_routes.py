"""
Display all registered Flask routes
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app import create_app

def display_routes():
    app = create_app()
    
    print("🚀 FB Daily Posts API - All Available Routes\n")
    print("=" * 80)
    
    routes = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
        if methods:  # Only show routes with actual methods
            routes.append({
                'endpoint': rule.rule,
                'methods': methods,
                'function': rule.endpoint
            })
    
    # Sort routes by endpoint
    routes.sort(key=lambda x: x['endpoint'])
    
    # Group routes by category
    auth_routes = [r for r in routes if r['endpoint'].startswith('/api/auth')]
    post_routes = [r for r in routes if r['endpoint'].startswith('/api/posts')]
    social_routes = [r for r in routes if r['endpoint'].startswith('/api/social')]
    compat_routes = [r for r in routes if r['endpoint'].startswith('/api/') and not any(
        r['endpoint'].startswith(prefix) for prefix in ['/api/auth', '/api/posts', '/api/social']
    )]
    health_routes = [r for r in routes if r['endpoint'] in ['/', '/health']]
    
    def print_route_group(title, routes_list):
        if routes_list:
            print(f"\n📍 {title}")
            print("-" * 50)
            for route in routes_list:
                print(f"   {route['methods']:<12} {route['endpoint']:<35} -> {route['function']}")
    
    print_route_group("HEALTH CHECK", health_routes)
    print_route_group("AUTHENTICATION", auth_routes)
    print_route_group("POST MANAGEMENT", post_routes)
    print_route_group("SOCIAL MEDIA & AI", social_routes)
    print_route_group("COMPATIBILITY (Legacy)", compat_routes)
    
    print(f"\n{'='*80}")
    print(f"Total Routes: {len(routes)}")
    print(f"Server: http://127.0.0.1:8000")
    print(f"{'='*80}")

if __name__ == "__main__":
    display_routes()