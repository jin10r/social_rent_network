#!/usr/bin/env python3
"""
Nginx Reverse Proxy Configuration Test for Social Rent App
Tests nginx configuration, docker-compose setup, and environment variables
"""

import os
import json
import re
from pathlib import Path

class NginxConfigTester:
    def __init__(self):
        self.test_results = []
        self.app_root = Path("/app")
        
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
    
    def test_file_exists(self, file_path: Path, description: str):
        """Test if a file exists"""
        exists = file_path.exists()
        self.log_test(f"File exists: {description}", exists, str(file_path))
        return exists
    
    def test_nginx_config(self):
        """Test nginx.conf configuration"""
        print("\n🔧 Testing Nginx Configuration...")
        
        nginx_conf = self.app_root / "nginx.conf"
        if not self.test_file_exists(nginx_conf, "nginx.conf"):
            return False
        
        try:
            content = nginx_conf.read_text()
            
            # Test API routing
            api_routing = "/api/" in content and "backend:8001" in content
            self.log_test("Nginx API routing (/api/ -> backend:8001)", api_routing,
                         "Found /api/ routing to backend:8001" if api_routing else "Missing API routing")
            
            # Test health endpoint routing
            health_routing = ("health" in content and "backend:8001" in content) or \
                           ("/(health|" in content and "backend:8001" in content)
            self.log_test("Nginx health routing (/health -> backend:8001)", health_routing,
                         "Found /health routing to backend:8001" if health_routing else "Missing health routing")
            
            # Test docs routing
            docs_routing = ("docs" in content and "backend:8001" in content) or \
                          ("/(health|docs|" in content and "backend:8001" in content)
            self.log_test("Nginx docs routing (/docs -> backend:8001)", docs_routing,
                         "Found /docs routing to backend:8001" if docs_routing else "Missing docs routing")
            
            # Test frontend routing
            frontend_routing = "frontend:3000" in content
            self.log_test("Nginx frontend routing (/ -> frontend:3000)", frontend_routing,
                         "Found frontend routing to frontend:3000" if frontend_routing else "Missing frontend routing")
            
            # Test port configuration
            port_80 = "listen 80" in content
            self.log_test("Nginx listening on port 80", port_80,
                         "Nginx configured to listen on port 80" if port_80 else "Nginx not listening on port 80")
            
            return api_routing and health_routing and docs_routing and frontend_routing and port_80
            
        except Exception as e:
            self.log_test("Nginx config parsing", False, str(e))
            return False
    
    def test_docker_compose_config(self):
        """Test docker-compose.yml configuration"""
        print("\n🐳 Testing Docker Compose Configuration...")
        
        compose_file = self.app_root / "docker-compose.yml"
        if not self.test_file_exists(compose_file, "docker-compose.yml"):
            return False
        
        try:
            content = compose_file.read_text()
            
            # Test nginx service
            nginx_service = "nginx:" in content and "image: nginx:alpine" in content
            self.log_test("Docker Compose nginx service", nginx_service,
                         "Found nginx service with alpine image" if nginx_service else "Missing nginx service")
            
            # Test nginx port mapping
            nginx_port = "${NGINX_PORT:-8080}:80" in content
            self.log_test("Docker Compose nginx port mapping", nginx_port,
                         "Found nginx port mapping 8080:80" if nginx_port else "Missing nginx port mapping")
            
            # Test backend service
            backend_service = "backend:" in content and "context: ./backend" in content
            self.log_test("Docker Compose backend service", backend_service,
                         "Found backend service" if backend_service else "Missing backend service")
            
            # Test frontend service
            frontend_service = "frontend:" in content and "context: ./frontend" in content
            self.log_test("Docker Compose frontend service", frontend_service,
                         "Found frontend service" if frontend_service else "Missing frontend service")
            
            # Test database service
            db_service = "db:" in content and "postgis/postgis" in content
            self.log_test("Docker Compose database service", db_service,
                         "Found PostgreSQL/PostGIS database service" if db_service else "Missing database service")
            
            # Test bot service
            bot_service = "bot:" in content and "context: ./bot" in content
            self.log_test("Docker Compose bot service", bot_service,
                         "Found Telegram bot service" if bot_service else "Missing bot service")
            
            # Test network configuration
            network_config = "social_rent_network" in content
            self.log_test("Docker Compose network configuration", network_config,
                         "Found social_rent_network configuration" if network_config else "Missing network configuration")
            
            return nginx_service and nginx_port and backend_service and frontend_service and db_service
            
        except Exception as e:
            self.log_test("Docker Compose config parsing", False, str(e))
            return False
    
    def test_environment_config(self):
        """Test .env configuration"""
        print("\n🔧 Testing Environment Configuration...")
        
        env_file = self.app_root / ".env"
        if not self.test_file_exists(env_file, ".env"):
            return False
        
        try:
            content = env_file.read_text()
            
            # Test nginx port
            nginx_port = "NGINX_PORT=8080" in content
            self.log_test("Environment NGINX_PORT", nginx_port,
                         "Found NGINX_PORT=8080" if nginx_port else "Missing or incorrect NGINX_PORT")
            
            # Test backend URL
            backend_url = "REACT_APP_BACKEND_URL=http://localhost:8080" in content
            self.log_test("Environment REACT_APP_BACKEND_URL", backend_url,
                         "Found REACT_APP_BACKEND_URL pointing to nginx" if backend_url else "Missing or incorrect REACT_APP_BACKEND_URL")
            
            # Test webapp URL
            webapp_url = "WEBAPP_URL=" in content
            self.log_test("Environment WEBAPP_URL", webapp_url,
                         "Found WEBAPP_URL configuration" if webapp_url else "Missing WEBAPP_URL")
            
            # Test database configuration
            db_config = "POSTGRES_DB=" in content and "POSTGRES_USER=" in content and "POSTGRES_PASSWORD=" in content
            self.log_test("Environment database configuration", db_config,
                         "Found complete database configuration" if db_config else "Missing database configuration")
            
            # Test CORS configuration
            cors_config = "ALLOWED_ORIGINS=" in content and "localhost:8080" in content
            self.log_test("Environment CORS configuration", cors_config,
                         "Found CORS configuration with nginx port" if cors_config else "Missing or incorrect CORS configuration")
            
            return nginx_port and backend_url and webapp_url and db_config and cors_config
            
        except Exception as e:
            self.log_test("Environment config parsing", False, str(e))
            return False
    
    def test_backend_config(self):
        """Test backend configuration"""
        print("\n⚙️  Testing Backend Configuration...")
        
        main_py = self.app_root / "backend" / "main.py"
        if not self.test_file_exists(main_py, "backend/main.py"):
            return False
        
        try:
            content = main_py.read_text()
            
            # Test FastAPI app
            fastapi_app = "app = FastAPI(" in content
            self.log_test("Backend FastAPI app", fastapi_app,
                         "Found FastAPI app initialization" if fastapi_app else "Missing FastAPI app")
            
            # Test CORS middleware
            cors_middleware = "CORSMiddleware" in content
            self.log_test("Backend CORS middleware", cors_middleware,
                         "Found CORS middleware configuration" if cors_middleware else "Missing CORS middleware")
            
            # Test API endpoints
            api_endpoints = "/api/" in content
            self.log_test("Backend API endpoints", api_endpoints,
                         "Found API endpoints with /api/ prefix" if api_endpoints else "Missing API endpoints")
            
            # Test health endpoint
            health_endpoint = "/health" in content
            self.log_test("Backend health endpoint", health_endpoint,
                         "Found /health endpoint" if health_endpoint else "Missing /health endpoint")
            
            # Test database integration
            db_integration = "AsyncSession" in content and "get_database" in content
            self.log_test("Backend database integration", db_integration,
                         "Found async database integration" if db_integration else "Missing database integration")
            
            return fastapi_app and cors_middleware and api_endpoints and health_endpoint and db_integration
            
        except Exception as e:
            self.log_test("Backend config parsing", False, str(e))
            return False
    
    def test_frontend_config(self):
        """Test frontend configuration"""
        print("\n🎨 Testing Frontend Configuration...")
        
        # Test package.json
        package_json = self.app_root / "frontend" / "package.json"
        if not self.test_file_exists(package_json, "frontend/package.json"):
            return False
        
        try:
            with open(package_json) as f:
                package_data = json.load(f)
            
            # Test React dependencies
            react_deps = "react" in package_data.get("dependencies", {})
            self.log_test("Frontend React dependency", react_deps,
                         "Found React in dependencies" if react_deps else "Missing React dependency")
            
            # Test router dependency
            router_deps = "react-router-dom" in package_data.get("dependencies", {})
            self.log_test("Frontend React Router dependency", router_deps,
                         "Found React Router in dependencies" if router_deps else "Missing React Router dependency")
            
            # Test axios dependency
            axios_deps = "axios" in package_data.get("dependencies", {})
            self.log_test("Frontend Axios dependency", axios_deps,
                         "Found Axios in dependencies" if axios_deps else "Missing Axios dependency")
            
        except Exception as e:
            self.log_test("Frontend package.json parsing", False, str(e))
            return False
        
        # Test API service
        api_service = self.app_root / "frontend" / "src" / "services" / "api.js"
        if not self.test_file_exists(api_service, "frontend/src/services/api.js"):
            return False
        
        try:
            content = api_service.read_text()
            
            # Test backend URL configuration
            backend_url_config = "REACT_APP_BACKEND_URL" in content
            self.log_test("Frontend backend URL configuration", backend_url_config,
                         "Found REACT_APP_BACKEND_URL usage" if backend_url_config else "Missing backend URL configuration")
            
            # Test API endpoints
            api_endpoints = "/api/" in content
            self.log_test("Frontend API endpoints", api_endpoints,
                         "Found /api/ endpoints" if api_endpoints else "Missing API endpoints")
            
            # Test auth integration
            auth_integration = "Authorization" in content and "Bearer" in content
            self.log_test("Frontend auth integration", auth_integration,
                         "Found Bearer token authentication" if auth_integration else "Missing auth integration")
            
            return react_deps and router_deps and axios_deps and backend_url_config and api_endpoints and auth_integration
            
        except Exception as e:
            self.log_test("Frontend API service parsing", False, str(e))
            return False
    
    def test_project_structure(self):
        """Test overall project structure"""
        print("\n📁 Testing Project Structure...")
        
        required_dirs = [
            "backend",
            "frontend", 
            "bot",
            "scripts"
        ]
        
        structure_valid = True
        for dir_name in required_dirs:
            dir_path = self.app_root / dir_name
            exists = dir_path.exists() and dir_path.is_dir()
            self.log_test(f"Directory exists: {dir_name}", exists, str(dir_path))
            if not exists:
                structure_valid = False
        
        # Test key files
        key_files = [
            "docker-compose.yml",
            "nginx.conf",
            ".env",
            "backend/main.py",
            "backend/requirements.txt",
            "frontend/package.json",
            "frontend/src/App.js",
            "bot/main.py"
        ]
        
        for file_path in key_files:
            full_path = self.app_root / file_path
            exists = full_path.exists() and full_path.is_file()
            self.log_test(f"File exists: {file_path}", exists, str(full_path))
            if not exists:
                structure_valid = False
        
        return structure_valid
    
    def run_comprehensive_tests(self):
        """Run all configuration tests"""
        print("🚀 Starting Nginx Reverse Proxy Configuration Tests\n")
        
        # Test project structure
        structure_ok = self.test_project_structure()
        
        # Test nginx configuration
        nginx_ok = self.test_nginx_config()
        
        # Test docker-compose configuration
        compose_ok = self.test_docker_compose_config()
        
        # Test environment configuration
        env_ok = self.test_environment_config()
        
        # Test backend configuration
        backend_ok = self.test_backend_config()
        
        # Test frontend configuration
        frontend_ok = self.test_frontend_config()
        
        # Print summary
        self.print_test_summary()
        
        return all([structure_ok, nginx_ok, compose_ok, env_ok, backend_ok, frontend_ok])
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*60)
        print("📊 NGINX CONFIGURATION TEST SUMMARY")
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
        
        print(f"\n🎯 CONFIGURATION STATUS:")
        categories = {
            "Project Structure": ["Directory exists", "File exists"],
            "Nginx Configuration": ["Nginx"],
            "Docker Compose": ["Docker Compose"],
            "Environment": ["Environment"],
            "Backend": ["Backend"],
            "Frontend": ["Frontend"]
        }
        
        for category, keywords in categories.items():
            category_results = [r for r in self.test_results 
                              if any(keyword in r['test'] for keyword in keywords)]
            if category_results:
                success_count = sum(1 for r in category_results if r['success'])
                total_count = len(category_results)
                status = "✅" if success_count == total_count else "❌"
                print(f"   {status} {category}: {success_count}/{total_count}")

def main():
    """Main test execution"""
    tester = NginxConfigTester()
    success = tester.run_comprehensive_tests()
    
    if success:
        print("\n🎉 All nginx reverse proxy configurations are correct!")
        print("💡 The application should work properly when services are running.")
    else:
        print("\n⚠️  Some configuration issues found.")
        print("🔧 Please fix the issues above before deploying.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())