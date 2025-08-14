#!/usr/bin/env python3
"""
Test script for Instagram URL extraction endpoint
"""
import requests
import json

# Configure these variables
API_BASE_URL = "http://localhost:8082/api/v1/retrieval"
TOKEN = "YOUR_TOKEN_HERE"  # Replace with your actual token

def test_instagram_extraction():
    """Test Instagram URL extraction"""
    print("Testing Instagram URL extraction...")
    
    test_text = """
    Check out this amazing reel: https://www.instagram.com/reel/C4hgXvRg4ZV/
    And this one too: https://www.instagram.com/p/C4hgXvRg4ZV/
    """
    
    url = f"{API_BASE_URL}/extract/instagram/urls"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}"
    }
    data = {
        "text": test_text
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def test_youtube_extraction():
    """Test YouTube URL extraction"""
    print("\nTesting YouTube URL extraction...")
    
    test_text = """
    Watch this video: https://www.youtube.com/watch?v=dQw4w9WgXcQ
    And this short: https://youtu.be/dQw4w9WgXcQ
    """
    
    url = f"{API_BASE_URL}/extract/youtube/urls"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}"
    }
    data = {
        "text": test_text
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Instagram and YouTube Extraction Endpoint Test")
    print("=" * 50)
    
    # First, get a token if needed
    print("\nNOTE: You need to replace TOKEN in this script with your actual auth token")
    print("You can get it from browser DevTools > Application > Local Storage > token")
    print("\nOr uncomment the login code below to get a token programmatically")
    
    # Uncomment to login and get token
    # login_url = "http://localhost:8082/api/v1/auths/signin"
    # login_data = {
    #     "email": "your_email@example.com",
    #     "password": "your_password"
    # }
    # login_response = requests.post(login_url, json=login_data)
    # if login_response.status_code == 200:
    #     TOKEN = login_response.json()["token"]
    #     print(f"Token obtained: {TOKEN[:20]}...")
    
    if TOKEN == "YOUR_TOKEN_HERE":
        print("\n⚠️  Please update the TOKEN variable in this script first!")
        exit(1)
    
    test_instagram_extraction()
    test_youtube_extraction()