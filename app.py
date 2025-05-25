from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
import hashlib
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a random string in production

# Database helper functions
def get_db_connection():
    conn = sqlite3.connect('businesses.db')
    conn.row_factory = sqlite3.Row
    return conn

# Authentication helper functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Route for home page
@app.route('/')
def index():
    return render_template('index.html')

# Authentication routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        is_business_owner = 'is_business_owner' in request.form
        
        # Form validation
        if not all([username, email, password, confirm_password]):
            flash('All fields are required', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
        
        # Check if username or email already exists
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? OR email = ?', 
                           (username, email)).fetchone()
        
        if user:
            conn.close()
            flash('Username or email already exists', 'danger')
            return render_template('register.html')
        
        # Insert new user
        try:
            password_hash = hash_password(password)
            conn.execute('INSERT INTO users (username, email, password_hash, is_business_owner) VALUES (?, ?, ?, ?)',
                       (username, email, password_hash, 1 if is_business_owner else 0))
            conn.commit()
            conn.close()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            conn.close()
            flash(f'An error occurred: {str(e)}', 'danger')
            return render_template('register.html')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if not all([username, password]):
            flash('Both username and password are required', 'danger')
            return render_template('login.html')
        
        # Verify credentials
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and user['password_hash'] == hash_password(password):
            # Set user session
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_business_owner'] = user['is_business_owner']
            
            flash(f'Welcome back, {username}!', 'success')
            next_page = request.args.get('next', url_for('index'))
            return redirect(next_page)
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    
    return render_template('profile.html', user=user)

# API Routes
@app.route('/api/categories')
def get_categories():
    conn = get_db_connection()
    categories = conn.execute('SELECT * FROM categories').fetchall()
    conn.close()
    
    # Convert to list of dictionaries
    return jsonify([{'id': category['id'], 'name': category['name']} for category in categories])

@app.route('/api/businesses')
def get_businesses():
    category_id = request.args.get('category_id')
    search_query = request.args.get('search', '')
    
    conn = get_db_connection()
    
    if category_id and search_query:
        # Filter by both category and search term
        businesses = conn.execute('''
            SELECT b.*, c.name as category_name 
            FROM businesses b
            JOIN categories c ON b.category_id = c.id
            WHERE b.category_id = ? AND (b.name LIKE ? OR b.description LIKE ?)
        ''', (category_id, f'%{search_query}%', f'%{search_query}%')).fetchall()
    elif category_id:
        # Filter by category only
        businesses = conn.execute('''
            SELECT b.*, c.name as category_name 
            FROM businesses b
            JOIN categories c ON b.category_id = c.id
            WHERE b.category_id = ?
        ''', (category_id,)).fetchall()
    elif search_query:
        # Filter by search term only
        businesses = conn.execute('''
            SELECT b.*, c.name as category_name 
            FROM businesses b
            JOIN categories c ON b.category_id = c.id
            WHERE b.name LIKE ? OR b.description LIKE ?
        ''', (f'%{search_query}%', f'%{search_query}%')).fetchall()
    else:
        # Get all businesses
        businesses = conn.execute('''
            SELECT b.*, c.name as category_name 
            FROM businesses b
            JOIN categories c ON b.category_id = c.id
        ''').fetchall()
    
    conn.close()
    
    # Convert to list of dictionaries
    return jsonify([{
        'id': business['id'],
        'name': business['name'],
        'category_id': business['category_id'],
        'category_name': business['category_name'],
        'description': business['description'],
        'address': business['address'],
        'phone': business['phone'],
        'email': business['email'],
        'website': business['website'],
        'image_url': business['image_url']
    } for business in businesses])

@app.route('/api/businesses/<int:business_id>')
def get_business(business_id):
    conn = get_db_connection()
    business = conn.execute('''
        SELECT b.*, c.name as category_name 
        FROM businesses b
        JOIN categories c ON b.category_id = c.id
        WHERE b.id = ?
    ''', (business_id,)).fetchone()
    conn.close()
    
    if business is None:
        return jsonify({'error': 'Business not found'}), 404
    
    return jsonify({
        'id': business['id'],
        'name': business['name'],
        'category_id': business['category_id'],
        'category_name': business['category_name'],
        'description': business['description'],
        'address': business['address'],
        'phone': business['phone'],
        'email': business['email'],
        'website': business['website'],
        'image_url': business['image_url']
    })

@app.route('/business/<int:business_id>')
def business_details(business_id):
    return render_template('business_details.html', business_id=business_id)

if __name__ == '__main__':
    # Check if the database exists, if not create it
    if not os.path.exists('businesses.db'):
        from schema import create_tables
        create_tables()
    
    app.run(debug=True)