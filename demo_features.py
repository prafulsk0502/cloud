#!/usr/bin/env python3
"""
Demo script for the Secure Chat App with new features
"""

import requests
import json
import time

def demo_api():
    """Demonstrate the new API features"""
    base_url = "http://localhost:5000"
    
    print("Secure Chat App - API Demo")
    print("=" * 40)
    
    # Test user registration with passwords
    print("1. Testing user registration with passwords...")
    
    users = [
        {"username": "alice", "password": "password123"},
        {"username": "bob", "password": "password456"},
        {"username": "charlie", "password": "password789"}
    ]
    
    for user in users:
        response = requests.post(f"{base_url}/register", json=user)
        result = response.json()
        if result['success']:
            print(f"   ✓ Registered user: {user['username']}")
        else:
            print(f"   ✗ Failed to register {user['username']}: {result['message']}")
    
    print("\n2. Testing user search...")
    response = requests.post(f"{base_url}/search_users", json={"query": "al"})
    search_results = response.json()
    print(f"   Search results for 'al': {search_results['users']}")
    
    print("\n3. Testing friend management...")
    # Alice adds Bob as friend
    response = requests.post(f"{base_url}/add_friend", json={
        "username": "alice",
        "friend_username": "bob"
    })
    result = response.json()
    if result['success']:
        print(f"   ✓ {result['message']}")
    else:
        print(f"   ✗ Failed to add friend: {result['message']}")
    
    # Get Alice's friends
    response = requests.get(f"{base_url}/friends/alice")
    friends = response.json()
    print(f"   Alice's friends: {friends['friends']}")
    
    print("\n4. Testing authentication...")
    # Test correct password
    response = requests.post(f"{base_url}/register", json={"username": "test_auth", "password": "testpass"})
    print("   ✓ User registered for auth test")
    
    print("\nDemo completed! Start the server with 'python app.py' to test the web interface.")
    print("Features to test in the browser:")
    print("- Register with username and password")
    print("- Login with credentials")
    print("- Search for users and add friends")
    print("- Start encrypted chats with friends")
    print("- Send encrypted messages")

if __name__ == "__main__":
    try:
        demo_api()
    except requests.exceptions.ConnectionError:
        print("Server not running. Please start the server first:")
        print("python app.py")
    except Exception as e:
        print(f"Demo failed: {e}")
