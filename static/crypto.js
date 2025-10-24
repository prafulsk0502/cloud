// Client-side encryption utilities for E2EE chat
class ClientCrypto {
    constructor() {
        this.aesKey = null;
        this.rsaKeyPair = null;
    }

    // Generate RSA key pair
    async generateRSAKeyPair() {
        try {
            this.rsaKeyPair = await window.crypto.subtle.generateKey(
                {
                    name: "RSA-OAEP",
                    modulusLength: 2048,
                    publicExponent: new Uint8Array([1, 0, 1]),
                    hash: "SHA-256",
                },
                true,
                ["encrypt", "decrypt"]
            );
            return this.rsaKeyPair;
        } catch (error) {
            console.error('Failed to generate RSA key pair:', error);
            throw error;
        }
    }

    // Export public key
    async exportPublicKey() {
        if (!this.rsaKeyPair) {
            throw new Error('RSA key pair not generated');
        }
        
        const exported = await window.crypto.subtle.exportKey(
            "spki",
            this.rsaKeyPair.publicKey
        );
        return this.arrayBufferToBase64(exported);
    }

    // Import public key
    async importPublicKey(base64Key) {
        const keyData = this.base64ToArrayBuffer(base64Key);
        return await window.crypto.subtle.importKey(
            "spki",
            keyData,
            {
                name: "RSA-OAEP",
                hash: "SHA-256",
            },
            true,
            ["encrypt"]
        );
    }

    // Generate AES key
    async generateAESKey() {
        this.aesKey = await window.crypto.subtle.generateKey(
            {
                name: "AES-GCM",
                length: 256,
            },
            true,
            ["encrypt", "decrypt"]
        );
        return this.aesKey;
    }

    // Export AES key
    async exportAESKey() {
        if (!this.aesKey) {
            throw new Error('AES key not generated');
        }
        
        const exported = await window.crypto.subtle.exportKey(
            "raw",
            this.aesKey
        );
        return this.arrayBufferToBase64(exported);
    }

    // Import AES key
    async importAESKey(base64Key) {
        const keyData = this.base64ToArrayBuffer(base64Key);
        this.aesKey = await window.crypto.subtle.importKey(
            "raw",
            keyData,
            {
                name: "AES-GCM",
                length: 256,
            },
            true,
            ["encrypt", "decrypt"]
        );
        return this.aesKey;
    }

    // Encrypt AES key with RSA public key
    async encryptAESKeyWithRSA(aesKeyBase64, publicKey) {
        const aesKeyData = this.base64ToArrayBuffer(aesKeyBase64);
        const encrypted = await window.crypto.subtle.encrypt(
            {
                name: "RSA-OAEP",
            },
            publicKey,
            aesKeyData
        );
        return this.arrayBufferToBase64(encrypted);
    }

    // Decrypt AES key with RSA private key
    async decryptAESKeyWithRSA(encryptedAESKeyBase64) {
        if (!this.rsaKeyPair) {
            throw new Error('RSA key pair not available');
        }
        
        const encryptedData = this.base64ToArrayBuffer(encryptedAESKeyBase64);
        const decrypted = await window.crypto.subtle.decrypt(
            {
                name: "RSA-OAEP",
            },
            this.rsaKeyPair.privateKey,
            encryptedData
        );
        return this.arrayBufferToBase64(decrypted);
    }

    // Encrypt message with AES
    async encryptMessage(message) {
        if (!this.aesKey) {
            throw new Error('AES key not available');
        }

        const encoder = new TextEncoder();
        const data = encoder.encode(message);
        
        // Generate random IV
        const iv = window.crypto.getRandomValues(new Uint8Array(12));
        
        const encrypted = await window.crypto.subtle.encrypt(
            {
                name: "AES-GCM",
                iv: iv,
            },
            this.aesKey,
            data
        );

        // Combine IV and encrypted data
        const combined = new Uint8Array(iv.length + encrypted.byteLength);
        combined.set(iv);
        combined.set(new Uint8Array(encrypted), iv.length);
        
        return this.arrayBufferToBase64(combined.buffer);
    }

    // Decrypt message with AES
    async decryptMessage(encryptedMessageBase64) {
        if (!this.aesKey) {
            throw new Error('AES key not available');
        }

        const combined = this.base64ToArrayBuffer(encryptedMessageBase64);
        const iv = combined.slice(0, 12);
        const encrypted = combined.slice(12);

        const decrypted = await window.crypto.subtle.decrypt(
            {
                name: "AES-GCM",
                iv: iv,
            },
            this.aesKey,
            encrypted
        );

        const decoder = new TextDecoder();
        return decoder.decode(decrypted);
    }

    // Utility functions
    arrayBufferToBase64(buffer) {
        const bytes = new Uint8Array(buffer);
        let binary = '';
        for (let i = 0; i < bytes.byteLength; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        return btoa(binary);
    }

    base64ToArrayBuffer(base64) {
        const binary = atob(base64);
        const bytes = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++) {
            bytes[i] = binary.charCodeAt(i);
        }
        return bytes.buffer;
    }
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ClientCrypto;
}
