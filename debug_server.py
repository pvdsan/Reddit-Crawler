# debug_server.py
import requests
import json

def debug_server():
    base_url = "http://localhost:8001"
    
    print("🔍 Debugging MCP Server...")
    
    try:
        # Test if server is running
        response = requests.get(f"{base_url}/docs", timeout=5)
        print(f"✅ Server is running - Status: {response.status_code}")
        
        # Get OpenAPI schema
        response = requests.get(f"{base_url}/openapi.json", timeout=5)
        if response.status_code == 200:
            schema = response.json()
            print(f"\n📋 Server Info:")
            print(f"   Title: {schema.get('info', {}).get('title', 'Unknown')}")
            print(f"   Version: {schema.get('info', {}).get('version', 'Unknown')}")
            
            print(f"\n🛠️  Available Endpoints:")
            paths = schema.get('paths', {})
            if paths:
                for path, methods in paths.items():
                    method_list = list(methods.keys())
                    print(f"   {path} - {', '.join(method_list).upper()}")
            else:
                print("   No endpoints found!")
                
            # Test specific endpoints
            print(f"\n🧪 Testing Key Endpoints:")
            test_endpoints = ["/health", "/mcp", "/scrape_reddit", "/pipeline_status"]
            
            for endpoint in test_endpoints:
                try:
                    resp = requests.get(f"{base_url}{endpoint}", timeout=3)
                    print(f"   {endpoint}: {resp.status_code}")
                except Exception as e:
                    print(f"   {endpoint}: ERROR - {str(e)}")
                    
        else:
            print(f"❌ Could not get OpenAPI schema: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Server connection failed: {e}")

if __name__ == "__main__":
    debug_server() 