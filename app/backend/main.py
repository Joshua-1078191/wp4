from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, constr
from typing import Optional, List
import sqlite3
import bcrypt
import re
import jwt
from datetime import datetime, timedelta

app = FastAPI()

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    conn = sqlite3.connect('racademic.db')
    try:
        yield conn
    finally:
        conn.close()

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

    c.execute('''
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            url TEXT,
            type TEXT NOT NULL,
            category TEXT,
            tags TEXT,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resource_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (resource_id) REFERENCES resources (id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(resource_id, user_id)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resource_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (resource_id) REFERENCES resources (id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(resource_id, user_id)
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

class ResourceCreate(BaseModel):
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    type: str  
    category: Optional[str] = None
    tags: Optional[str] = None

class ResourceResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    url: Optional[str]
    type: str
    category: Optional[str]
    tags: Optional[str]
    user_id: int
    user_display_name: str
    created_at: str
    average_rating: Optional[float]
    ratings_count: int
    is_favorited: bool
    favorites_count: int
    can_edit: bool
    can_delete: bool

class RatingCreate(BaseModel):
    rating: int  

class FavoriteToggle(BaseModel):
    resource_id: int

class NameUpdate(BaseModel):
    display_name: constr(min_length=1)

class PasswordUpdate(BaseModel):
    current_password: constr(min_length=1)
    new_password: constr(min_length=6)

class BlockEmailRequest(BaseModel):
    email: EmailStr
    reason: Optional[str] = None

class UnblockEmailRequest(BaseModel):
    email: EmailStr

class CreateAdminRequest(BaseModel):
    email: EmailStr
    password: str
    display_name: str

class BlockedEmailResponse(BaseModel):
    id: int
    email: str
    blocked_by: int
    blocked_at: str
    reason: Optional[str]
    blocked_by_name: str

class UserListResponse(BaseModel):
    id: int
    email: str
    display_name: str
    is_admin: bool
    is_blocked: bool

# Helper functions
def validate_hr_email(email: str) -> bool:
    return bool(re.match(r'^[a-zA-Z0-9._%+-]+@hr\.nl$', email))

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(authorization: Optional[str] = Header(None), db: sqlite3.Connection = Depends(get_db)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authorization scheme")
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        cursor = db.cursor()
        cursor.execute("SELECT id, email, display_name, is_blocked, is_admin FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        if user[3]:
            raise HTTPException(status_code=403, detail="Account is blocked")
        
        return {"id": user[0], "email": user[1], "display_name": user[2], "is_admin": user[4]}
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header")

def get_current_admin(current_user: dict = Depends(get_current_user)):
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# Routes
@app.get("/")
def read_root():
    return {"message": "Welcome to RAcademic API"}

@app.post("/register")
def register(user: UserCreate, db: sqlite3.Connection = Depends(get_db)):
    if not validate_hr_email(user.email):
        raise HTTPException(status_code=400, detail="Only @hr.nl email addresses are allowed")
    
    cursor = db.cursor()
    cursor.execute("SELECT is_blocked FROM users WHERE email = ?", (user.email,))
    result = cursor.fetchone()
    if result and result[0]:
        raise HTTPException(status_code=400, detail="This email address is blocked")
    
    cursor.execute("SELECT id FROM users WHERE email = ?", (user.email,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Email already registered")
    
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
    cursor.execute("SELECT id, password, is_blocked, display_name, is_admin FROM users WHERE email = ?", (user.email,))
    result = cursor.fetchone()
    
    if not result:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    user_id, hashed_password, is_blocked, display_name, is_admin = result
    
    if is_blocked:
        raise HTTPException(status_code=403, detail="This account is blocked")
    
    if not verify_password(user.password, hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"user_id": user_id}, expires_delta=access_token_expires
    )
    
    return {
        "message": "Login successful",
        "user_id": user_id,
        "email": user.email,
        "display_name": display_name,
        "is_admin": bool(is_admin),
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.post("/bronnen", response_model=ResourceResponse)
def create_resource(resource: ResourceCreate, current_user: dict = Depends(get_current_user), db: sqlite3.Connection = Depends(get_db)):
    user_id = current_user["id"]
    
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO resources (title, description, url, type, category, tags, user_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (resource.title, resource.description, resource.url, resource.type, resource.category, resource.tags, user_id)
    )
    db.commit()
    
    resource_id = cursor.lastrowid
    
    cursor.execute("SELECT display_name FROM users WHERE id = ?", (user_id,))
    user_display_name = cursor.fetchone()[0]
    
    return ResourceResponse(
        id=resource_id,
        title=resource.title,
        description=resource.description,
        url=resource.url,
        type=resource.type,
        category=resource.category,
        tags=resource.tags,
        user_id=user_id,
        user_display_name=user_display_name,
        created_at=str(cursor.execute("SELECT created_at FROM resources WHERE id = ?", (resource_id,)).fetchone()[0]),
        average_rating=None,
        ratings_count=0,
        is_favorited=False,
        favorites_count=0,
        can_edit=True,
        can_delete=True
    )

@app.get("/bronnen", response_model=list[ResourceResponse])
def get_resources(
    search: Optional[str] = None,
    type_filter: Optional[str] = None,
    category_filter: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db)
):
    cursor = db.cursor()
    user_id = current_user["id"]
    is_admin = current_user.get("is_admin", False)
    
    query = """
        SELECT r.id, r.title, r.description, r.url, r.type, r.category, r.tags, 
               r.user_id, r.created_at, u.display_name,
               AVG(rat.rating) as avg_rating,
               COUNT(DISTINCT rat.id) as ratings_count,
               COUNT(DISTINCT f.id) as favorites_count,
               CASE WHEN user_fav.id IS NOT NULL THEN 1 ELSE 0 END as is_favorited
        FROM resources r
        LEFT JOIN users u ON r.user_id = u.id
        LEFT JOIN ratings rat ON r.id = rat.resource_id
        LEFT JOIN favorites f ON r.id = f.resource_id
        LEFT JOIN favorites user_fav ON r.id = user_fav.resource_id AND user_fav.user_id = ?
    """
    
    params = [user_id]
    where_conditions = []
    
    if search:
        where_conditions.append("(r.title LIKE ? OR r.description LIKE ? OR r.tags LIKE ?)")
        search_param = f"%{search}%"
        params.extend([search_param, search_param, search_param])
    
    if type_filter:
        where_conditions.append("r.type = ?")
        params.append(type_filter)
    
    if category_filter:
        where_conditions.append("r.category = ?")
        params.append(category_filter)
    
    if where_conditions:
        query += " WHERE " + " AND ".join(where_conditions)
    
    query += " GROUP BY r.id ORDER BY r.created_at DESC"
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    
    resources = []
    for row in results:
        resource_user_id = row[7]
        can_edit = is_admin or resource_user_id == user_id
        can_delete = is_admin or resource_user_id == user_id
        
        resources.append(ResourceResponse(
            id=row[0],
            title=row[1],
            description=row[2],
            url=row[3],
            type=row[4],
            category=row[5],
            tags=row[6],
            user_id=resource_user_id,
            user_display_name=row[9],
            created_at=row[8],
            average_rating=row[10],
            ratings_count=row[11],
            is_favorited=bool(row[13]),
            favorites_count=row[12],
            can_edit=can_edit,
            can_delete=can_delete
        ))
    
    return resources

@app.post("/bronnen/{resource_id}/beoordeel")
def rate_resource(resource_id: int, rating: RatingCreate, current_user: dict = Depends(get_current_user), db: sqlite3.Connection = Depends(get_db)):
    user_id = current_user["id"]
    
    if not 1 <= rating.rating <= 5:
        raise HTTPException(status_code=400, detail="Beoordeling moet tussen 1 en 5 liggen")
    
    cursor = db.cursor()
    
    cursor.execute("SELECT id FROM resources WHERE id = ?", (resource_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Bron niet gevonden")
    
    cursor.execute(
        "INSERT OR REPLACE INTO ratings (resource_id, user_id, rating) VALUES (?, ?, ?)",
        (resource_id, user_id, rating.rating)
    )
    db.commit()
    
    return {"message": "Beoordeling succesvol bijgewerkt"}

@app.post("/bronnen/{resource_id}/favoriet")
def toggle_favorite(resource_id: int, current_user: dict = Depends(get_current_user), db: sqlite3.Connection = Depends(get_db)):
    user_id = current_user["id"]
    
    cursor = db.cursor()
    
    cursor.execute("SELECT id FROM resources WHERE id = ?", (resource_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Bron niet gevonden")
    
    cursor.execute("SELECT id FROM favorites WHERE resource_id = ? AND user_id = ?", (resource_id, user_id))
    existing = cursor.fetchone()
    
    if existing:
        cursor.execute("DELETE FROM favorites WHERE resource_id = ? AND user_id = ?", (resource_id, user_id))
        message = "Verwijderd uit favorieten"
    else:
        cursor.execute("INSERT INTO favorites (resource_id, user_id) VALUES (?, ?)", (resource_id, user_id))
        message = "Toegevoegd aan favorieten"
    
    db.commit()
    return {"message": message}

@app.put("/api/user/update-name")
def update_name(data: NameUpdate, current_user: dict = Depends(get_current_user), db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("UPDATE users SET display_name = ? WHERE id = ?", (data.display_name, current_user["id"]))
    db.commit()
    return {"message": "Naam succesvol bijgewerkt!"}

@app.put("/api/user/update-password")
def update_password(data: PasswordUpdate, current_user: dict = Depends(get_current_user), db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT password FROM users WHERE id = ?", (current_user["id"],))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Gebruiker niet gevonden")
    hashed_password = row[0]
    if not verify_password(data.current_password, hashed_password):
        raise HTTPException(status_code=400, detail="Huidig wachtwoord is onjuist")
    new_hashed = hash_password(data.new_password)
    cursor.execute("UPDATE users SET password = ? WHERE id = ?", (new_hashed, current_user["id"]))
    db.commit()
    return {"message": "Wachtwoord succesvol bijgewerkt!"}

@app.delete("/bronnen/{resource_id}")
def delete_resource(resource_id: int, current_user: dict = Depends(get_current_user), db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    
    # Check if resource exists
    cursor.execute("SELECT user_id FROM resources WHERE id = ?", (resource_id,))
    result = cursor.fetchone()
    if not result:
        raise HTTPException(status_code=404, detail="Bron niet gevonden")
    
    resource_user_id = result[0]
    current_user_id = current_user["id"]
    is_admin = current_user.get("is_admin", False)
    
    # Only allow deletion if user is admin or owns the resource
    if not is_admin and resource_user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Je kunt alleen je eigen bronnen verwijderen")
    
    # Delete related data first (ratings, favorites)
    cursor.execute("DELETE FROM ratings WHERE resource_id = ?", (resource_id,))
    cursor.execute("DELETE FROM favorites WHERE resource_id = ?", (resource_id,))
    
    # Delete the resource
    cursor.execute("DELETE FROM resources WHERE id = ?", (resource_id,))
    db.commit()
    
    return {"message": "Bron succesvol verwijderd"}

@app.put("/bronnen/{resource_id}")
def update_resource(resource_id: int, resource: ResourceCreate, current_user: dict = Depends(get_current_user), db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    
    # Check if resource exists
    cursor.execute("SELECT user_id FROM resources WHERE id = ?", (resource_id,))
    result = cursor.fetchone()
    if not result:
        raise HTTPException(status_code=404, detail="Bron niet gevonden")
    
    resource_user_id = result[0]
    current_user_id = current_user["id"]
    is_admin = current_user.get("is_admin", False)
    
    # Only allow editing if user owns the resource or is admin
    if not is_admin and resource_user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Je kunt alleen je eigen bronnen bewerken")
    
    # Update the resource
    cursor.execute(
        "UPDATE resources SET title = ?, description = ?, url = ?, type = ?, category = ?, tags = ? WHERE id = ?",
        (resource.title, resource.description, resource.url, resource.type, resource.category, resource.tags, resource_id)
    )
    db.commit()
    
    return {"message": "Bron succesvol bijgewerkt"}

# Admin endpoints
@app.post("/admin/block-email")
def block_email(
    request: BlockEmailRequest, 
    current_admin: dict = Depends(get_current_admin), 
    db: sqlite3.Connection = Depends(get_db)
):
    # Validate HR email
    if not validate_hr_email(request.email):
        raise HTTPException(status_code=400, detail="Only @hr.nl email addresses can be blocked")
    
    cursor = db.cursor()
    
    # Check if email is already blocked
    cursor.execute("SELECT id FROM blocked_emails WHERE email = ?", (request.email,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Email is already blocked")
    
    # Check if email exists as a user
    cursor.execute("SELECT id FROM users WHERE email = ?", (request.email,))
    user = cursor.fetchone()
    if user:
        # Block the existing user
        cursor.execute("UPDATE users SET is_blocked = 1 WHERE email = ?", (request.email,))
    
    # Add to blocked_emails table
    cursor.execute(
        "INSERT INTO blocked_emails (email, blocked_by, reason) VALUES (?, ?, ?)",
        (request.email, current_admin["id"], request.reason)
    )
    
    db.commit()
    return {"message": f"Email {request.email} has been blocked successfully"}

@app.post("/admin/unblock-email")
def unblock_email(
    request: UnblockEmailRequest, 
    current_admin: dict = Depends(get_current_admin), 
    db: sqlite3.Connection = Depends(get_db)
):
    cursor = db.cursor()
    
    # Remove from blocked_emails table
    cursor.execute("DELETE FROM blocked_emails WHERE email = ?", (request.email,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Email is not blocked")
    
    # Unblock user if they exist
    cursor.execute("UPDATE users SET is_blocked = 0 WHERE email = ?", (request.email,))
    
    db.commit()
    return {"message": f"Email {request.email} has been unblocked successfully"}

@app.get("/admin/blocked-emails", response_model=list[BlockedEmailResponse])
def get_blocked_emails(
    current_admin: dict = Depends(get_current_admin), 
    db: sqlite3.Connection = Depends(get_db)
):
    cursor = db.cursor()
    cursor.execute("""
        SELECT be.id, be.email, be.blocked_by, be.blocked_at, be.reason, u.display_name
        FROM blocked_emails be
        LEFT JOIN users u ON be.blocked_by = u.id
        ORDER BY be.blocked_at DESC
    """)
    
    results = cursor.fetchall()
    blocked_emails = []
    for row in results:
        blocked_emails.append(BlockedEmailResponse(
            id=row[0],
            email=row[1],
            blocked_by=row[2],
            blocked_at=row[3],
            reason=row[4],
            blocked_by_name=row[5] or "Unknown"
        ))
    
    return blocked_emails

@app.post("/admin/create-admin")
def create_admin(
    request: CreateAdminRequest, 
    current_admin: dict = Depends(get_current_admin), 
    db: sqlite3.Connection = Depends(get_db)
):
    # Validate HR email
    if not validate_hr_email(request.email):
        raise HTTPException(status_code=400, detail="Only @hr.nl email addresses are allowed for admin accounts")
    
    cursor = db.cursor()
    
    # Check if email is blocked
    cursor.execute("SELECT id FROM blocked_emails WHERE email = ?", (request.email,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="This email address is blocked")
    
    # Check if email already exists
    cursor.execute("SELECT id FROM users WHERE email = ?", (request.email,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password and create admin user
    hashed_password = hash_password(request.password)
    cursor.execute(
        "INSERT INTO users (email, password, display_name, is_admin) VALUES (?, ?, ?, ?)",
        (request.email, hashed_password, request.display_name, True)
    )
    db.commit()
    
    return {"message": f"Admin account created successfully for {request.email}"}

@app.get("/admin/users", response_model=List[UserListResponse])
def get_all_users(current_admin: dict = Depends(get_current_admin), db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT id, email, display_name, is_admin, is_blocked FROM users ORDER BY is_admin DESC, is_blocked DESC, email ASC")
    users = [
        UserListResponse(
            id=row[0],
            email=row[1],
            display_name=row[2],
            is_admin=bool(row[3]),
            is_blocked=bool(row[4])
        )
        for row in cursor.fetchall()
    ]
    return users 