import os
import json
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import secrets

class CryptoManager:
    """Handles RSA and AES encryption/decryption operations"""
    
    def __init__(self):
        self.backend = default_backend()
    
    def generate_rsa_keypair(self):
        """Generate a new RSA key pair"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=self.backend
        )
        public_key = private_key.public_key()
        return private_key, public_key
    
    def serialize_public_key(self, public_key):
        """Serialize public key to PEM format"""
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem.decode('utf-8')
    
    def deserialize_public_key(self, pem_string):
        """Deserialize public key from PEM format"""
        return serialization.load_pem_public_key(
            pem_string.encode('utf-8'),
            backend=self.backend
        )
    
    def serialize_private_key(self, private_key):
        """Serialize private key to PEM format"""
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        return pem.decode('utf-8')
    
    def deserialize_private_key(self, pem_string):
        """Deserialize private key from PEM format"""
        return serialization.load_pem_private_key(
            pem_string.encode('utf-8'),
            password=None,
            backend=self.backend
        )
    
    def generate_aes_key(self):
        """Generate a random AES key"""
        return secrets.token_bytes(32)  # 256-bit key
    
    def encrypt_aes_key(self, aes_key, public_key):
        """Encrypt AES key with RSA public key"""
        encrypted_key = public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return encrypted_key
    
    def decrypt_aes_key(self, encrypted_aes_key, private_key):
        """Decrypt AES key with RSA private key"""
        aes_key = private_key.decrypt(
            encrypted_aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return aes_key
    
    def encrypt_message(self, message, aes_key):
        """Encrypt message with AES"""
        # Generate random IV
        iv = secrets.token_bytes(16)
        
        # Create cipher
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=self.backend)
        encryptor = cipher.encryptor()
        
        # Pad message to multiple of 16 bytes
        message_bytes = message.encode('utf-8')
        padding_length = 16 - (len(message_bytes) % 16)
        padded_message = message_bytes + bytes([padding_length] * padding_length)
        
        # Encrypt
        encrypted_message = encryptor.update(padded_message) + encryptor.finalize()
        
        # Return IV + encrypted message
        return iv + encrypted_message
    
    def decrypt_message(self, encrypted_data, aes_key):
        """Decrypt message with AES"""
        # Extract IV and encrypted message
        iv = encrypted_data[:16]
        encrypted_message = encrypted_data[16:]
        
        # Create cipher
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=self.backend)
        decryptor = cipher.decryptor()
        
        # Decrypt
        padded_message = decryptor.update(encrypted_message) + decryptor.finalize()
        
        # Remove padding
        padding_length = padded_message[-1]
        message_bytes = padded_message[:-padding_length]
        
        return message_bytes.decode('utf-8')
    
    def encrypt_chat_log(self, chat_data, aes_key):
        """Encrypt chat log data"""
        json_data = json.dumps(chat_data)
        return self.encrypt_message(json_data, aes_key)
    
    def decrypt_chat_log(self, encrypted_data, aes_key):
        """Decrypt chat log data"""
        json_data = self.decrypt_message(encrypted_data, aes_key)
        return json.loads(json_data)
