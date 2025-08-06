"""
Data models and schemas for the multi-user SQL agent application.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class User(BaseModel):
    """User model for session management."""
    username: str = Field(..., min_length=1, max_length=50, description="Unique username")
    session_id: str = Field(..., description="Session identifier")
    created_at: datetime = Field(default_factory=datetime.now)
    database_path: str = Field(..., description="Path to user's database file")


class ChatMessage(BaseModel):
    """Chat message model."""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., min_length=1, description="User message")
    session_id: str = Field(..., description="Session identifier")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str = Field(..., description="Agent response")
    query_executed: Optional[str] = Field(None, description="SQL query that was executed")
    results: Optional[List[Dict[str, Any]]] = Field(None, description="Query results")
    error: Optional[str] = Field(None, description="Error message if any")


class LoginRequest(BaseModel):
    """Request model for login endpoint."""
    username: str = Field(..., min_length=1, max_length=50)


class LoginResponse(BaseModel):
    """Response model for login endpoint."""
    session_id: str = Field(..., description="Session identifier")
    username: str = Field(..., description="Username")
    message: str = Field(..., description="Login status message")


class DatabaseSchema(BaseModel):
    """Database schema information."""
    tables: List[str] = Field(..., description="List of table names")
    table_schemas: Dict[str, List[Dict[str, str]]] = Field(..., description="Schema for each table")


class UploadResponse(BaseModel):
    """Response model for file upload."""
    success: bool = Field(..., description="Upload success status")
    message: str = Field(..., description="Status message")
    tables_created: List[str] = Field(default_factory=list, description="Names of tables created")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")