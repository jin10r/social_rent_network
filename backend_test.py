#!/usr/bin/env python3
"""
Comprehensive Backend API Tests for Social Rent Application
Tests all API endpoints with mock Telegram authentication
"""

import asyncio
import json
import requests
import random
from typing import Dict, List, Optional
import uuid

# Configuration - Testing through nginx reverse proxy
NGINX_URL = "http://localhost:8080"
BACKEND_URL = NGINX_URL  # Test through nginx proxy
API_BASE = f"{BACKEND_URL}/api"

# Test data - realistic Moscow users
TEST_USERS = [
    {
        "id": 123456789,
        "username": "anna_moscow",
        "first_name": "Анна",
        "last_name": "Петрова",
        "photo_url": "https://picsum.photos/200/200?random=1"
    },
    {
        "id": 987654321,
        "username": "dmitry_dev",
        "first_name": "Дмитрий",
        "last_name": "Иванов",
        "photo_url": "https://picsum.photos/200/200?random=2"
    },
    {
        "id": 555666777,
        "username": "maria_student",
        "first_name": "Мария",
        "last_name": "Сидорова",
        "photo_url": "https://picsum.photos/200/200?random=3"
    }
]

# Moscow coordinates for testing
MOSCOW_CENTER = {"lat": 55.7558, "lon": 37.6176}
MOSCOW_COORDS = [
    {"lat": 55.7558, "lon": 37.6176},  # Red Square
    {"lat": 55.7522, "lon": 37.6156},  # Kremlin
    {"lat": 55.7539, "lon": 37.6208},  # GUM
]

class SocialRentAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.created_users = []
        self.created_listings = []
        self.test_matches = []
        
    def create_auth_token(self, user_data: Dict) -> str:
        """Create mock Telegram auth token"""
        return json.dumps(user_data)
    
    def get_headers(self, user_data: Dict) -> Dict[str, str]:
        """Get headers with auth token"""
        token = self.create_auth_token(user_data)
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    def test_health_check(self):
        """Test GET /health endpoint through nginx"""
        try:
            response = self.session.get(f"{NGINX_URL}/health")
            success = response.status_code == 200 and response.json().get("status") == "healthy"
            self.log_test("Health Check (via nginx)", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Health Check (via nginx)", False, str(e))
            return False
    
    def test_nginx_routing(self):
        """Test nginx routing configuration"""
        try:
            print("\n🔀 Testing Nginx Routing...")
            
            # Test /docs endpoint (should route to backend)
            response = self.session.get(f"{NGINX_URL}/docs")
            docs_success = response.status_code == 200
            self.log_test("Nginx /docs routing", docs_success, f"Status: {response.status_code}")
            
            # Test /openapi.json endpoint (should route to backend)
            response = self.session.get(f"{NGINX_URL}/openapi.json")
            openapi_success = response.status_code == 200
            self.log_test("Nginx /openapi.json routing", openapi_success, f"Status: {response.status_code}")
            
            # Test root endpoint (should route to frontend)
            response = self.session.get(f"{NGINX_URL}/")
            root_success = response.status_code == 200
            self.log_test("Nginx root routing", root_success, f"Status: {response.status_code}")
            
            return docs_success and openapi_success and root_success
        except Exception as e:
            self.log_test("Nginx Routing", False, str(e))
            return False
    
    def test_create_user(self, user_data: Dict):
        """Test POST /api/users/ endpoint"""
        try:
            headers = self.get_headers(user_data)
            
            # Create user profile data
            profile_data = {
                "telegram_id": user_data["id"],
                "username": user_data["username"],
                "first_name": user_data["first_name"],
                "last_name": user_data["last_name"],
                "photo_url": user_data["photo_url"],
                "age": random.randint(22, 35),
                "bio": f"Привет! Меня зовут {user_data['first_name']}. Ищу жилье в Москве.",
                "price_min": random.randint(30000, 50000),
                "price_max": random.randint(60000, 100000),
                "metro_station": random.choice(["Сокольники", "Красносельская", "Комсомольская"]),
                "search_radius": random.randint(1000, 3000),
                "lat": MOSCOW_CENTER["lat"] + random.uniform(-0.1, 0.1),
                "lon": MOSCOW_CENTER["lon"] + random.uniform(-0.1, 0.1)
            }
            
            response = self.session.post(f"{API_BASE}/users/", 
                                       headers=headers, 
                                       json=profile_data)
            
            success = response.status_code == 200
            if success:
                user_response = response.json()
                self.created_users.append(user_response)
                self.log_test(f"Create User ({user_data['first_name']})", True, 
                            f"User ID: {user_response.get('id')}")
            else:
                self.log_test(f"Create User ({user_data['first_name']})", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
            
            return success
        except Exception as e:
            self.log_test(f"Create User ({user_data['first_name']})", False, str(e))
            return False
    
    def test_get_current_user(self, user_data: Dict):
        """Test GET /api/users/me endpoint"""
        try:
            headers = self.get_headers(user_data)
            response = self.session.get(f"{API_BASE}/users/me", headers=headers)
            
            success = response.status_code == 200
            if success:
                user_info = response.json()
                self.log_test(f"Get Current User ({user_data['first_name']})", True,
                            f"Username: {user_info.get('username')}")
            else:
                self.log_test(f"Get Current User ({user_data['first_name']})", False,
                            f"Status: {response.status_code}")
            
            return success
        except Exception as e:
            self.log_test(f"Get Current User ({user_data['first_name']})", False, str(e))
            return False
    
    def test_update_user_profile(self, user_data: Dict):
        """Test PUT /api/users/me endpoint"""
        try:
            headers = self.get_headers(user_data)
            
            update_data = {
                "bio": f"Обновленная биография для {user_data['first_name']}",
                "price_max": 120000,
                "search_radius": 2500
            }
            
            response = self.session.put(f"{API_BASE}/users/me", 
                                      headers=headers, 
                                      json=update_data)
            
            success = response.status_code == 200
            if success:
                updated_user = response.json()
                self.log_test(f"Update User Profile ({user_data['first_name']})", True,
                            f"Updated bio: {updated_user.get('bio', '')[:50]}...")
            else:
                self.log_test(f"Update User Profile ({user_data['first_name']})", False,
                            f"Status: {response.status_code}")
            
            return success
        except Exception as e:
            self.log_test(f"Update User Profile ({user_data['first_name']})", False, str(e))
            return False
    
    def test_get_potential_matches(self, user_data: Dict):
        """Test GET /api/users/potential-matches endpoint"""
        try:
            headers = self.get_headers(user_data)
            response = self.session.get(f"{API_BASE}/users/potential-matches?limit=5", 
                                      headers=headers)
            
            success = response.status_code == 200
            if success:
                matches = response.json()
                self.log_test(f"Get Potential Matches ({user_data['first_name']})", True,
                            f"Found {len(matches)} potential matches")
                return matches
            else:
                self.log_test(f"Get Potential Matches ({user_data['first_name']})", False,
                            f"Status: {response.status_code}")
                return []
        except Exception as e:
            self.log_test(f"Get Potential Matches ({user_data['first_name']})", False, str(e))
            return []
    
    def test_like_user(self, liker_data: Dict, liked_user_id: str):
        """Test POST /api/users/{user_id}/like endpoint"""
        try:
            headers = self.get_headers(liker_data)
            response = self.session.post(f"{API_BASE}/users/{liked_user_id}/like", 
                                       headers=headers)
            
            success = response.status_code == 200
            if success:
                result = response.json()
                is_match = result.get("match", False)
                self.log_test(f"Like User ({liker_data['first_name']})", True,
                            f"Match: {is_match}, Message: {result.get('message', '')}")
                if is_match:
                    self.test_matches.append({
                        "user1": liker_data,
                        "user2_id": liked_user_id
                    })
            else:
                self.log_test(f"Like User ({liker_data['first_name']})", False,
                            f"Status: {response.status_code}")
            
            return success
        except Exception as e:
            self.log_test(f"Like User ({liker_data['first_name']})", False, str(e))
            return False
    
    def test_get_user_matches(self, user_data: Dict):
        """Test GET /api/users/matches endpoint"""
        try:
            headers = self.get_headers(user_data)
            response = self.session.get(f"{API_BASE}/users/matches", headers=headers)
            
            success = response.status_code == 200
            if success:
                matches = response.json()
                self.log_test(f"Get User Matches ({user_data['first_name']})", True,
                            f"Found {len(matches)} matches")
                return matches
            else:
                self.log_test(f"Get User Matches ({user_data['first_name']})", False,
                            f"Status: {response.status_code}")
                return []
        except Exception as e:
            self.log_test(f"Get User Matches ({user_data['first_name']})", False, str(e))
            return []
    
    def test_get_listings(self):
        """Test GET /api/listings/ endpoint"""
        try:
            # Test without location filter
            response = self.session.get(f"{API_BASE}/listings/?limit=10")
            success = response.status_code == 200
            
            if success:
                listings = response.json()
                self.log_test("Get Listings (no filter)", True, f"Found {len(listings)} listings")
            else:
                self.log_test("Get Listings (no filter)", False, f"Status: {response.status_code}")
            
            # Test with location filter (Moscow center)
            params = {
                "lat": MOSCOW_CENTER["lat"],
                "lon": MOSCOW_CENTER["lon"],
                "radius": 2000,
                "limit": 10
            }
            response = self.session.get(f"{API_BASE}/listings/", params=params)
            success_geo = response.status_code == 200
            
            if success_geo:
                geo_listings = response.json()
                self.log_test("Get Listings (with location)", True, 
                            f"Found {len(geo_listings)} listings near center")
            else:
                self.log_test("Get Listings (with location)", False, 
                            f"Status: {response.status_code}")
            
            return success and success_geo
        except Exception as e:
            self.log_test("Get Listings", False, str(e))
            return False
    
    def test_search_listings_for_user(self, user_data: Dict):
        """Test GET /api/listings/search endpoint"""
        try:
            headers = self.get_headers(user_data)
            response = self.session.get(f"{API_BASE}/listings/search", headers=headers)
            
            success = response.status_code == 200
            if success:
                listings = response.json()
                self.log_test(f"Search Listings for User ({user_data['first_name']})", True,
                            f"Found {len(listings)} listings matching criteria")
                if listings:
                    self.created_listings.extend(listings[:3])  # Store some for testing
            else:
                self.log_test(f"Search Listings for User ({user_data['first_name']})", False,
                            f"Status: {response.status_code}")
            
            return success
        except Exception as e:
            self.log_test(f"Search Listings for User ({user_data['first_name']})", False, str(e))
            return False
    
    def test_like_listing(self, user_data: Dict, listing_id: str):
        """Test POST /api/listings/{listing_id}/like endpoint"""
        try:
            headers = self.get_headers(user_data)
            response = self.session.post(f"{API_BASE}/listings/{listing_id}/like", 
                                       headers=headers)
            
            success = response.status_code == 200
            if success:
                result = response.json()
                self.log_test(f"Like Listing ({user_data['first_name']})", True,
                            f"Liked: {result.get('liked', False)}")
            else:
                self.log_test(f"Like Listing ({user_data['first_name']})", False,
                            f"Status: {response.status_code}")
            
            return success
        except Exception as e:
            self.log_test(f"Like Listing ({user_data['first_name']})", False, str(e))
            return False
    
    def test_get_liked_listings(self, user_data: Dict):
        """Test GET /api/listings/liked endpoint"""
        try:
            headers = self.get_headers(user_data)
            response = self.session.get(f"{API_BASE}/listings/liked", headers=headers)
            
            success = response.status_code == 200
            if success:
                liked_listings = response.json()
                self.log_test(f"Get Liked Listings ({user_data['first_name']})", True,
                            f"Found {len(liked_listings)} liked listings")
            else:
                self.log_test(f"Get Liked Listings ({user_data['first_name']})", False,
                            f"Status: {response.status_code}")
            
            return success
        except Exception as e:
            self.log_test(f"Get Liked Listings ({user_data['first_name']})", False, str(e))
            return False
    
    def test_get_user_liked_listings(self, viewer_data: Dict, target_user_id: str):
        """Test GET /api/users/{user_id}/liked-listings endpoint"""
        try:
            headers = self.get_headers(viewer_data)
            response = self.session.get(f"{API_BASE}/users/{target_user_id}/liked-listings", 
                                      headers=headers)
            
            # This should work only if users are matched
            if response.status_code == 200:
                liked_listings = response.json()
                self.log_test(f"Get User Liked Listings ({viewer_data['first_name']})", True,
                            f"Found {len(liked_listings)} liked listings of matched user")
                return True
            elif response.status_code == 403:
                # Expected if users are not matched
                self.log_test(f"Get User Liked Listings ({viewer_data['first_name']})", True,
                            "Correctly blocked - users not matched")
                return True
            else:
                self.log_test(f"Get User Liked Listings ({viewer_data['first_name']})", False,
                            f"Unexpected status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test(f"Get User Liked Listings ({viewer_data['first_name']})", False, str(e))
            return False
    
    def test_geographic_functionality(self):
        """Test geographic search functionality"""
        try:
            print("\n🗺️  Testing Geographic Functionality...")
            
            # Test search with different radii
            radii = [500, 1000, 5000]  # meters
            for radius in radii:
                params = {
                    "lat": MOSCOW_CENTER["lat"],
                    "lon": MOSCOW_CENTER["lon"],
                    "radius": radius,
                    "limit": 20
                }
                response = self.session.get(f"{API_BASE}/listings/", params=params)
                
                if response.status_code == 200:
                    listings = response.json()
                    self.log_test(f"Geographic Search (radius {radius}m)", True,
                                f"Found {len(listings)} listings")
                else:
                    self.log_test(f"Geographic Search (radius {radius}m)", False,
                                f"Status: {response.status_code}")
            
            # Test price filtering
            params = {
                "lat": MOSCOW_CENTER["lat"],
                "lon": MOSCOW_CENTER["lon"],
                "radius": 2000,
                "price_min": 50000,
                "price_max": 80000,
                "limit": 10
            }
            response = self.session.get(f"{API_BASE}/listings/", params=params)
            
            success = response.status_code == 200
            if success:
                filtered_listings = response.json()
                self.log_test("Price Filtering", True,
                            f"Found {len(filtered_listings)} listings in price range")
            else:
                self.log_test("Price Filtering", False, f"Status: {response.status_code}")
            
            return True
        except Exception as e:
            self.log_test("Geographic Functionality", False, str(e))
            return False
    
    def test_matching_logic(self):
        """Test user matching logic"""
        try:
            print("\n💕 Testing Matching Logic...")
            
            if len(self.created_users) < 2:
                self.log_test("Matching Logic", False, "Not enough users created")
                return False
            
            user1 = TEST_USERS[0]
            user2 = TEST_USERS[1]
            
            # Get potential matches for user1
            matches = self.test_get_potential_matches(user1)
            
            if matches:
                # User1 likes User2 (if User2 is in potential matches)
                user2_match = None
                for match in matches:
                    if match.get('first_name') == user2['first_name']:
                        user2_match = match
                        break
                
                if user2_match:
                    # User1 likes User2
                    self.test_like_user(user1, user2_match['id'])
                    
                    # User2 likes User1 back (should create match)
                    user1_matches = self.test_get_potential_matches(user2)
                    user1_match = None
                    for match in user1_matches:
                        if match.get('first_name') == user1['first_name']:
                            user1_match = match
                            break
                    
                    if user1_match:
                        self.test_like_user(user2, user1_match['id'])
                        
                        # Check if match was created
                        user1_matches = self.test_get_user_matches(user1)
                        user2_matches = self.test_get_user_matches(user2)
                        
                        match_success = len(user1_matches) > 0 and len(user2_matches) > 0
                        self.log_test("Mutual Matching", match_success,
                                    f"User1 matches: {len(user1_matches)}, User2 matches: {len(user2_matches)}")
                        return match_success
            
            return True
        except Exception as e:
            self.log_test("Matching Logic", False, str(e))
            return False
    
    def test_data_validation(self):
        """Test data validation and error handling"""
        try:
            print("\n🔍 Testing Data Validation...")
            
            # Test invalid auth token
            invalid_headers = {"Authorization": "Bearer invalid_token"}
            response = self.session.get(f"{API_BASE}/users/me", headers=invalid_headers)
            
            auth_validation = response.status_code == 401
            self.log_test("Invalid Auth Token", auth_validation,
                        f"Status: {response.status_code}")
            
            # Test invalid user ID in like endpoint
            if self.created_users:
                headers = self.get_headers(TEST_USERS[0])
                invalid_user_id = "invalid-uuid"
                response = self.session.post(f"{API_BASE}/users/{invalid_user_id}/like", 
                                           headers=headers)
                
                uuid_validation = response.status_code in [400, 422, 404]
                self.log_test("Invalid User ID", uuid_validation,
                            f"Status: {response.status_code}")
            
            # Test invalid coordinates
            params = {
                "lat": 200,  # Invalid latitude
                "lon": 300,  # Invalid longitude
                "radius": 1000
            }
            response = self.session.get(f"{API_BASE}/listings/", params=params)
            
            coord_validation = response.status_code in [400, 422]
            self.log_test("Invalid Coordinates", coord_validation,
                        f"Status: {response.status_code}")
            
            return True
        except Exception as e:
            self.log_test("Data Validation", False, str(e))
            return False
    
    def run_comprehensive_tests(self):
        """Run all API tests"""
        print("🚀 Starting Comprehensive Social Rent API Tests\n")
        
        # 1. Health check
        print("1️⃣  Testing Health Check...")
        self.test_health_check()
        
        # 2. User management
        print("\n👤 Testing User Management...")
        for user in TEST_USERS:
            self.test_create_user(user)
            self.test_get_current_user(user)
            self.test_update_user_profile(user)
        
        # 3. Listing functionality
        print("\n🏠 Testing Listing Functionality...")
        self.test_get_listings()
        for user in TEST_USERS:
            self.test_search_listings_for_user(user)
        
        # 4. Like functionality
        print("\n❤️  Testing Like Functionality...")
        if self.created_listings:
            for i, user in enumerate(TEST_USERS):
                if i < len(self.created_listings):
                    listing = self.created_listings[i]
                    self.test_like_listing(user, listing['id'])
                    self.test_get_liked_listings(user)
        
        # 5. Matching system
        self.test_matching_logic()
        
        # 6. Geographic functionality
        self.test_geographic_functionality()
        
        # 7. Data validation
        self.test_data_validation()
        
        # 8. Cross-user functionality
        print("\n🔗 Testing Cross-User Functionality...")
        if len(self.created_users) >= 2:
            user1_id = self.created_users[0]['id']
            user2_id = self.created_users[1]['id']
            
            # Test viewing liked listings of other users
            self.test_get_user_liked_listings(TEST_USERS[0], user2_id)
            self.test_get_user_liked_listings(TEST_USERS[1], user1_id)
        
        # Print summary
        self.print_test_summary()
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['details']}")
        
        print(f"\n📈 STATISTICS:")
        print(f"   • Created Users: {len(self.created_users)}")
        print(f"   • Found Listings: {len(self.created_listings)}")
        print(f"   • Test Matches: {len(self.test_matches)}")
        
        print("\n🎯 CRITICAL ENDPOINTS STATUS:")
        critical_endpoints = [
            "Health Check",
            "Create User",
            "Get Current User", 
            "Get Listings",
            "Search Listings for User",
            "Get Potential Matches"
        ]
        
        for endpoint in critical_endpoints:
            endpoint_results = [r for r in self.test_results if endpoint in r['test']]
            if endpoint_results:
                success_count = sum(1 for r in endpoint_results if r['success'])
                total_count = len(endpoint_results)
                status = "✅" if success_count == total_count else "❌"
                print(f"   {status} {endpoint}: {success_count}/{total_count}")

def main():
    """Main test execution"""
    tester = SocialRentAPITester()
    tester.run_comprehensive_tests()

if __name__ == "__main__":
    main()