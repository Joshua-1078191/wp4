from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional
import sqlite3
import bcrypt
import re

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
def get_db():
    conn = sqlite3.connect('racademic.db')
    try:
        yield conn
    finally:
        conn.close()

# Create users table if it doesn't exist
def init_db():
    conn = sqlite3.connect('racademic.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            display_name TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT 0,
            is_blocked BOOLEAN DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    display_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Helper functions
def validate_hr_email(email: str) -> bool:
    return bool(re.match(r'^[a-zA-Z0-9._%+-]+@hr\.nl$', email))

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# Routes
@app.get("/")
def read_root():
    return {"message": "Welcome to RAcademic API"}

@app.post("/register")
def register(user: UserCreate, db: sqlite3.Connection = Depends(get_db)):
    # Validate HR email
    if not validate_hr_email(user.email):
        raise HTTPException(status_code=400, detail="Only @hr.nl email addresses are allowed")
    
    # Check if email is blocked
    cursor = db.cursor()
    cursor.execute("SELECT is_blocked FROM users WHERE email = ?", (user.email,))
    result = cursor.fetchone()
    if result and result[0]:
        raise HTTPException(status_code=400, detail="This email address is blocked")
    
    # Check if email already exists
    cursor.execute("SELECT id FROM users WHERE email = ?", (user.email,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password and create user
    hashed_password = hash_password(user.password)
    cursor.execute(
        "INSERT INTO users (email, password, display_name) VALUES (?, ?, ?)",
        (user.email, hashed_password, user.display_name)
    )
    db.commit()
    
    return {"message": "User registered successfully"}

@app.post("/login")
def login(user: UserLogin, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT id, password, is_blocked FROM users WHERE email = ?", (user.email,))
    result = cursor.fetchone()
    
    if not result:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    user_id, hashed_password, is_blocked = result
    
    if is_blocked:
        raise HTTPException(status_code=403, detail="This account is blocked")
    
    if not verify_password(user.password, hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    return {
        "message": "Login successful",
        "user_id": user_id,
        "email": user.email
    } 