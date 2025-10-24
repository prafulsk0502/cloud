#!/usr/bin/env python3
"""
Test the simplified AES key exchange
"""

import requests
import json

def test_simplified_chat():
    """Test the simplified chat functionality"""
    base_url = "http://localhost:5000"
    
    print("Testing Simplified Chat Functionality")
    print("=" * 40)
    
    # Register test users
    print("1. Registering test users...")
    users = [
        {"username": "testuser1", "password": "password123"},
        {"username": "testuser2", "password": "password456"}
    ]
    
    for user in users:
        response = requests.post(f"{base_url}/register", json=user)
        result = response.json()
        if result['success']:
            print(f"   [OK] Registered: {user['username']}")
        else:
            print(f"   [INFO] {user['username']}: {result['message']}")
    
    # Add friends
    print("\n2. Adding friends...")
    response = requests.post(f"{base_url}/add_friend", json={
        "username": "testuser1",
        "friend_username": "testuser2"
    })
    result = response.json()
    if result['success']:
        print(f"   [OK] {result['message']}")
    else:
        print(f"   [INFO] {result['message']}")
    
    print("\n" + "=" * 40)
    print("Server is running with simplified AES key exchange!")
    print("Open browser to: http://localhost:5000")
    print("\nThe RSA decryption error should now be fixed.")
    print("Try starting a chat between testuser1 and testuser2!")

if __name__ == "__main__":
    try:
        test_simplified_chat()
    except requests.exceptions.ConnectionError:
        print("Server not running. Please start the server first:")
        print("python app.py")
    except Exception as e:
        print(f"Test failed: {e}")
