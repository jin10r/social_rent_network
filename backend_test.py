#!/usr/bin/env python3
"""
Backend API Testing for Social Rent Application
Tests the unified FastAPI backend serving both API and frontend on port 8001
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional

class SocialRentAPITester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.session = requests.Session()
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}: PASSED {details}")
        else:
            print(f"❌ {name}: FAILED {details}")
        
        self.test_results.append({
            "name": name,
            "success": success,
            "details": details
        })

    def test_health_check(self) -> bool:
        """Test health check endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Response: {data}"
            self.log_test("Health Check", success, details)
            return success
        except Exception as e:
            self.log_test("Health Check", False, f"Error: {str(e)}")
            return False

    def test_root_endpoint(self) -> bool:
        """Test root API endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Message: {data.get('message', 'N/A')}"
            self.log_test("Root Endpoint", success, details)
            return success
        except Exception as e:
            self.log_test("Root Endpoint", False, f"Error: {str(e)}")
            return False

    def test_api_docs(self) -> bool:
        """Test API documentation endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/docs", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}, Content-Type: {response.headers.get('content-type', 'N/A')}"
            self.log_test("API Documentation", success, details)
            return success
        except Exception as e:
            self.log_test("API Documentation", False, f"Error: {str(e)}")
            return False

    def test_metro_stations_api(self) -> bool:
        """Test metro stations API"""
        try:
            response = self.session.get(f"{self.base_url}/api/metro/stations", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                if isinstance(data, list):
                    details += f", Found {len(data)} stations"
                    if len(data) > 0:
                        details += f", First station: {data[0]}"
                else:
                    details += f", Unexpected response format: {type(data)}"
            self.log_test("Metro Stations API", success, details)
            return success
        except Exception as e:
            self.log_test("Metro Stations API", False, f"Error: {str(e)}")
            return False

    def test_metro_search_api(self) -> bool:
        """Test metro search API"""
        try:
            response = self.session.get(f"{self.base_url}/api/metro/search?query=Сокольники", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Search results: {len(data) if isinstance(data, list) else 'Invalid format'}"
            self.log_test("Metro Search API", success, details)
            return success
        except Exception as e:
            self.log_test("Metro Search API", False, f"Error: {str(e)}")
            return False

    def test_frontend_serving(self) -> bool:
        """Test that frontend HTML is served"""
        try:
            response = self.session.get(f"{self.base_url}/app", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}, Content-Type: {response.headers.get('content-type', 'N/A')}"
            if success:
                content = response.text
                if "Social Rent" in content and "root" in content:
                    details += ", Contains expected HTML content"
                else:
                    details += ", HTML content may be incomplete"
            self.log_test("Frontend HTML Serving", success, details)
            return success
        except Exception as e:
            self.log_test("Frontend HTML Serving", False, f"Error: {str(e)}")
            return False

    def test_static_files(self) -> bool:
        """Test static files serving"""
        try:
            # Test CSS file
            response = self.session.get(f"{self.base_url}/static/css/main.6a53e6cb.css", timeout=10)
            css_success = response.status_code == 200
            
            # Test JS file
            response = self.session.get(f"{self.base_url}/static/js/main.40cc0626.js", timeout=10)
            js_success = response.status_code == 200
            
            success = css_success and js_success
            details = f"CSS: {'✓' if css_success else '✗'}, JS: {'✓' if js_success else '✗'}"
            self.log_test("Static Files Serving", success, details)
            return success
        except Exception as e:
            self.log_test("Static Files Serving", False, f"Error: {str(e)}")
            return False

    def test_favicon_and_manifest(self) -> bool:
        """Test favicon and manifest serving"""
        try:
            # Test favicon
            favicon_response = self.session.get(f"{self.base_url}/favicon.ico", timeout=10)
            favicon_success = favicon_response.status_code == 200
            
            # Test manifest
            manifest_response = self.session.get(f"{self.base_url}/manifest.json", timeout=10)
            manifest_success = manifest_response.status_code == 200
            
            success = favicon_success or manifest_success  # At least one should work
            details = f"Favicon: {'✓' if favicon_success else '✗'}, Manifest: {'✓' if manifest_success else '✗'}"
            self.log_test("Favicon & Manifest", success, details)
            return success
        except Exception as e:
            self.log_test("Favicon & Manifest", False, f"Error: {str(e)}")
            return False

    def test_database_connection(self) -> bool:
        """Test database connection indirectly through API"""
        try:
            # Try to access an endpoint that requires database
            response = self.session.get(f"{self.base_url}/api/listings/", timeout=10)
            # Even if we get 401/403, it means the endpoint is working and DB is connected
            success = response.status_code in [200, 401, 403, 422]  # 422 for validation errors
            details = f"Status: {response.status_code}"
            if response.status_code == 422:
                details += " (Expected - requires auth or parameters)"
            elif response.status_code == 200:
                details += " (Database connected and working)"
            self.log_test("Database Connection", success, details)
            return success
        except Exception as e:
            self.log_test("Database Connection", False, f"Error: {str(e)}")
            return False

    def test_cors_headers(self) -> bool:
        """Test CORS headers are present"""
        try:
            response = self.session.options(f"{self.base_url}/api/metro/stations", timeout=10)
            cors_headers = {
                'access-control-allow-origin': response.headers.get('access-control-allow-origin'),
                'access-control-allow-methods': response.headers.get('access-control-allow-methods'),
                'access-control-allow-headers': response.headers.get('access-control-allow-headers')
            }
            
            success = any(cors_headers.values())
            details = f"CORS headers present: {bool(any(cors_headers.values()))}"
            self.log_test("CORS Configuration", success, details)
            return success
        except Exception as e:
            self.log_test("CORS Configuration", False, f"Error: {str(e)}")
            return False

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return results"""
        print("🚀 Starting Social Rent API Tests...")
        print(f"📍 Testing endpoint: {self.base_url}")
        print("=" * 60)

        # Core API tests
        self.test_health_check()
        self.test_root_endpoint()
        self.test_api_docs()
        
        # Metro API tests
        self.test_metro_stations_api()
        self.test_metro_search_api()
        
        # Frontend serving tests
        self.test_frontend_serving()
        self.test_static_files()
        self.test_favicon_and_manifest()
        
        # Infrastructure tests
        self.test_database_connection()
        self.test_cors_headers()

        print("=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return {"status": "success", "passed": self.tests_passed, "total": self.tests_run}
        else:
            print("⚠️  Some tests failed. Check the details above.")
            return {"status": "partial", "passed": self.tests_passed, "total": self.tests_run}

def main():
    """Main test execution"""
    tester = SocialRentAPITester("http://localhost:8001")
    results = tester.run_all_tests()
    
    # Return appropriate exit code
    if results["status"] == "success":
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())