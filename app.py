from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import base64
import uuid
from datetime import datetime
from crypto_utils import CryptoManager
from user_manager import UserManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize managers
user_manager = UserManager()
crypto_manager = CryptoManager()

# Store active sessions and AES keys
active_sessions = {}  # {session_id: {'username': str, 'private_key': obj}}
chat_aes_keys = {}    # {chat_id: aes_key}

@app.route('/')
def index():
    """Serve the main chat interface"""
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username:
        return jsonify({'success': False, 'message': 'Username is required'})
    
    if not password:
        return jsonify({'success': False, 'message': 'Password is required'})
    
    success, message = user_manager.register_user(username, password)
    return jsonify({'success': success, 'message': message})

@app.route('/users', methods=['GET'])
def get_users():
    """Get list of all users"""
    users = user_manager.get_all_users()
    return jsonify({'users': users})

@app.route('/search_users', methods=['POST'])
def search_users():
    """Search for users by username"""
    data = request.get_json()
    query = data.get('query', '')
    exclude_user = data.get('exclude_user')
    
    users = user_manager.search_users(query, exclude_user)
    return jsonify({'users': users})

@app.route('/add_friend', methods=['POST'])
def add_friend():
    """Add a friend"""
    data = request.get_json()
    username = data.get('username')
    friend_username = data.get('friend_username')
    
    if not username or not friend_username:
        return jsonify({'success': False, 'message': 'Username and friend username required'})
    
    success, message = user_manager.add_friend(username, friend_username)
    return jsonify({'success': success, 'message': message})

@app.route('/friends/<username>', methods=['GET'])
def get_friends(username):
    """Get user's friends"""
    friends = user_manager.get_friends(username)
    return jsonify({'friends': friends})

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"Client disconnected: {request.sid}")
    
    # Clean up session data
    if request.sid in active_sessions:
        username = active_sessions[request.sid]['username']
        user_manager.update_last_seen(username)
        del active_sessions[request.sid]

@socketio.on('login')
def handle_login(data):
    """Handle user login"""
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        emit('login_response', {'success': False, 'message': 'Username and password required'})
        return
    
    # Authenticate user
    auth_success, auth_message = user_manager.authenticate_user(username, password)
    if not auth_success:
        emit('login_response', {'success': False, 'message': auth_message})
        return
    
    # Store session data
    private_key_pem = user_manager.get_user_private_key(username)
    private_key = crypto_manager.deserialize_private_key(private_key_pem)
    
    active_sessions[request.sid] = {
        'username': username,
        'private_key': private_key
    }
    
    # Update last seen
    user_manager.update_last_seen(username)
    
    emit('login_response', {
        'success': True, 
        'message': 'Logged in successfully',
        'username': username
    })

@socketio.on('get_public_key')
def handle_get_public_key(data):
    """Send user's public key to client"""
    username = data.get('username')
    
    if not username or not user_manager.user_exists(username):
        emit('public_key_response', {'success': False, 'message': 'User not found'})
        return
    
    public_key_pem = user_manager.get_user_public_key(username)
    emit('public_key_response', {
        'success': True,
        'public_key': public_key_pem
    })

@socketio.on('start_chat')
def handle_start_chat(data):
    """Start a new chat session"""
    participants = data.get('participants', [])
    current_user = active_sessions.get(request.sid, {}).get('username')
    
    print(f"Start chat request from {current_user} with participants: {participants}")
    
    if not current_user:
        print("Error: User not logged in")
        emit('chat_error', {'message': 'Not logged in'})
        return
    
    if len(participants) < 1:
        print("Error: No participants provided")
        emit('chat_error', {'message': 'At least 1 participant required'})
        return
    
    # Add current user to participants if not already included
    if current_user not in participants:
        participants.append(current_user)
    
    print(f"Final participants list: {participants}")
    
    # Generate unique chat ID
    chat_id = str(uuid.uuid4())
    print(f"Generated chat ID: {chat_id}")
    
    # Generate AES key for this chat
    aes_key = crypto_manager.generate_aes_key()
    chat_aes_keys[chat_id] = aes_key
    
    # Join the current user to the chat room
    join_room(chat_id)
    print(f"User {current_user} joined room {chat_id}")
    
    # Send AES key to each participant (simplified approach)
    for participant in participants:
        if user_manager.user_exists(participant):
            print(f"Sending AES key to participant: {participant}")
            
            # Find participant's session ID
            participant_session = None
            for session_id, session_data in active_sessions.items():
                if session_data.get('username') == participant:
                    participant_session = session_id
                    break
            
            if participant_session:
                print(f"Sending AES key to session: {participant_session}")
                # Send AES key directly (base64 encoded for simplicity)
                socketio.emit('aes_key', {
                    'chat_id': chat_id,
                    'aes_key': base64.b64encode(aes_key).decode('utf-8')
                }, room=participant_session)
            else:
                print(f"Warning: Participant {participant} not found in active sessions")
    
    emit('chat_started', {
        'chat_id': chat_id,
        'participants': participants
    })
    print(f"Chat started successfully with ID: {chat_id}")

@socketio.on('join_chat')
def handle_join_chat(data):
    """Join a chat room"""
    chat_id = data.get('chat_id')
    username = active_sessions.get(request.sid, {}).get('username')
    
    if not username:
        emit('chat_error', {'message': 'Not logged in'})
        return
    
    join_room(chat_id)
    emit('joined_chat', {'chat_id': chat_id, 'username': username})

@socketio.on('leave_chat')
def handle_leave_chat(data):
    """Leave a chat room"""
    chat_id = data.get('chat_id')
    username = active_sessions.get(request.sid, {}).get('username')
    
    if username:
        leave_room(chat_id)
        emit('left_chat', {'chat_id': chat_id, 'username': username})

@socketio.on('send_message')
def handle_send_message(data):
    """Handle sending encrypted messages"""
    chat_id = data.get('chat_id')
    encrypted_message = data.get('encrypted_message')
    username = active_sessions.get(request.sid, {}).get('username')
    
    if not username:
        emit('message_error', {'message': 'Not logged in'})
        return
    
    if not chat_id or not encrypted_message:
        emit('message_error', {'message': 'Missing chat_id or message'})
        return
    
    # Store encrypted message in chat log
    message_data = {
        'username': username,
        'encrypted_message': encrypted_message,
        'timestamp': datetime.now().isoformat()
    }
    
    # Load existing chat log
    encrypted_log = user_manager.load_chat_log(chat_id)
    if encrypted_log and chat_id in chat_aes_keys:
        try:
            chat_log = crypto_manager.decrypt_chat_log(encrypted_log, chat_aes_keys[chat_id])
        except:
            chat_log = []
    else:
        chat_log = []
    
    # Add new message
    chat_log.append(message_data)
    
    # Save encrypted chat log
    if chat_id in chat_aes_keys:
        encrypted_log = crypto_manager.encrypt_chat_log(chat_log, chat_aes_keys[chat_id])
        user_manager.save_chat_log(chat_id, encrypted_log)
    
    # Broadcast encrypted message to all participants in the chat
    socketio.emit('message_received', {
        'chat_id': chat_id,
        'username': username,
        'encrypted_message': encrypted_message,
        'timestamp': message_data['timestamp']
    }, room=chat_id)

@socketio.on('get_chat_history')
def handle_get_chat_history(data):
    """Send encrypted chat history to client"""
    chat_id = data.get('chat_id')
    username = active_sessions.get(request.sid, {}).get('username')
    
    if not username:
        emit('chat_history_error', {'message': 'Not logged in'})
        return
    
    # Load encrypted chat log
    encrypted_log = user_manager.load_chat_log(chat_id)
    if encrypted_log and chat_id in chat_aes_keys:
        try:
            chat_log = crypto_manager.decrypt_chat_log(encrypted_log, chat_aes_keys[chat_id])
            emit('chat_history', {
                'chat_id': chat_id,
                'messages': chat_log
            })
        except Exception as e:
            emit('chat_history_error', {'message': 'Failed to decrypt chat history'})
    else:
        emit('chat_history', {
            'chat_id': chat_id,
            'messages': []
        })

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
