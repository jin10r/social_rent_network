import requests
import sys
import json
from datetime import datetime

class SocialRentAPITester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.user_id = None

    def get_mock_auth_token(self):
        """Get mock auth token for testing"""
        mock_user_data = {
            "id": 123456789,
            "first_name": "Test",
            "last_name": "User", 
            "username": "testuser"
        }
        return f"Bearer {json.dumps(mock_user_data)}"

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        # Add auth token
        auth_token = self.get_mock_auth_token()
        test_headers['Authorization'] = auth_token
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        print(f"   Method: {method}")
        if data:
            print(f"   Data: {json.dumps(data, indent=2)}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers)

            print(f"   Response Status: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2, default=str)}")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test health check endpoint"""
        return self.run_test("Health Check", "GET", "health", 200)

    def test_metro_stations(self):
        """Test metro stations endpoints"""
        print("\n📍 Testing Metro Stations API...")
        
        # Test get all stations
        success1, _ = self.run_test("Get All Metro Stations", "GET", "api/metro/stations", 200)
        
        # Test search stations
        success2, _ = self.run_test("Search Metro Stations", "GET", "api/metro/search?query=Маяковская", 200)
        
        return success1 and success2

    def test_user_profile_flow(self):
        """Test complete user profile flow"""
        print("\n👤 Testing User Profile Flow...")
        
        # Test get current user (should fail initially)
        print("\n1. Testing get current user (should fail initially)...")
        success1, _ = self.run_test("Get Current User (Initial)", "GET", "api/users/me", 404)
        
        # Test create/update user profile
        print("\n2. Testing create user profile...")
        user_data = {
            "telegram_id": 123456789,
            "first_name": "Test",
            "last_name": "User",
            "age": 25,
            "bio": "Test user bio",
            "price_min": 30000,
            "price_max": 50000,
            "metro_station": "Маяковская",
            "search_radius": 2000
        }
        
        success2, response_data = self.run_test("Create User Profile", "POST", "api/users/", 200, user_data)
        if success2 and response_data:
            self.user_id = response_data.get('id')
            print(f"   Created user with ID: {self.user_id}")
        
        # Test get current user (should succeed now)
        print("\n3. Testing get current user (should succeed now)...")
        success3, _ = self.run_test("Get Current User (After Creation)", "GET", "api/users/me", 200)
        
        # Test update user profile
        print("\n4. Testing update user profile...")
        update_data = {
            "first_name": "Updated Test",
            "age": 26,
            "bio": "Updated bio",
            "price_min": 35000,
            "price_max": 55000,
            "metro_station": "Пушкинская",
            "search_radius": 3000
        }
        
        success4, _ = self.run_test("Update User Profile", "PUT", "api/users/profile", 200, update_data)
        
        # Test get current user again to verify update
        print("\n5. Testing get current user (verify update)...")
        success5, updated_user = self.run_test("Get Current User (Verify Update)", "GET", "api/users/me", 200)
        
        if success5 and updated_user:
            print(f"   Verifying updated data...")
            if updated_user.get('first_name') == 'Updated Test':
                print(f"   ✅ First name updated correctly")
            else:
                print(f"   ❌ First name not updated correctly")
            
            if updated_user.get('age') == 26:
                print(f"   ✅ Age updated correctly")
            else:
                print(f"   ❌ Age not updated correctly")
                
            if updated_user.get('metro_station') == 'Пушкинская':
                print(f"   ✅ Metro station updated correctly")
            else:
                print(f"   ❌ Metro station not updated correctly")
        
        return success2 and success3 and success4 and success5

    def test_listings_api(self):
        """Test listings API"""
        print("\n🏠 Testing Listings API...")
        
        # Test get listings
        success1, _ = self.run_test("Get Listings", "GET", "api/listings/", 200)
        
        # Test search listings for user (requires user to be created first)
        if self.user_id:
            success2, _ = self.run_test("Search Listings for User", "GET", "api/listings/search", 200)
        else:
            print("   ⚠️ Skipping user-specific listings test (no user created)")
            success2 = True
        
        return success1 and success2

def main():
    print("🚀 Starting Social Rent API Tests...")
    print("=" * 50)
    
    # Setup
    tester = SocialRentAPITester("http://localhost:8001")
    
    # Run tests
    health_ok = tester.test_health_check()
    metro_ok = tester.test_metro_stations()
    profile_ok = tester.test_user_profile_flow()
    listings_ok = tester.test_listings_api()
    
    # Print results
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    print(f"Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Metro Stations: {'✅ PASS' if metro_ok else '❌ FAIL'}")
    print(f"User Profile Flow: {'✅ PASS' if profile_ok else '❌ FAIL'}")
    print(f"Listings API: {'✅ PASS' if listings_ok else '❌ FAIL'}")
    print(f"\nOverall: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())