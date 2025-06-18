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

class RatingCreate(BaseModel):
    rating: int  

class FavoriteToggle(BaseModel):
    resource_id: int

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


@app.post("/bronnen", response_model=ResourceResponse)
def create_resource(resource: ResourceCreate, db: sqlite3.Connection = Depends(get_db)):
    user_id = 1  
    
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
        favorites_count=0
    )

@app.get("/bronnen", response_model=list[ResourceResponse])
def get_resources(
    search: Optional[str] = None,
    type_filter: Optional[str] = None,
    category_filter: Optional[str] = None,
    db: sqlite3.Connection = Depends(get_db)
):
    cursor = db.cursor()
    
    query = """
        SELECT r.id, r.title, r.description, r.url, r.type, r.category, r.tags, 
               r.user_id, r.created_at, u.display_name,
               AVG(rat.rating) as avg_rating,
               COUNT(DISTINCT rat.id) as ratings_count,
               COUNT(DISTINCT f.id) as favorites_count
        FROM resources r
        LEFT JOIN users u ON r.user_id = u.id
        LEFT JOIN ratings rat ON r.id = rat.resource_id
        LEFT JOIN favorites f ON r.id = f.resource_id
    """
    
    params = []
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
        resources.append(ResourceResponse(
            id=row[0],
            title=row[1],
            description=row[2],
            url=row[3],
            type=row[4],
            category=row[5],
            tags=row[6],
            user_id=row[7],
            user_display_name=row[9],
            created_at=row[8],
            average_rating=row[10],
            ratings_count=row[11],
            is_favorited=False,  
            favorites_count=row[12]
        ))
    
    return resources

@app.post("/bronnen/{resource_id}/beoordeel")
def rate_resource(resource_id: int, rating: RatingCreate, db: sqlite3.Connection = Depends(get_db)):
    user_id = 1  
    
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
def toggle_favorite(resource_id: int, db: sqlite3.Connection = Depends(get_db)):
    user_id = 1  
    
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