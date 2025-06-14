# test_mcp_server.py
import requests
import json
import time
import sys
from typing import Dict, Any

BASE_URL = "http://localhost:8001"

class MCPServerTester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, message: str, response_data: Any = None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "response_data": response_data
        })
        
    def test_server_health(self) -> bool:
        """Test if the MCP server is running and healthy"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Server Health", True, f"Server is healthy - Status: {data.get('status')}", data)
                return True
            else:
                self.log_test("Server Health", False, f"Health check failed with status {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Server Health", False, f"Cannot connect to server: {str(e)}")
            return False
    
    def test_mcp_endpoint(self) -> bool:
        """Test if MCP tools are exposed correctly"""
        try:
            response = self.session.get(f"{self.base_url}/mcp", timeout=10)
            if response.status_code == 200:
                # The MCP endpoint might return different formats, so we check if it's accessible
                self.log_test("MCP Endpoint", True, "MCP tools endpoint is accessible")
                return True
            else:
                self.log_test("MCP Endpoint", False, f"MCP endpoint returned status {response.status_code}")
                return False
        except Exception as e:
            self.log_test("MCP Endpoint", False, f"MCP endpoint error: {str(e)}")
            return False
    
    def test_pipeline_status(self) -> bool:
        """Test pipeline status endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/pipeline_status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Pipeline Status", True, f"Pipeline status retrieved", data)
                return True
            else:
                self.log_test("Pipeline Status", False, f"Status endpoint failed with {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Pipeline Status", False, f"Status endpoint error: {str(e)}")
            return False
    
    def test_reddit_scraping(self, posts_per_subreddit: int = 5) -> Dict[str, Any]:
        """Test Reddit scraping functionality with minimal posts"""
        try:
            payload = {
                "scrapes_per_subreddit": posts_per_subreddit,
                "subreddits_file": "subreddits.txt"
            }
            
            print(f"🔄 Testing Reddit scraping with {posts_per_subreddit} posts per subreddit...")
            response = self.session.post(f"{self.base_url}/scrape_reddit", json=payload, timeout=300)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Reddit Scraping", True, 
                            f"Scraped {data['total_posts_scraped']} posts in {data['processing_time']}s", data)
                return data
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.headers.get('content-type', '').startswith('application/json') else response.text
                self.log_test("Reddit Scraping", False, f"Scraping failed: {error_detail}")
                return {}
        except Exception as e:
            self.log_test("Reddit Scraping", False, f"Scraping error: {str(e)}")
            return {}
    
    def test_vector_database(self, run_path: str) -> Dict[str, Any]:
        """Test vector database creation"""
        try:
            payload = {
                "run_path": run_path,
                "batch_size": 50,  # Smaller batch for testing
                "index_name": "test-tech-ideas",
                "vector_model": "llama-text-embed-v2"
            }
            
            print("🔄 Testing vector database creation...")
            response = self.session.post(f"{self.base_url}/create_vector_database", json=payload, timeout=300)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Vector Database", True, 
                            f"Created vectors for {data['records_uploaded']} records in {data['processing_time']}s", data)
                return data
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.headers.get('content-type', '').startswith('application/json') else response.text
                self.log_test("Vector Database", False, f"Vector creation failed: {error_detail}")
                return {}
        except Exception as e:
            self.log_test("Vector Database", False, f"Vector creation error: {str(e)}")
            return {}
    
    def test_vector_search(self, run_path: str) -> Dict[str, Any]:
        """Test vector search functionality"""
        try:
            payload = {
                "query": "AI MCP server ideas for development",
                "index_name": "test-tech-ideas",
                "run_path": run_path,
                "top_k": 10
            }
            
            print("🔄 Testing vector search...")
            response = self.session.post(f"{self.base_url}/search_vectors", json=payload, timeout=120)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Vector Search", True, 
                            f"Found {data['results_count']} results in {data['search_time']}s", data)
                return data
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.headers.get('content-type', '').startswith('application/json') else response.text
                self.log_test("Vector Search", False, f"Search failed: {error_detail}")
                return {}
        except Exception as e:
            self.log_test("Vector Search", False, f"Search error: {str(e)}")
            return {}
    
    def test_ai_analysis(self, run_path: str) -> Dict[str, Any]:
        """Test AI analysis functionality"""
        try:
            payload = {
                "query": "Generate 3 AI MCP server product ideas based on the search results",
                "run_path": run_path,
                "model": "gemini-2.0-flash-exp"
            }
            
            print("🔄 Testing AI analysis...")
            response = self.session.post(f"{self.base_url}/analyze_with_ai", json=payload, timeout=180)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("AI Analysis", True, 
                            f"Generated {data['word_count']} words in {data['processing_time']}s", data)
                return data
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.headers.get('content-type', '').startswith('application/json') else response.text
                self.log_test("AI Analysis", False, f"AI analysis failed: {error_detail}")
                return {}
        except Exception as e:
            self.log_test("AI Analysis", False, f"AI analysis error: {str(e)}")
            return {}
    
    def test_full_pipeline(self) -> Dict[str, Any]:
        """Test the complete pipeline workflow"""
        try:
            params = {
                "scrapes_per_subreddit": 3,  # Very small for testing
                "search_query": "AI development tools and frameworks",
                "analysis_query": "Suggest 2 practical AI development tools based on the data"
            }
            
            print("🔄 Testing full pipeline execution...")
            response = self.session.post(f"{self.base_url}/run_full_pipeline", params=params, timeout=600)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Full Pipeline", True, 
                            f"Completed full pipeline in {data['total_processing_time']}s", data['summary'])
                return data
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.headers.get('content-type', '').startswith('application/json') else response.text
                self.log_test("Full Pipeline", False, f"Full pipeline failed: {error_detail}")
                return {}
        except Exception as e:
            self.log_test("Full Pipeline", False, f"Full pipeline error: {str(e)}")
            return {}
    
    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("🚀 Starting MCP Server Comprehensive Test Suite")
        print("=" * 60)
        
        # Test 1: Server Health
        if not self.test_server_health():
            print("❌ Server is not running. Please start the MCP server first.")
            return False
        
        # Test 2: MCP Endpoint
        self.test_mcp_endpoint()
        
        # Test 3: Pipeline Status
        self.test_pipeline_status()
        
        # Test 4: Individual Pipeline Steps (with small data)
        print("\n📊 Testing Individual Pipeline Steps:")
        print("-" * 40)
        
        # Test Reddit scraping
        scrape_result = self.test_reddit_scraping(posts_per_subreddit=3)
        if not scrape_result.get('success'):
            print("❌ Skipping subsequent tests due to scraping failure")
            return False
        
        run_path = scrape_result.get('run_path')
        if not run_path:
            print("❌ No run path returned from scraping")
            return False
        
        # Test vector database creation
        vector_result = self.test_vector_database(run_path)
        if not vector_result.get('success'):
            print("⚠️  Vector database test failed, but continuing...")
        
        # Test vector search
        search_result = self.test_vector_search(run_path)
        if not search_result.get('success'):
            print("⚠️  Vector search test failed, but continuing...")
        
        # Test AI analysis
        ai_result = self.test_ai_analysis(run_path)
        if not ai_result.get('success'):
            print("⚠️  AI analysis test failed, but continuing...")
        
        # Test 5: Full Pipeline (if individual tests passed)
        print("\n🔗 Testing Full Pipeline Integration:")
        print("-" * 40)
        self.test_full_pipeline()
        
        # Summary
        self.print_test_summary()
        return True
    
    def run_quick_test(self):
        """Run quick tests for development"""
        print("⚡ Running Quick MCP Server Test")
        print("=" * 40)
        
        # Quick health check
        if not self.test_server_health():
            return False
        
        # Test MCP endpoint
        self.test_mcp_endpoint()
        
        # Test status
        self.test_pipeline_status()
        
        print("\n✅ Quick test completed. Server appears to be working!")
        return True
    
    def print_test_summary(self):
        """Print a summary of all test results"""
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if total - passed > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['message']}")
        
        print("\n🎯 MCP Server Test Complete!")

def main():
    """Main test runner"""
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        # Quick test mode
        tester = MCPServerTester()
        tester.run_quick_test()
    else:
        # Comprehensive test mode
        tester = MCPServerTester()
        tester.run_comprehensive_test()

if __name__ == "__main__":
    main() 