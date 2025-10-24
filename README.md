# Secure Chat App with End-to-End Encryption

A private chat application with end-to-end encryption using RSA and AES cryptography, built with Python Flask-SocketIO and modern web technologies.

## Features

- **End-to-End Encryption**: Messages are encrypted with AES-256-GCM and keys are shared via RSA-OAEP
- **Password Authentication**: Secure user registration and login with password hashing
- **Friend Management**: Add friends by searching usernames and manage friend lists
- **Real-time Communication**: Powered by Flask-SocketIO for instant messaging
- **Secure Key Management**: RSA key pairs generated per user session
- **Encrypted Storage**: Chat logs are encrypted and stored on the server
- **Modern UI**: Beautiful, responsive interface with encryption status indicators
- **Client-side Decryption**: Messages are only decrypted on the client side

## Architecture

### Encryption Flow
1. **User Registration**: Each user gets a unique RSA key pair and password hash
2. **Chat Initiation**: AES key is generated and shared directly with participants
3. **Message Encryption**: Messages are encrypted with AES-256-GCM before transmission
4. **Secure Storage**: Chat logs are encrypted and stored on the server
5. **Client Decryption**: Messages are decrypted only on the client side

### Components
- **Backend**: Flask-SocketIO server with cryptographic utilities
- **Frontend**: HTML5/JavaScript client with Web Crypto API
- **Storage**: Encrypted chat logs and user data

## Installation

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Setup
1. Clone or download the project files
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```

4. Open your browser and navigate to `http://localhost:5000`

## Usage

### Getting Started
1. **Register**: Create a new username and password (this generates your RSA key pair)
2. **Login**: Use your username and password to log in
3. **Add Friends**: Search for users by username and add them as friends
4. **Start Chat**: Select friends and start a new encrypted chat
5. **Send Messages**: Type messages that are automatically encrypted

### Security Features
- All messages are encrypted with AES-256-GCM
- RSA-OAEP is used for key exchange
- Chat logs are encrypted before storage
- Private keys never leave the client
- Real-time encryption status indicator

## Technical Details

### Encryption Stack
- **RSA-OAEP**: 2048-bit keys for secure key exchange
- **AES-GCM**: 256-bit encryption for message content
- **Web Crypto API**: Browser-native cryptographic functions
- **Python Cryptography**: Server-side cryptographic operations

### File Structure
```
cchat/
├── app.py                 # Main Flask-SocketIO server
├── crypto_utils.py        # Server-side cryptographic utilities
├── user_manager.py       # User registration and key management
├── requirements.txt      # Python dependencies
├── templates/
│   └── index.html        # Main chat interface
├── static/
│   └── crypto.js         # Client-side encryption utilities
└── data/                 # Encrypted storage directory
    ├── users.json        # User data and keys
    └── chat_logs/        # Encrypted chat logs
```

## Security Considerations

### What's Encrypted
- ✅ Message content (AES-256-GCM)
- ✅ Chat logs on server (AES-256-GCM)
- ✅ AES keys in transit (RSA-OAEP)
- ✅ User private keys (stored encrypted)

### What's Not Encrypted
- ❌ Usernames (for routing purposes)
- ❌ Timestamps (for message ordering)
- ❌ Chat metadata (participants, etc.)

### Limitations
- This is a demonstration project
- No perfect forward secrecy implementation
- No message authentication beyond GCM
- No key rotation mechanism
- No secure deletion of old keys

## Development

### Running in Development Mode
```bash
python app.py
```
The server will start in debug mode on `http://localhost:5000`

### Testing the Encryption
1. Open multiple browser tabs/windows
2. Register different users
3. Start a chat between users
4. Send messages and verify they're encrypted in transit
5. Check browser developer tools to see encrypted data

## Contributing

This is a demonstration project showcasing end-to-end encryption concepts. For production use, consider:
- Implementing perfect forward secrecy
- Adding message authentication
- Implementing key rotation
- Adding secure key deletion
- Implementing message threading
- Adding file sharing capabilities

## License

This project is for educational purposes. Use at your own risk for production applications.

## Disclaimer

This software is provided for educational and demonstration purposes only. While it implements real cryptographic algorithms, it should not be used for production systems without thorough security review and additional security measures.
