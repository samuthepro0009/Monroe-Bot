
# Credentials management for Monroe Social Club Dashboard
import hashlib
import os

class CredentialsManager:
    """Simple credentials management for dashboard users"""
    
    def __init__(self):
        # Store credentials as username: hashed_password pairs
        self.credentials = {
            # Existing credential (if any)
            "Samu": self._hash_password("NapoliEsplosa11"),  # Default admin
            
            # New credentials as requested
            "Rev": self._hash_password("kitemmurtstravev"),
            "Royal": self._hash_password("dionettuno"),
            "Luca": self._hash_password("TETTECULO1")
        }
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_credentials(self, username: str, password: str) -> bool:
        """Verify username and password combination"""
        if username not in self.credentials:
            return False
        
        hashed_input = self._hash_password(password)
        return self.credentials[username] == hashed_input
    
    def add_user(self, username: str, password: str) -> bool:
        """Add new user credentials"""
        if username in self.credentials:
            return False  # User already exists
        
        self.credentials[username] = self._hash_password(password)
        return True
    
    def remove_user(self, username: str) -> bool:
        """Remove user credentials"""
        if username in self.credentials:
            del self.credentials[username]
            return True
        return False
    
    def change_password(self, username: str, new_password: str) -> bool:
        """Change password for existing user"""
        if username not in self.credentials:
            return False
        
        self.credentials[username] = self._hash_password(new_password)
        return True
    
    def list_users(self) -> list:
        """Get list of all usernames"""
        return list(self.credentials.keys())

# Global instance
credentials_manager = CredentialsManager()
