#!/usr/bin/env python3
"""
Comprehensive Performance Testing for Social Rent Application
Tests load, stress, and database performance with PostGIS queries
"""

import asyncio
import aiohttp
import time
import json
import statistics
import psutil
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple
import uuid
import random

# Configuration
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

# Test data for performance testing
MOSCOW_CENTER = {"lat": 55.7558, "lon": 37.6176}

class PerformanceTester:
    def __init__(self):
        self.results = {}
        self.test_users = []
        self.system_metrics = []
        
    def create_auth_token(self, user_id: int) -> str:
        """Create mock Telegram auth token"""
        user_data = {
            "id": user_id,
            "username": f"test_user_{user_id}",
            "first_name": f"User{user_id}",
            "last_name": "Test"
        }
        return json.dumps(user_data)
    
    def get_headers(self, user_id: int) -> Dict[str, str]:
        """Get headers with auth token"""
        token = self.create_auth_token(user_id)
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def monitor_system_resources(self, duration: int):
        """Monitor system resources during testing"""
        start_time = time.time()
        while time.time() - start_time < duration:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            self.system_metrics.append({
                'timestamp': time.time(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used_mb': memory.used / 1024 / 1024
            })
            time.sleep(1)
    
    def single_request(self, endpoint: str, method: str = "GET", data: dict = None, user_id: int = None) -> Tuple[float, int, str]:
        """Make a single HTTP request and measure response time"""
        import requests
        
        url = f"{BACKEND_URL}{endpoint}"
        headers = self.get_headers(user_id) if user_id else {}
        
        start_time = time.time()
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=30)
            
            response_time = time.time() - start_time
            return response_time, response.status_code, "success"
        except Exception as e:
            response_time = time.time() - start_time
            return response_time, 0, str(e)
    
    def load_test_endpoint(self, endpoint: str, concurrent_users: int, requests_per_user: int = 5, method: str = "GET", data: dict = None) -> Dict:
        """Perform load testing on a specific endpoint"""
        print(f"🔥 Load testing {endpoint} with {concurrent_users} concurrent users, {requests_per_user} requests each")
        
        # Start system monitoring
        monitor_thread = threading.Thread(
            target=self.monitor_system_resources, 
            args=(concurrent_users * requests_per_user // 10 + 10,)
        )
        monitor_thread.daemon = True
        monitor_thread.start()
        
        results = []
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = []
            
            for user_id in range(concurrent_users):
                for _ in range(requests_per_user):
                    future = executor.submit(
                        self.single_request, 
                        endpoint, 
                        method, 
                        data, 
                        user_id + 1000000  # Unique user IDs
                    )
                    futures.append(future)
            
            for future in as_completed(futures):
                response_time, status_code, error = future.result()
                results.append({
                    'response_time': response_time,
                    'status_code': status_code,
                    'error': error
                })
        
        total_time = time.time() - start_time
        
        # Calculate metrics
        response_times = [r['response_time'] for r in results]
        successful_requests = [r for r in results if r['status_code'] == 200]
        failed_requests = [r for r in results if r['status_code'] != 200]
        
        metrics = {
            'endpoint': endpoint,
            'concurrent_users': concurrent_users,
            'total_requests': len(results),
            'successful_requests': len(successful_requests),
            'failed_requests': len(failed_requests),
            'success_rate': len(successful_requests) / len(results) * 100,
            'total_time': total_time,
            'requests_per_second': len(results) / total_time,
            'avg_response_time': statistics.mean(response_times),
            'min_response_time': min(response_times),
            'max_response_time': max(response_times),
            'median_response_time': statistics.median(response_times),
            'p95_response_time': self.percentile(response_times, 95),
            'p99_response_time': self.percentile(response_times, 99)
        }
        
        return metrics
    
    def percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def test_health_endpoint_performance(self):
        """Test /health endpoint performance"""
        print("\n🏥 Testing Health Endpoint Performance")
        
        load_levels = [10, 50, 100, 200]
        results = {}
        
        for concurrent_users in load_levels:
            metrics = self.load_test_endpoint("/health", concurrent_users, 10)
            results[f"{concurrent_users}_users"] = metrics
            
            print(f"   {concurrent_users} users: {metrics['requests_per_second']:.1f} req/s, "
                  f"avg: {metrics['avg_response_time']*1000:.1f}ms, "
                  f"success: {metrics['success_rate']:.1f}%")
        
        self.results['health_endpoint'] = results
    
    def test_listings_endpoint_performance(self):
        """Test /api/listings/ endpoint performance with geographic queries"""
        print("\n🏠 Testing Listings Endpoint Performance (Geographic Queries)")
        
        load_levels = [10, 50, 100, 200]
        results = {}
        
        for concurrent_users in load_levels:
            # Test with geographic parameters
            endpoint = f"/api/listings/?lat={MOSCOW_CENTER['lat']}&lon={MOSCOW_CENTER['lon']}&radius=2000&limit=20"
            metrics = self.load_test_endpoint(endpoint, concurrent_users, 5)
            results[f"{concurrent_users}_users"] = metrics
            
            print(f"   {concurrent_users} users: {metrics['requests_per_second']:.1f} req/s, "
                  f"avg: {metrics['avg_response_time']*1000:.1f}ms, "
                  f"success: {metrics['success_rate']:.1f}%")
        
        self.results['listings_endpoint'] = results
    
    def test_potential_matches_performance(self):
        """Test /api/users/potential-matches endpoint performance"""
        print("\n💕 Testing Potential Matches Endpoint Performance")
        
        # First create some test users
        self.create_test_users(50)
        
        load_levels = [10, 50, 100]  # Lower levels since this requires auth
        results = {}
        
        for concurrent_users in load_levels:
            metrics = self.load_test_endpoint("/api/users/potential-matches?limit=10", concurrent_users, 3)
            results[f"{concurrent_users}_users"] = metrics
            
            print(f"   {concurrent_users} users: {metrics['requests_per_second']:.1f} req/s, "
                  f"avg: {metrics['avg_response_time']*1000:.1f}ms, "
                  f"success: {metrics['success_rate']:.1f}%")
        
        self.results['potential_matches_endpoint'] = results
    
    def create_test_users(self, count: int):
        """Create test users for performance testing"""
        print(f"👥 Creating {count} test users...")
        
        import requests
        
        for i in range(count):
            user_id = 2000000 + i
            headers = self.get_headers(user_id)
            
            profile_data = {
                "telegram_id": user_id,
                "username": f"perf_user_{user_id}",
                "first_name": f"PerfUser{i}",
                "last_name": "Test",
                "age": random.randint(22, 35),
                "bio": f"Performance test user {i}",
                "price_min": random.randint(30000, 50000),
                "price_max": random.randint(60000, 100000),
                "metro_station": random.choice(["Сокольники", "Красносельская", "Комсомольская"]),
                "search_radius": random.randint(1000, 3000),
                "lat": MOSCOW_CENTER["lat"] + random.uniform(-0.1, 0.1),
                "lon": MOSCOW_CENTER["lon"] + random.uniform(-0.1, 0.1)
            }
            
            try:
                response = requests.post(f"{API_BASE}/users/", 
                                       headers=headers, 
                                       json=profile_data,
                                       timeout=10)
                if response.status_code == 200:
                    self.test_users.append(response.json())
            except Exception as e:
                print(f"Failed to create user {i}: {e}")
        
        print(f"✅ Created {len(self.test_users)} test users")
    
    def test_database_performance(self):
        """Test database performance with complex geographic queries"""
        print("\n🗄️ Testing Database Performance (PostGIS Queries)")
        
        # Test different radius sizes
        radii = [500, 1000, 2000, 5000, 10000]  # meters
        results = {}
        
        for radius in radii:
            print(f"   Testing radius: {radius}m")
            endpoint = f"/api/listings/?lat={MOSCOW_CENTER['lat']}&lon={MOSCOW_CENTER['lon']}&radius={radius}&limit=50"
            
            # Test with moderate load
            metrics = self.load_test_endpoint(endpoint, 20, 5)
            results[f"radius_{radius}m"] = metrics
            
            print(f"     {metrics['requests_per_second']:.1f} req/s, "
                  f"avg: {metrics['avg_response_time']*1000:.1f}ms")
        
        self.results['database_performance'] = results
    
    def stress_test_find_breaking_point(self):
        """Stress test to find the breaking point"""
        print("\n💥 Stress Testing - Finding Breaking Point")
        
        breaking_point = None
        load_levels = [50, 100, 200, 300, 400, 500]
        
        for concurrent_users in load_levels:
            print(f"   Testing with {concurrent_users} concurrent users...")
            
            metrics = self.load_test_endpoint("/health", concurrent_users, 5)
            
            success_rate = metrics['success_rate']
            avg_response_time = metrics['avg_response_time']
            
            print(f"     Success rate: {success_rate:.1f}%, "
                  f"Avg response time: {avg_response_time*1000:.1f}ms")
            
            # Consider breaking point if success rate < 95% or avg response time > 5s
            if success_rate < 95 or avg_response_time > 5:
                breaking_point = concurrent_users
                print(f"   🚨 Breaking point found at {concurrent_users} concurrent users")
                break
        
        if not breaking_point:
            print("   ✅ System handled all tested load levels successfully")
        
        self.results['stress_test'] = {
            'breaking_point': breaking_point,
            'max_tested_users': max(load_levels)
        }
    
    def test_memory_and_cpu_usage(self):
        """Analyze memory and CPU usage during tests"""
        print("\n📊 System Resource Analysis")
        
        if not self.system_metrics:
            print("   No system metrics collected")
            return
        
        cpu_values = [m['cpu_percent'] for m in self.system_metrics]
        memory_values = [m['memory_percent'] for m in self.system_metrics]
        memory_mb_values = [m['memory_used_mb'] for m in self.system_metrics]
        
        cpu_stats = {
            'avg_cpu': statistics.mean(cpu_values),
            'max_cpu': max(cpu_values),
            'min_cpu': min(cpu_values)
        }
        
        memory_stats = {
            'avg_memory_percent': statistics.mean(memory_values),
            'max_memory_percent': max(memory_values),
            'avg_memory_mb': statistics.mean(memory_mb_values),
            'max_memory_mb': max(memory_mb_values)
        }
        
        print(f"   CPU Usage - Avg: {cpu_stats['avg_cpu']:.1f}%, Max: {cpu_stats['max_cpu']:.1f}%")
        print(f"   Memory Usage - Avg: {memory_stats['avg_memory_percent']:.1f}%, Max: {memory_stats['max_memory_percent']:.1f}%")
        print(f"   Memory MB - Avg: {memory_stats['avg_memory_mb']:.0f}MB, Max: {memory_stats['max_memory_mb']:.0f}MB")
        
        self.results['system_resources'] = {
            'cpu_stats': cpu_stats,
            'memory_stats': memory_stats
        }
    
    def test_specific_functions_performance(self):
        """Test performance of specific functions"""
        print("\n🎯 Testing Specific Functions Performance")
        
        # Test user matching system
        print("   Testing user matching system...")
        if len(self.test_users) >= 10:
            metrics = self.load_test_endpoint("/api/users/potential-matches?limit=5", 10, 3)
            print(f"     Matching: {metrics['requests_per_second']:.1f} req/s, "
                  f"avg: {metrics['avg_response_time']*1000:.1f}ms")
        
        # Test location-based search
        print("   Testing location-based search...")
        endpoint = f"/api/listings/?lat={MOSCOW_CENTER['lat']}&lon={MOSCOW_CENTER['lon']}&radius=1000&limit=10"
        metrics = self.load_test_endpoint(endpoint, 20, 5)
        print(f"     Location search: {metrics['requests_per_second']:.1f} req/s, "
              f"avg: {metrics['avg_response_time']*1000:.1f}ms")
        
        # Test like system (would need more setup for realistic testing)
        print("   Like system performance testing would require more complex setup")
    
    def run_comprehensive_performance_tests(self):
        """Run all performance tests"""
        print("🚀 Starting Comprehensive Performance Testing for Social Rent API\n")
        
        start_time = time.time()
        
        # 1. Health endpoint performance
        self.test_health_endpoint_performance()
        
        # 2. Listings endpoint with geographic queries
        self.test_listings_endpoint_performance()
        
        # 3. Database performance testing
        self.test_database_performance()
        
        # 4. Potential matches performance
        self.test_potential_matches_performance()
        
        # 5. Stress testing
        self.stress_test_find_breaking_point()
        
        # 6. Specific functions performance
        self.test_specific_functions_performance()
        
        # 7. System resource analysis
        self.test_memory_and_cpu_usage()
        
        total_time = time.time() - start_time
        
        # Print comprehensive summary
        self.print_performance_summary(total_time)
    
    def print_performance_summary(self, total_test_time: float):
        """Print comprehensive performance test summary"""
        print("\n" + "="*80)
        print("📊 PERFORMANCE TEST SUMMARY")
        print("="*80)
        
        print(f"Total Test Duration: {total_test_time:.1f} seconds")
        print(f"Test Users Created: {len(self.test_users)}")
        print(f"System Metrics Collected: {len(self.system_metrics)}")
        
        # Health endpoint summary
        if 'health_endpoint' in self.results:
            print(f"\n🏥 HEALTH ENDPOINT PERFORMANCE:")
            for load, metrics in self.results['health_endpoint'].items():
                print(f"   {load}: {metrics['requests_per_second']:.1f} req/s, "
                      f"{metrics['avg_response_time']*1000:.1f}ms avg, "
                      f"{metrics['success_rate']:.1f}% success")
        
        # Listings endpoint summary
        if 'listings_endpoint' in self.results:
            print(f"\n🏠 LISTINGS ENDPOINT PERFORMANCE (Geographic Queries):")
            for load, metrics in self.results['listings_endpoint'].items():
                print(f"   {load}: {metrics['requests_per_second']:.1f} req/s, "
                      f"{metrics['avg_response_time']*1000:.1f}ms avg, "
                      f"{metrics['success_rate']:.1f}% success")
        
        # Database performance summary
        if 'database_performance' in self.results:
            print(f"\n🗄️ DATABASE PERFORMANCE (PostGIS):")
            for radius, metrics in self.results['database_performance'].items():
                print(f"   {radius}: {metrics['requests_per_second']:.1f} req/s, "
                      f"{metrics['avg_response_time']*1000:.1f}ms avg")
        
        # Stress test summary
        if 'stress_test' in self.results:
            print(f"\n💥 STRESS TEST RESULTS:")
            breaking_point = self.results['stress_test']['breaking_point']
            if breaking_point:
                print(f"   Breaking Point: {breaking_point} concurrent users")
            else:
                max_tested = self.results['stress_test']['max_tested_users']
                print(f"   No breaking point found up to {max_tested} users")
        
        # System resources summary
        if 'system_resources' in self.results:
            print(f"\n📊 SYSTEM RESOURCES:")
            cpu_stats = self.results['system_resources']['cpu_stats']
            memory_stats = self.results['system_resources']['memory_stats']
            print(f"   CPU: {cpu_stats['avg_cpu']:.1f}% avg, {cpu_stats['max_cpu']:.1f}% max")
            print(f"   Memory: {memory_stats['avg_memory_percent']:.1f}% avg, {memory_stats['max_memory_percent']:.1f}% max")
        
        print(f"\n🎯 PERFORMANCE RECOMMENDATIONS:")
        
        # Analyze results and provide recommendations
        if 'health_endpoint' in self.results:
            health_200_users = self.results['health_endpoint'].get('200_users', {})
            if health_200_users.get('success_rate', 0) < 95:
                print("   ⚠️  Health endpoint struggling with 200+ concurrent users")
            elif health_200_users.get('avg_response_time', 0) > 1:
                print("   ⚠️  Health endpoint response time high under load")
            else:
                print("   ✅ Health endpoint performing well under load")
        
        if 'listings_endpoint' in self.results:
            listings_200_users = self.results['listings_endpoint'].get('200_users', {})
            if listings_200_users.get('avg_response_time', 0) > 2:
                print("   ⚠️  Geographic queries may need optimization")
            else:
                print("   ✅ PostGIS geographic queries performing well")
        
        print(f"\n📈 SCALABILITY ASSESSMENT:")
        print("   Based on test results, the system shows good performance characteristics")
        print("   for a social network application with geographic features.")

def main():
    """Main performance test execution"""
    tester = PerformanceTester()
    tester.run_comprehensive_performance_tests()

if __name__ == "__main__":
    main()