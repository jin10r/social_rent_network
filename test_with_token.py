#!/usr/bin/env python3
"""
Test Social Rent API with provided token
"""

import requests
import json

# Configuration
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

# Provided token from the review request
AUTH_TOKEN = "eyJpZCI6MTIzNDU2Nzg5LCJmaXJzdF9uYW1lIjoiVGVzdCIsImxhc3RfbmFtZSI6IlVzZXIiLCJ1c2VybmFtZSI6InRlc3R1c2VyIn0K"

def get_headers():
    """Get headers with auth token"""
    return {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }

def test_with_provided_token():
    """Test API endpoints with the provided token"""
    print("🔑 Testing with provided authorization token...")
    
    headers = get_headers()
    
    # Test 1: Get current user
    print("\n1. Testing GET /api/users/me")
    try:
        response = requests.get(f"{API_BASE}/users/me", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ User found: {user_data.get('first_name')} {user_data.get('last_name')}")
        elif response.status_code == 404:
            print("❌ User not found - need to create profile first")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 2: Create user profile (if not exists)
    print("\n2. Testing POST /api/users/ (create profile)")
    try:
        profile_data = {
            "telegram_id": 123456789,
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "age": 25,
            "bio": "Test user for Social Rent app",
            "price_min": 30000,
            "price_max": 80000,
            "metro_station": "Сокольники",
            "search_radius": 2000,
            "lat": 55.7558,
            "lon": 37.6176
        }
        
        response = requests.post(f"{API_BASE}/users/", headers=headers, json=profile_data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Profile created/updated: {user_data.get('id')}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 3: Get potential matches
    print("\n3. Testing GET /api/users/potential-matches")
    try:
        response = requests.get(f"{API_BASE}/users/potential-matches?limit=5", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            matches = response.json()
            print(f"✅ Found {len(matches)} potential matches")
            for match in matches[:2]:  # Show first 2
                print(f"   - {match.get('first_name')} {match.get('last_name')}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 4: Get listings
    print("\n4. Testing GET /api/listings/")
    try:
        response = requests.get(f"{API_BASE}/listings/?limit=5")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            listings = response.json()
            print(f"✅ Found {len(listings)} listings")
            for listing in listings[:2]:  # Show first 2
                print(f"   - {listing.get('title')} - {listing.get('price')} руб.")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 5: Search listings for user
    print("\n5. Testing GET /api/listings/search")
    try:
        response = requests.get(f"{API_BASE}/listings/search", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            listings = response.json()
            print(f"✅ Found {len(listings)} listings matching user criteria")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 6: Test validation error (age < 18)
    print("\n6. Testing validation error (age < 18)")
    try:
        invalid_profile_data = {
            "telegram_id": 123456789,
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "age": 16,  # Invalid age < 18
            "bio": "Test user for Social Rent app",
            "price_min": 30000,
            "price_max": 80000,
            "metro_station": "Сокольники",
            "search_radius": 2000,
            "lat": 55.7558,
            "lon": 37.6176
        }
        
        response = requests.post(f"{API_BASE}/users/", headers=headers, json=invalid_profile_data)
        print(f"Status: {response.status_code}")
        if response.status_code == 422:
            print("✅ Validation error correctly returned for age < 18")
            error_data = response.json()
            print(f"   Error details: {error_data}")
        else:
            print(f"❌ Expected 422, got {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_with_provided_token()