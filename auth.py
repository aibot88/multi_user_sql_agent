"""
Authentication and session management for the multi-user SQL agent application.
"""
import uuid
import os
from typing import Dict, Optional
from datetime import datetime, timedelta
from models import User


class SessionManager:
    """Manages user sessions and authentication."""
    
    def __init__(self):
        self.sessions: Dict[str, User] = {}
        self.session_timeout = timedelta(hours=24)  # 24 hour session timeout
    
    def create_session(self, username: str) -> str:
        """Create a new session for a user."""
        # Clean up expired sessions first
        self._cleanup_expired_sessions()
        
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        
        # Create database path for this user
        safe_username = "".join(c for c in username if c.isalnum() or c in '_-')
        database_path = f"user_databases/{safe_username}_{session_id[:8]}.db"
        
        # Create user object
        user = User(
            username=username,
            session_id=session_id,
            database_path=database_path
        )
        
        # Store session
        self.sessions[session_id] = user
        
        return session_id
    
    def get_user(self, session_id: str) -> Optional[User]:
        """Get user by session ID."""
        if session_id not in self.sessions:
            return None
        
        user = self.sessions[session_id]
        
        # Check if session has expired
        if datetime.now() - user.created_at > self.session_timeout:
            self.delete_session(session_id)
            return None
        
        return user
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self.sessions:
            user = self.sessions[session_id]
            
            # Optionally clean up user database file
            # (Keeping it for now to preserve user data across sessions)
            
            del self.sessions[session_id]
            return True
        return False
    
    def _cleanup_expired_sessions(self):
        """Remove expired sessions."""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, user in self.sessions.items():
            if current_time - user.created_at > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.delete_session(session_id)
    
    def get_active_sessions_count(self) -> int:
        """Get count of active sessions."""
        self._cleanup_expired_sessions()
        return len(self.sessions)
    
    def validate_session(self, session_id: str) -> bool:
        """Validate if a session is active and valid."""
        return self.get_user(session_id) is not None


# Global session manager instance
session_manager = SessionManager()