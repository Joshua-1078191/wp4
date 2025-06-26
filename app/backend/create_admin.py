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
    import sys
    if '--dummy' in sys.argv:
        create_dummy_admin()
        return
    email = input('Admin email (@hr.nl): ').strip()
    if not email.endswith('@hr.nl'):
        print('Email must be an @hr.nl address.')
        return
    display_name = input('Display name: ').strip()
    password = getpass.getpass('Password: ')
    password2 = getpass.getpass('Repeat password: ')
    if password != password2:
        print('Passwords do not match.')
        return
    hashed = hash_password(password)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE email = ?', (email,))
    if c.fetchone():
        print('A user with this email already exists.')
        conn.close()
        return
    c.execute('INSERT INTO users (email, password, display_name, is_admin) VALUES (?, ?, ?, ?)',
              (email, hashed, display_name, 1))
    conn.commit()
    conn.close()
    print('Admin user created successfully!')

if __name__ == '__main__':
    main() 