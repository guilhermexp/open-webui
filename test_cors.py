#!/usr/bin/env python3
"""Test CORS headers for static files"""

import requests

# Test URLs
backend_url = "http://localhost:8082"
frontend_origin = "http://localhost:5173"

# Test static file
static_file_url = f"{backend_url}/static/favicon.png"

# Test with Origin header (simulating browser request)
headers = {
    "Origin": frontend_origin
}

print("Testing CORS for static files...")
print(f"Request URL: {static_file_url}")
print(f"Origin: {frontend_origin}")

try:
    response = requests.get(static_file_url, headers=headers)
    print(f"\nStatus Code: {response.status_code}")
    
    # Check CORS headers
    cors_headers = {
        "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
        "Access-Control-Allow-Credentials": response.headers.get("Access-Control-Allow-Credentials"),
        "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
        "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers"),
    }
    
    print("\nCORS Headers:")
    for header, value in cors_headers.items():
        print(f"  {header}: {value}")
        
    # Check if CORS is properly configured
    if cors_headers["Access-Control-Allow-Origin"] == frontend_origin:
        print("\n✅ CORS is properly configured!")
    else:
        print("\n❌ CORS is not properly configured")
        
except requests.exceptions.RequestException as e:
    print(f"\n❌ Error: {e}")