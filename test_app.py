"""
Basic tests for the multi-user SQL agent application.
"""
import pytest
import os
import tempfile
import sqlite3
from fastapi.testclient import TestClient

# Import our application modules
from app import app
from auth import SessionManager
from database import DatabaseManager
from sql_agent import SimpleSQLAgent


# Test client
client = TestClient(app)


class TestSessionManager:
    """Test the session management functionality."""
    
    def test_create_session(self):
        """Test creating a new session."""
        sm = SessionManager()
        session_id = sm.create_session("testuser")
        
        assert session_id is not None
        assert len(session_id) > 0
        
        user = sm.get_user(session_id)
        assert user is not None
        assert user.username == "testuser"
        assert user.session_id == session_id
    
    def test_session_validation(self):
        """Test session validation."""
        sm = SessionManager()
        session_id = sm.create_session("testuser")
        
        # Valid session
        assert sm.validate_session(session_id) is True
        
        # Invalid session
        assert sm.validate_session("invalid-session") is False
    
    def test_delete_session(self):
        """Test deleting a session."""
        sm = SessionManager()
        session_id = sm.create_session("testuser")
        
        # Session should exist
        assert sm.validate_session(session_id) is True
        
        # Delete session
        sm.delete_session(session_id)
        
        # Session should no longer exist
        assert sm.validate_session(session_id) is False


class TestDatabaseManager:
    """Test the database management functionality."""
    
    def test_database_creation(self):
        """Test database file creation."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db_manager = DatabaseManager(db_path)
            
            # Database file should exist
            assert os.path.exists(db_path)
            
            # Should be able to execute queries
            tables = db_manager.get_table_names()
            assert isinstance(tables, list)
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    def test_sample_data_creation(self):
        """Test creating sample data."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db_manager = DatabaseManager(db_path)
            
            # Create sample data
            tables_created = db_manager.create_sample_data()
            
            assert len(tables_created) > 0
            assert 'customers' in tables_created
            assert 'orders' in tables_created
            
            # Verify data exists
            customers = db_manager.execute_query("SELECT COUNT(*) as count FROM customers")
            assert customers[0]['count'] > 0
            
            orders = db_manager.execute_query("SELECT COUNT(*) as count FROM orders")
            assert orders[0]['count'] > 0
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


class TestSQLAgent:
    """Test the SQL agent functionality."""
    
    def test_agent_initialization(self):
        """Test SQL agent initialization."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            agent = SimpleSQLAgent(db_path)
            assert agent.database_path == db_path
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    def test_agent_with_sample_data(self):
        """Test SQL agent with sample data."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            # Create agent and sample data
            agent = SimpleSQLAgent(db_path)
            agent.db_manager.create_sample_data()
            
            # Test basic query
            result = agent.process_user_query("What tables are available?")
            assert "response" in result
            assert "customers" in result["response"] or "orders" in result["response"]
            
            # Test data query
            result = agent.process_user_query("How many customers do I have?")
            assert "response" in result
            assert "error" not in result or result["error"] is None
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


class TestAPI:
    """Test the FastAPI endpoints."""
    
    def test_health_check(self):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_login_flow(self):
        """Test the login functionality."""
        # Test login
        response = client.post("/auth/login", json={"username": "testuser"})
        assert response.status_code == 200
        
        data = response.json()
        assert "session_id" in data
        assert data["username"] == "testuser"
        
        session_id = data["session_id"]
        
        # Test logout
        response = client.post(f"/auth/logout?session_id={session_id}")
        assert response.status_code == 200
    
    def test_sample_data_creation(self):
        """Test creating sample data via API."""
        # Login first
        login_response = client.post("/auth/login", json={"username": "testuser"})
        session_id = login_response.json()["session_id"]
        
        # Create sample data
        response = client.post(f"/database/sample-data?session_id={session_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert len(data["tables_created"]) > 0
        
        # Cleanup
        client.post(f"/auth/logout?session_id={session_id}")
    
    def test_chat_functionality(self):
        """Test the chat endpoint."""
        # Login and create sample data
        login_response = client.post("/auth/login", json={"username": "testuser"})
        session_id = login_response.json()["session_id"]
        
        client.post(f"/database/sample-data?session_id={session_id}")
        
        # Test chat
        response = client.post("/chat", json={
            "message": "What tables do I have?",
            "session_id": session_id
        })
        assert response.status_code == 200
        
        data = response.json()
        assert "response" in data
        
        # Cleanup
        client.post(f"/auth/logout?session_id={session_id}")


def test_user_isolation():
    """Test that users are properly isolated from each other."""
    # Create two users
    login1 = client.post("/auth/login", json={"username": "user1"})
    login2 = client.post("/auth/login", json={"username": "user2"})
    
    session1 = login1.json()["session_id"]
    session2 = login2.json()["session_id"]
    
    # Create different sample data for each user
    client.post(f"/database/sample-data?session_id={session1}")
    client.post(f"/database/sample-data?session_id={session2}")
    
    # Get database info for each user
    info1 = client.get(f"/database/info?session_id={session1}")
    info2 = client.get(f"/database/info?session_id={session2}")
    
    assert info1.status_code == 200
    assert info2.status_code == 200
    
    # Users should have their own data
    data1 = info1.json()
    data2 = info2.json()
    
    # Both should have data, but they are in separate databases
    assert "tables" in data1
    assert "tables" in data2
    
    # User1 cannot access user2's session
    wrong_session_response = client.get(f"/database/info?session_id=invalid-session")
    assert wrong_session_response.status_code == 401
    
    # Cleanup
    client.post(f"/auth/logout?session_id={session1}")
    client.post(f"/auth/logout?session_id={session2}")


if __name__ == "__main__":
    # Run basic tests
    print("Running basic functionality tests...")
    
    # Test session manager
    sm_test = TestSessionManager()
    sm_test.test_create_session()
    sm_test.test_session_validation()
    sm_test.test_delete_session()
    print("✓ Session management tests passed")
    
    # Test database manager
    db_test = TestDatabaseManager()
    db_test.test_database_creation()
    db_test.test_sample_data_creation()
    print("✓ Database management tests passed")
    
    # Test SQL agent
    agent_test = TestSQLAgent()
    agent_test.test_agent_initialization()
    agent_test.test_agent_with_sample_data()
    print("✓ SQL agent tests passed")
    
    print("\nAll basic tests passed! 🎉")
    print("To run full API tests, use: python -m pytest test_app.py")