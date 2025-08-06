"""
Main FastAPI application for the multi-user SQL agent web app.
"""
import os
import tempfile
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn

# Import our modules
from models import (
    LoginRequest, LoginResponse, ChatRequest, ChatResponse,
    DatabaseSchema, UploadResponse, ErrorResponse
)
from auth import session_manager
from database import DatabaseManager
from sql_agent import SimpleSQLAgent


# Create FastAPI app
app = FastAPI(
    title="Multi-User SQL Agent",
    description="A multi-user web application for natural language database queries using LangGraph",
    version="1.0.0"
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Store active SQL agents per session
active_agents: Dict[str, SimpleSQLAgent] = {}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main web interface."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Create or resume a user session."""
    try:
        # Create new session
        session_id = session_manager.create_session(request.username)
        
        # Get user info
        user = session_manager.get_user(session_id)
        if not user:
            raise HTTPException(status_code=500, detail="Failed to create session")
        
        # Initialize SQL agent for this user
        agent = SimpleSQLAgent(user.database_path)
        active_agents[session_id] = agent
        
        return LoginResponse(
            session_id=session_id,
            username=user.username,
            message=f"Welcome {user.username}! Your session has been created."
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/auth/logout")
async def logout(session_id: str):
    """End a user session."""
    try:
        # Remove agent
        if session_id in active_agents:
            del active_agents[session_id]
        
        # Delete session
        success = session_manager.delete_session(session_id)
        
        if success:
            return {"message": "Session ended successfully"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a chat message and return agent response."""
    try:
        # Validate session
        user = session_manager.get_user(request.session_id)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid or expired session")
        
        # Get SQL agent for this session
        if request.session_id not in active_agents:
            # Recreate agent if not found
            agent = SimpleSQLAgent(user.database_path)
            active_agents[request.session_id] = agent
        else:
            agent = active_agents[request.session_id]
        
        # Process the user query
        result = agent.process_user_query(request.message)
        
        return ChatResponse(
            response=result["response"],
            query_executed=result.get("query_executed"),
            results=result.get("results"),
            error=result.get("error")
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/database/schema", response_model=DatabaseSchema)
async def get_database_schema(session_id: str):
    """Get the current database schema for a user."""
    try:
        # Validate session
        user = session_manager.get_user(session_id)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid or expired session")
        
        # Get database manager
        db_manager = DatabaseManager(user.database_path)
        schema = db_manager.get_database_schema()
        
        return schema
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/database/upload", response_model=UploadResponse)
async def upload_data(session_id: str, file: UploadFile = File(...)):
    """Upload CSV data to create database tables."""
    try:
        # Validate session
        user = session_manager.get_user(session_id)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid or expired session")
        
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # Get database manager
            db_manager = DatabaseManager(user.database_path)
            
            # Upload data
            tables_created = db_manager.upload_csv_data(tmp_file_path)
            
            return UploadResponse(
                success=True,
                message=f"Successfully uploaded data and created tables: {', '.join(tables_created)}",
                tables_created=tables_created
            )
        
        finally:
            # Clean up temporary file
            os.unlink(tmp_file_path)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/database/sample-data", response_model=UploadResponse)
async def create_sample_data(session_id: str):
    """Create sample data for demonstration."""
    try:
        # Validate session
        user = session_manager.get_user(session_id)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid or expired session")
        
        # Get database manager
        db_manager = DatabaseManager(user.database_path)
        
        # Create sample data
        tables_created = db_manager.create_sample_data()
        
        return UploadResponse(
            success=True,
            message=f"Successfully created sample data with tables: {', '.join(tables_created)}",
            tables_created=tables_created
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/database/info")
async def get_database_info(session_id: str):
    """Get detailed database information."""
    try:
        # Validate session
        user = session_manager.get_user(session_id)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid or expired session")
        
        # Get SQL agent for this session
        if session_id not in active_agents:
            agent = SimpleSQLAgent(user.database_path)
            active_agents[session_id] = agent
        else:
            agent = active_agents[session_id]
        
        # Get database info
        info = agent.get_database_info()
        
        return info
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "active_sessions": session_manager.get_active_sessions_count(),
        "active_agents": len(active_agents)
    }


if __name__ == "__main__":
    # Ensure required directories exist
    os.makedirs("user_databases", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    os.makedirs("templates", exist_ok=True)
    
    # Run the application
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )