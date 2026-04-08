from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, List
import sqlite3
import json
from datetime import datetime
from auth.auth_service import AuthService
from auth.password_utils import PasswordManager
from config import ACTIVE_CONFIG
from realtime_dynamic_v2 import RealTimeDynamicProcessor  # IMPROVED VERSION
import os

app = FastAPI(title="Student Portal API v2", version="2.0.0")

# Serve static files
app.mount("/static", StaticFiles(directory="templates"), name="static")

# Database configuration
DB_PATH = ACTIVE_CONFIG.DATABASE_PATH
DATA_TABLE = ACTIVE_CONFIG.DATA_TABLE
ID_COLUMN = ACTIVE_CONFIG.USER_ID_COLUMN
auth_service = AuthService(DB_PATH)

# Initialize REAL-TIME dynamic processor (loads headers at request time)
def get_processor():
    """Get real-time processor - loads columns fresh each time"""
    return RealTimeDynamicProcessor(DB_PATH, DATA_TABLE, ID_COLUMN)

# ==================== PYDANTIC MODELS ====================

class LoginRequest(BaseModel):
    register_number: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict

class RegisterRequest(BaseModel):
    register_number: str
    password: str
    full_name: str
    email: str

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    intent: str
    data: Optional[Dict] = None

# ==================== AUTHENTICATION ====================

def verify_token(token: str) -> dict:
    """Verify JWT token"""
    if not token.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format"
        )
    
    token = token.replace("Bearer ", "")
    payload = auth_service.verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired or invalid"
        )
    
    return payload

async def get_current_user(request: Request) -> dict:
    """Get current authenticated user from Authorization header"""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token"
        )
    
    return verify_token(auth_header)

# ==================== AUTH ENDPOINTS ====================

@app.post("/api/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Login endpoint"""
    user = auth_service.login(request.register_number, request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid register number or password"
        )
    
    access_token, expires_in = auth_service.create_access_token(
        user_id=1,  # Simplified for now
        register_number=user['register_number']
    )
    
    return LoginResponse(
        access_token=access_token,
        expires_in=expires_in,
        user=user
    )

@app.post("/api/register")
async def register(request: RegisterRequest):
    """Register new user"""
    success = auth_service.register_user(
        register_number=request.register_number,
        password=request.password,
        full_name=request.full_name,
        email=request.email
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Register number already exists"
        )
    
    return {"message": "User registered successfully"}

# ==================== CHAT ENDPOINT ====================

def get_student_data(register_number: str) -> Dict:
    """Get student data from database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Use config to find the correct column
        id_column = ACTIVE_CONFIG.USER_ID_COLUMN
        cursor.execute(f"SELECT * FROM {DATA_TABLE} WHERE {id_column} = ?", (register_number,))
        record = cursor.fetchone()
        
        if record:
            return dict(record)
        return None
    finally:
        conn.close()

def process_intent(message: str, user_data: Dict, register_number: str) -> tuple:
    """
    Dynamic intent classification using REAL-TIME schema discovery.
    Works with any dataset automatically - loads columns at request time.
    """
    # Use the real-time dynamic processor
    processor = get_processor()
    response, matched_intent = processor.process_query(
        message, 
        user_data if user_data else {}
    )[:2]  # Get only response and column name
    
    return response, matched_intent

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    """Chat endpoint - process queries using REAL-TIME dynamic intent system"""
    register_number = current_user.get('register_number')
    
    # Get user data
    user_data = get_student_data(register_number)
    
    # Get REAL-TIME processor (loads headers from database each request)
    processor = get_processor()
    
    # Process query against ALL available columns in database
    response, matched_column, confidence = processor.process_query(
        request.message, 
        user_data
    )
    
    return ChatResponse(
        response=response,
        intent=matched_column,  # This is now the actual matched column name
        data=user_data
    )

# ==================== DATA ENDPOINTS ====================

@app.get("/api/user/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    register_number = current_user.get('register_number')
    student_data = get_student_data(register_number)
    
    if not student_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    return {
        "register_number": register_number,
        "user": current_user,
        "academic_data": student_data
    }

@app.get("/api/user/data/{column}")
async def get_column_data(column: str, current_user: dict = Depends(get_current_user)):
    """Get specific column data"""
    register_number = current_user.get('register_number')
    student_data = get_student_data(register_number)
    
    if not student_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    if column not in student_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Column '{column}' not found"
        )
    
    return {
        "column": column,
        "value": student_data.get(column)
    }

# ==================== FILE SERVING ====================

@app.get("/")
async def serve_root():
    """Serve login page as root"""
    return FileResponse("templates/login.html", media_type="text/html")

@app.get("/login.html")
async def serve_login():
    """Serve login page"""
    return FileResponse("templates/login.html", media_type="text/html")

@app.get("/dashboard.html")
async def serve_dashboard():
    """Serve dashboard page"""
    return FileResponse("templates/dashboard.html", media_type="text/html")

# ==================== HEALTH CHECK ====================

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "online",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/schema")
async def get_schema():
    """Get available schema and columns for current dataset (REAL-TIME discovery)"""
    processor = get_processor()
    columns = processor.get_all_columns()
    
    return {
        "database": DB_PATH,
        "table": DATA_TABLE,
        "columns": columns,
        "total_columns": len(columns),
        "queryable_columns": processor.get_queryable_columns(),
        "total_queryable": len(processor.get_queryable_columns())
    }

@app.get("/api/intents")
async def get_available_intents():
    """Get all available intents based on REAL-TIME column discovery"""
    processor = get_processor()
    
    # Get all possible queries for every column
    all_queries = processor.get_all_possible_queries()
    sample_queries = processor.get_sample_queries(limit=10)
    
    return {
        "all_intents": all_queries,
        "total_intents": len(all_queries),
        "sample_queries": sample_queries,
        "info": "You can query any column by asking about it in natural language"
    }

@app.get("/api/all-queries")
async def get_all_possible_queries():
    """Get ALL possible queries user can make (for guidance)"""
    processor = get_processor()
    all_queries = processor.get_all_possible_queries()
    queryable = processor.get_queryable_columns()
    
    return {
        "all_possible_queries": all_queries,
        "total_queryable_columns": len(queryable),
        "queryable_columns": queryable,
        "message": f"You can ask about any of these {len(queryable)} columns in any way you like"
    }

if __name__ == "__main__":
    import uvicorn
    
    # Initialize database
    from database_init import initialize_database
    initialize_database()
    
    print("\n" + "="*60)
    print("[*] Student Portal API v2 Starting...")
    print("="*60)
    print("[+] Authentication enabled")
    print("[+] Database initialized")
    print("[+] JWT tokens active")
    print("[+] REAL-TIME Dynamic Intent System enabled")
    print("="*60)
    print("\n[INFO] Test Login Credentials:")
    print("   Register: DEMO001")
    print("   Password: demo@123")
    print("\n[INFO] All columns are automatically queryable!")
    print("[INFO] Access at: http://localhost:8000")
    print("="*60 + "\n")
    
    try:
        uvicorn.run(app, host="127.0.0.1", port=8000)
    except OSError:
        print("Port 8000 is busy, trying 8001...")
        uvicorn.run(app, host="127.0.0.1", port=8001)
