import sqlite3
import hashlib

def hash_password(password):
    # A simple password hashing function
    return hashlib.sha256(password.encode()).hexdigest()

def create_tables():
    # Connect to SQLite database (creates it if it doesn't exist)
    conn = sqlite3.connect('businesses.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        is_business_owner BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create business categories table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE
    )
    ''')
    
    # Create businesses table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS businesses (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        category_id INTEGER,
        description TEXT,
        address TEXT,
        phone TEXT,
        email TEXT,
        website TEXT,
        image_url TEXT,
        FOREIGN KEY (category_id) REFERENCES categories (id)
    )
    ''')
    
    # Insert some sample categories
    categories = [
        ('Fashion',),
        ('Food',),
        ('Services',),
        ('Health',),
        ('Technology',)
    ]
    
    cursor.executemany('INSERT OR IGNORE INTO categories (name) VALUES (?)', categories)
    
    # Insert some sample businesses
    businesses = [
        ('Kashmir Pashmina Store', 1, 'Authentic Kashmiri Pashmina shawls and clothing', 
         'Lal Chowk, Srinagar', '+91 9876543210', 'info@kashmirpashmina.com', 
         'www.kashmirpashmina.com', 'pashmina.jpg'),
        
        ('Wazwan Delights', 2, 'Traditional Kashmiri Wazwan cuisine', 
         'Residency Road, Srinagar', '+91 9876543211', 'info@wazwandelights.com', 
         'www.wazwandelights.com', 'wazwan.jpg'),
        
        ('Kashmir Tours & Travels', 3, 'Local travel agency for Kashmir tourism', 
         'Dal Gate, Srinagar', '+91 9876543212', 'info@kashmirtours.com', 
         'www.kashmirtours.com', 'tours.jpg'),
         
        ('Himalayan Herbs', 4, 'Traditional herbal medicine and wellness products', 
         'Karan Nagar, Srinagar', '+91 9876543213', 'info@himalayanherbs.com', 
         'www.himalayanherbs.com', 'herbs.jpg'),
        
        ('Digital Valley', 5, 'IT services and software development', 
         'Rajbagh, Srinagar', '+91 9876543214', 'info@digitalvalley.com', 
         'www.digitalvalley.com', 'digital.jpg')
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO businesses 
        (name, category_id, description, address, phone, email, website, image_url) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', businesses)
    
    # Insert some sample users
    sample_users = [
        ('john_doe', 'john@example.com', hash_password('password123'), 0),
        ('business_owner', 'owner@example.com', hash_password('owner123'), 1)
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO users 
        (username, email, password_hash, is_business_owner) 
        VALUES (?, ?, ?, ?)
    ''', sample_users)
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("Database created successfully with sample data!")

if __name__ == "__main__":
    create_tables()