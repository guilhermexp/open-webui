#!/usr/bin/env python3
"""
Simple test to check MCP endpoints are working
"""
import requests
import json

BASE_URL = "http://localhost:8082"

print("Testing MCP Backend Endpoints")
print("=" * 50)

# Test basic connectivity
print("\n1. Testing backend connectivity...")
try:
    response = requests.get(f"{BASE_URL}/", timeout=5)
    print(f"   Backend is responding: {response.status_code}")
except Exception as e:
    print(f"   Backend not accessible: {e}")
    exit(1)

# Test auth endpoint
print("\n2. Testing auth endpoint...")
try:
    response = requests.post(
        f"{BASE_URL}/api/auth/signin",
        json={"email": "test@example.com", "password": "test"},
        timeout=5
    )
    print(f"   Auth endpoint status: {response.status_code}")
    print(f"   Response: {response.text[:100]}...")
except Exception as e:
    print(f"   Auth endpoint error: {e}")

# Test MCP endpoints (expecting 401 without auth)
print("\n3. Testing MCP endpoints (without auth)...")
endpoints = [
    ("GET", "/api/v1/mcp/"),
    ("GET", "/api/v1/mcp/test-id"),
    ("POST", "/api/v1/mcp/test-id/test"),
    ("GET", "/api/v1/mcp/test-id/tools"),
]

for method, endpoint in endpoints:
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
        else:
            response = requests.post(f"{BASE_URL}{endpoint}", timeout=5)
        
        print(f"   {method} {endpoint}: {response.status_code}")
        if response.status_code != 401:
            print(f"      Response: {response.text[:100]}...")
    except Exception as e:
        print(f"   {method} {endpoint}: Error - {e}")

print("\n" + "=" * 50)
print("Note: 401 errors are expected without authentication")
print("The endpoints are working if they return 401 instead of 404/500")