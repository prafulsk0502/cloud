#!/usr/bin/env python3
"""
Quick test script to verify chat functionality
"""

import requests
import json

def test_chat_functionality():
    """Test the chat functionality"""
    base_url = "http://localhost:5000"
    
    print("Testing Chat Functionality")
    print("=" * 30)
    
    # Test user registration
    print("1. Registering test users...")
    users = [
        {"username": "alice", "password": "password123"},
        {"username": "bob", "password": "password456"}
    ]
    
    for user in users:
        response = requests.post(f"{base_url}/register", json=user)
        result = response.json()
        if result['success']:
            print(f"   [OK] Registered: {user['username']}")
        else:
            print(f"   [FAIL] Failed to register {user['username']}: {result['message']}")
    
    # Test friend addition
    print("\n2. Adding friends...")
    response = requests.post(f"{base_url}/add_friend", json={
        "username": "alice",
        "friend_username": "bob"
    })
    result = response.json()
    if result['success']:
        print(f"   [OK] {result['message']}")
    else:
        print(f"   [FAIL] Failed to add friend: {result['message']}")
    
    # Test getting friends
    print("\n3. Getting friends list...")
    response = requests.get(f"{base_url}/friends/alice")
    friends = response.json()
    print(f"   Alice's friends: {friends['friends']}")
    
    print("\n" + "=" * 30)
    print("Server is running! Open your browser to:")
    print("http://localhost:5000")
    print("\nTo test chat functionality:")
    print("1. Register two users (e.g., alice and bob)")
    print("2. Login as alice")
    print("3. Search for 'bob' and add as friend")
    print("4. Select bob and click 'Start Chat'")
    print("5. Send messages!")
    print("\nCheck the browser console and server logs for debugging info.")

if __name__ == "__main__":
    try:
        test_chat_functionality()
    except requests.exceptions.ConnectionError:
        print("Server not running. Please start the server first:")
        print("python app.py")
    except Exception as e:
        print(f"Test failed: {e}")