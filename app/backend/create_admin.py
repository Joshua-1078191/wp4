import os
import sqlite3
import bcrypt
import getpass

DB_PATH = 'racademic.db'

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_dummy_admin():
    email = 'admin@hr.nl'
    display_name = 'Admin'
    password = 'admin123'
    hashed = hash_password(password)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE email = ?', (email,))
    if c.fetchone():
        print('Dummy admin already exists.')
        conn.close()
        return
    c.execute('INSERT INTO users (email, password, display_name, is_admin) VALUES (?, ?, ?, ?)',
              (email, hashed, display_name, 1))
    conn.commit()
    conn.close()
    print('Dummy admin user created:')
    print(f'  Email: {email}')
    print(f'  Password: {password}')
    print(f'  Display name: {display_name}')

def main():
    create_dummy_admin()

if __name__ == '__main__':
    main() 