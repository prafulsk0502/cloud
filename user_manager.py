import json
import os
import base64
import hashlib
import secrets
from datetime import datetime
from crypto_utils import CryptoManager

class UserManager:
    """Manages user registration, authentication, and key storage"""
    
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.crypto_manager = CryptoManager()
        self.users_file = os.path.join(data_dir, "users.json")
        self.chat_logs_dir = os.path.join(data_dir, "chat_logs")
        
        # Create directories if they don't exist
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(self.chat_logs_dir, exist_ok=True)
        
        # Load existing users
        self.users = self._load_users()
    
    def _load_users(self):
        """Load users from file"""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}
    
    def _save_users(self):
        """Save users to file"""
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def _hash_password(self, password):
        """Hash password with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return salt + password_hash.hex()
    
    def _verify_password(self, password, stored_hash):
        """Verify password against stored hash"""
        salt = stored_hash[:32]  # First 32 chars are salt
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return stored_hash == salt + password_hash.hex()

    def register_user(self, username, password):
        """Register a new user with RSA key pair and password"""
        if username in self.users:
            return False, "Username already exists"
        
        if len(password) < 6:
            return False, "Password must be at least 6 characters"
        
        # Generate RSA key pair
        private_key, public_key = self.crypto_manager.generate_rsa_keypair()
        
        # Serialize keys
        private_key_pem = self.crypto_manager.serialize_private_key(private_key)
        public_key_pem = self.crypto_manager.serialize_public_key(public_key)
        
        # Hash password
        password_hash = self._hash_password(password)
        
        # Store user data
        self.users[username] = {
            "public_key": public_key_pem,
            "private_key": private_key_pem,
            "password_hash": password_hash,
            "created_at": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat(),
            "friends": []
        }
        
        self._save_users()
        return True, "User registered successfully"
    
    def get_user_public_key(self, username):
        """Get user's public key"""
        if username not in self.users:
            return None
        return self.users[username]["public_key"]
    
    def get_user_private_key(self, username):
        """Get user's private key"""
        if username not in self.users:
            return None
        return self.users[username]["private_key"]
    
    def update_last_seen(self, username):
        """Update user's last seen timestamp"""
        if username in self.users:
            self.users[username]["last_seen"] = datetime.now().isoformat()
            self._save_users()
    
    def get_all_users(self):
        """Get list of all registered users"""
        return list(self.users.keys())
    
    def user_exists(self, username):
        """Check if user exists"""
        return username in self.users
    
    def save_chat_log(self, chat_id, encrypted_data):
        """Save encrypted chat log to file"""
        log_file = os.path.join(self.chat_logs_dir, f"{chat_id}.enc")
        with open(log_file, 'wb') as f:
            f.write(encrypted_data)
    
    def load_chat_log(self, chat_id):
        """Load encrypted chat log from file"""
        log_file = os.path.join(self.chat_logs_dir, f"{chat_id}.enc")
        if os.path.exists(log_file):
            with open(log_file, 'rb') as f:
                return f.read()
        return None
    
    def authenticate_user(self, username, password):
        """Authenticate user with username and password"""
        if username not in self.users:
            return False, "User not found"
        
        stored_hash = self.users[username].get('password_hash')
        if not stored_hash:
            return False, "User not found"
        
        if self._verify_password(password, stored_hash):
            return True, "Authentication successful"
        else:
            return False, "Invalid password"
    
    def add_friend(self, username, friend_username):
        """Add a friend to user's friend list"""
        if username not in self.users:
            return False, "User not found"
        
        if friend_username not in self.users:
            return False, "Friend not found"
        
        if friend_username == username:
            return False, "Cannot add yourself as friend"
        
        if friend_username not in self.users[username]['friends']:
            self.users[username]['friends'].append(friend_username)
            self._save_users()
            return True, f"Added {friend_username} as friend"
        else:
            return False, "User is already your friend"
    
    def get_friends(self, username):
        """Get user's friend list"""
        if username not in self.users:
            return []
        return self.users[username].get('friends', [])
    
    def search_users(self, query, exclude_user=None):
        """Search for users by username"""
        matching_users = []
        for username in self.users.keys():
            if exclude_user and username == exclude_user:
                continue
            if query.lower() in username.lower():
                matching_users.append(username)
        return matching_users
