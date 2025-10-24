#!/usr/bin/env python3
"""
Startup script for the Secure Chat App with End-to-End Encryption
"""

import sys
import os
import subprocess

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import flask_socketio
        import cryptography
        print("[OK] All required dependencies are installed")
        return True
    except ImportError as e:
        print(f"[FAIL] Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False

def run_tests():
    """Run the test suite"""
    print("Running E2EE test suite...")
    try:
        result = subprocess.run([sys.executable, "test_e2ee.py"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("[OK] All tests passed")
            return True
        else:
            print("[FAIL] Some tests failed")
            print(result.stdout)
            return False
    except Exception as e:
        print(f"[FAIL] Error running tests: {e}")
        return False

def start_server():
    """Start the Flask-SocketIO server"""
    print("Starting Secure Chat Server...")
    print("Server will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Import and run the app
        from app import app, socketio
        socketio.run(app, debug=False, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"[FAIL] Error starting server: {e}")
        return False
    
    return True

def main():
    """Main startup function"""
    print("Secure Chat App - End-to-End Encryption")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Run tests
    if not run_tests():
        print("Warning: Tests failed, but continuing...")
    
    print("\nStarting server...")
    return start_server()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
