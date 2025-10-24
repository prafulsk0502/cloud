#!/usr/bin/env python3
"""
Test script for the Secure Chat App E2EE functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crypto_utils import CryptoManager
from user_manager import UserManager

def test_crypto_operations():
    """Test basic cryptographic operations"""
    print("Testing cryptographic operations...")
    
    crypto_manager = CryptoManager()
    
    # Test RSA key generation
    print("1. Generating RSA key pair...")
    private_key, public_key = crypto_manager.generate_rsa_keypair()
    print("   RSA key pair generated")
    
    # Test key serialization
    print("2. Testing key serialization...")
    private_pem = crypto_manager.serialize_private_key(private_key)
    public_pem = crypto_manager.serialize_public_key(public_key)
    print("   Keys serialized to PEM format")
    
    # Test key deserialization
    print("3. Testing key deserialization...")
    deserialized_private = crypto_manager.deserialize_private_key(private_pem)
    deserialized_public = crypto_manager.deserialize_public_key(public_pem)
    print("   Keys deserialized from PEM format")
    
    # Test AES key generation
    print("4. Generating AES key...")
    aes_key = crypto_manager.generate_aes_key()
    print("   AES key generated")
    
    # Test AES key encryption with RSA
    print("5. Testing AES key encryption with RSA...")
    encrypted_aes_key = crypto_manager.encrypt_aes_key(aes_key, deserialized_public)
    print("   AES key encrypted with RSA public key")
    
    # Test AES key decryption with RSA
    print("6. Testing AES key decryption with RSA...")
    decrypted_aes_key = crypto_manager.decrypt_aes_key(encrypted_aes_key, deserialized_private)
    print("   [OK] AES key decrypted with RSA private key")
    
    # Verify keys match
    if aes_key == decrypted_aes_key:
        print("   [OK] Decrypted AES key matches original")
    else:
        print("   [FAIL] Decrypted AES key does not match original")
        return False
    
    # Test message encryption/decryption
    print("7. Testing message encryption/decryption...")
    test_message = "Hello, this is a test message for E2EE!"
    encrypted_message = crypto_manager.encrypt_message(test_message, aes_key)
    decrypted_message = crypto_manager.decrypt_message(encrypted_message, aes_key)
    
    if decrypted_message == test_message:
        print("   [OK] Message encryption/decryption successful")
    else:
        print("   [FAIL] Message encryption/decryption failed")
        return False
    
    print("\nAll cryptographic tests passed!")
    return True

def test_user_management():
    """Test user management functionality"""
    print("\nTesting user management...")
    
    # Clean up any existing test data
    import shutil
    if os.path.exists("test_data"):
        shutil.rmtree("test_data")
    
    user_manager = UserManager("test_data")
    
    # Test user registration
    print("1. Testing user registration...")
    success, message = user_manager.register_user("testuser1", "password123")
    if success:
        print("   [OK] User 'testuser1' registered successfully")
    else:
        print(f"   [FAIL] User registration failed: {message}")
        return False
    
    # Test duplicate registration
    success, message = user_manager.register_user("testuser1", "password123")
    if not success and "already exists" in message:
        print("   [OK] Duplicate registration properly rejected")
    else:
        print("   [FAIL] Duplicate registration not handled correctly")
        return False
    
    # Test authentication
    print("2. Testing user authentication...")
    auth_success, auth_message = user_manager.authenticate_user("testuser1", "password123")
    if auth_success:
        print("   [OK] User authentication successful")
    else:
        print(f"   [FAIL] User authentication failed: {auth_message}")
        return False
    
    # Test wrong password
    auth_success, auth_message = user_manager.authenticate_user("testuser1", "wrongpassword")
    if not auth_success and "Invalid password" in auth_message:
        print("   [OK] Wrong password properly rejected")
    else:
        print("   [FAIL] Wrong password not handled correctly")
        return False
    
    # Test user existence check
    print("3. Testing user existence check...")
    if user_manager.user_exists("testuser1"):
        print("   [OK] User existence check works")
    else:
        print("   [FAIL] User existence check failed")
        return False
    
    # Test key retrieval
    print("4. Testing key retrieval...")
    public_key = user_manager.get_user_public_key("testuser1")
    private_key = user_manager.get_user_private_key("testuser1")
    
    if public_key and private_key:
        print("   [OK] User keys retrieved successfully")
    else:
        print("   [FAIL] Failed to retrieve user keys")
        return False
    
    # Test user list
    print("5. Testing user list...")
    users = user_manager.get_all_users()
    if "testuser1" in users:
        print("   [OK] User appears in user list")
    else:
        print("   [FAIL] User not found in user list")
        return False
    
    # Test friend management
    print("6. Testing friend management...")
    user_manager.register_user("testuser2", "password456")
    
    # Add friend
    success, message = user_manager.add_friend("testuser1", "testuser2")
    if success:
        print("   [OK] Friend added successfully")
    else:
        print(f"   [FAIL] Failed to add friend: {message}")
        return False
    
    # Get friends
    friends = user_manager.get_friends("testuser1")
    if "testuser2" in friends:
        print("   [OK] Friend appears in friend list")
    else:
        print("   [FAIL] Friend not found in friend list")
        return False
    
    # Test user search
    print("7. Testing user search...")
    search_results = user_manager.search_users("test", exclude_user="testuser1")
    if "testuser2" in search_results:
        print("   [OK] User search works correctly")
    else:
        print("   [FAIL] User search failed")
        return False
    
    # Clean up test data
    shutil.rmtree("test_data")
    print("   [OK] Test data cleaned up")
    
    print("\nAll user management tests passed!")
    return True

def test_chat_log_encryption():
    """Test encrypted chat log functionality"""
    print("\nTesting chat log encryption...")
    
    # Clean up any existing test data
    import shutil
    if os.path.exists("test_data"):
        shutil.rmtree("test_data")
    
    user_manager = UserManager("test_data")
    crypto_manager = CryptoManager()
    
    # Generate AES key for chat
    aes_key = crypto_manager.generate_aes_key()
    
    # Create test chat data
    test_chat_data = [
        {
            "username": "user1",
            "encrypted_message": "encrypted_msg_1",
            "timestamp": "2023-01-01T12:00:00"
        },
        {
            "username": "user2", 
            "encrypted_message": "encrypted_msg_2",
            "timestamp": "2023-01-01T12:01:00"
        }
    ]
    
    print("1. Testing chat log encryption...")
    encrypted_log = crypto_manager.encrypt_chat_log(test_chat_data, aes_key)
    print("   [OK] Chat log encrypted")
    
    print("2. Testing chat log decryption...")
    decrypted_log = crypto_manager.decrypt_chat_log(encrypted_log, aes_key)
    print("   [OK] Chat log decrypted")
    
    # Verify data integrity
    if decrypted_log == test_chat_data:
        print("   [OK] Chat log data integrity verified")
    else:
        print("   [FAIL] Chat log data integrity check failed")
        return False
    
    print("3. Testing chat log storage...")
    chat_id = "test_chat_123"
    user_manager.save_chat_log(chat_id, encrypted_log)
    print("   [OK] Chat log saved to file")
    
    print("4. Testing chat log loading...")
    loaded_log = user_manager.load_chat_log(chat_id)
    if loaded_log == encrypted_log:
        print("   [OK] Chat log loaded from file")
    else:
        print("   [FAIL] Chat log loading failed")
        return False
    
    # Clean up test data
    shutil.rmtree("test_data")
    print("   [OK] Test data cleaned up")
    
    print("\nAll chat log encryption tests passed!")
    return True

def main():
    """Run all tests"""
    print("Secure Chat App - E2EE Test Suite")
    print("=" * 50)
    
    tests = [
        test_crypto_operations,
        test_user_management,
        test_chat_log_encryption
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"\nTest failed with error: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed! The E2EE chat app is ready to use.")
        return True
    else:
        print("Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
