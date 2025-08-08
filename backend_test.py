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

    def test_profile_flow_secure(self):
        """Test the specific profile flow requested in review"""
        print("\n👤 Testing Secure Profile Flow (Review Request)...")
        
        # Test 1: GET /api/users/me/secure -> expect 200 and JSON with id, telegram_id
        print("\n1. Testing GET /api/users/me/secure...")
        success1, user_data = self.run_test("Get Current User Secure", "GET", "api/users/me/secure", 200)
        
        if success1 and user_data:
            # Verify required fields
            has_id = 'id' in user_data
            has_telegram_id = 'telegram_id' in user_data
            print(f"   ✅ Has 'id' field: {has_id}")
            print(f"   ✅ Has 'telegram_id' field: {has_telegram_id}")
            if not (has_id and has_telegram_id):
                print(f"   ❌ Missing required fields in response")
                success1 = False
        
        # Test 2: PUT /api/users/profile/secure with specific data
        print("\n2. Testing PUT /api/users/profile/secure...")
        profile_data = {
            "first_name": "Тест",
            "last_name": "Пользователь", 
            "age": 25,
            "bio": "bio",
            "price_min": 30000,
            "price_max": 60000,
            "metro_station": "Сокольники",
            "search_radius": 1500
        }
        
        success2, updated_data = self.run_test("Update Profile Secure", "PUT", "api/users/profile/secure", 200, profile_data)
        
        if success2 and updated_data:
            # Verify fields were updated
            fields_correct = True
            for field, expected_value in profile_data.items():
                actual_value = updated_data.get(field)
                if actual_value == expected_value:
                    print(f"   ✅ {field}: {actual_value}")
                else:
                    print(f"   ❌ {field}: expected {expected_value}, got {actual_value}")
                    fields_correct = False
            success2 = fields_correct
        
        # Test 3: GET /api/metro/stations -> expect 200 and array including "Сокольники"
        print("\n3. Testing GET /api/metro/stations...")
        success3, stations_data = self.run_test("Get Metro Stations", "GET", "api/metro/stations", 200)
        
        if success3 and stations_data:
            if isinstance(stations_data, list):
                has_sokolniki = "Сокольники" in stations_data
                print(f"   ✅ Response is array: True")
                print(f"   ✅ Contains 'Сокольники': {has_sokolniki}")
                if not has_sokolniki:
                    print(f"   ❌ 'Сокольники' not found in stations list")
                    success3 = False
            else:
                print(f"   ❌ Response is not an array")
                success3 = False
        
        return success1 and success2 and success3

def main():
    print("🚀 Starting Social Rent API Tests (Profile Flow Focus)...")
    print("=" * 50)
    
    # Setup
    tester = SocialRentAPITester("http://localhost:8001")
    
    # Run focused profile flow test as requested in review
    profile_secure_ok = tester.test_profile_flow_secure()
    
    # Also run basic health and metro tests for completeness
    health_ok = tester.test_health_check()
    
    # Print results
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS (Profile Flow Focus)")
    print("=" * 50)
    print(f"Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Profile Flow Secure: {'✅ PASS' if profile_secure_ok else '❌ FAIL'}")
    print(f"\nOverall: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if profile_secure_ok:
        print("🎉 Profile flow tests passed!")
        return 0
    else:
        print("❌ Profile flow tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())