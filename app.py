from flask import Flask, render_template, request, redirect, url_for
from finance_tracker import add_transaction, view_transactions, generate_report, visualize_data

app = Flask(__name__)
# app.py

from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key

# Function to connect to the database
def get_db_connection():
    connection = sqlite3.connect('finance.db')
    connection.row_factory = sqlite3.Row
    return connection

# Route for home page
@app.route('/')
def index():
    return render_template('index.html')

# Route for registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            connection.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists.', 'danger')
        finally:
            cursor.close()
            connection.close()
    
    return render_template('register.html')

# Route for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Hash the password for comparison
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hashed_password))
        user = cursor.fetchone()
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
        
        cursor.close()
        connection.close()

    return render_template('login.html')


# Route for dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', user_id=session['user_id'], username=session['username'])

@app.route('/add', methods=['GET', 'POST'])
def add():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        type = request.form['type']
        category = request.form['category']
        amount = float(request.form['amount'])
        add_transaction(session['user_id'], type, category, amount)
        return redirect(url_for('dashboard'))
    return render_template('add_transaction.html')

@app.route('/transactions')
def transactions():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    transactions = view_transactions(session['user_id']).to_dict(orient='records')
    return render_template('transactions.html', transactions=transactions)


@app.route('/report')
def report():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    report = generate_report(session['user_id']).to_dict(orient='records')
    return render_template('report.html', report=report)


@app.route('/visualize')
def visualize():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    visualize_data(session['user_id'])
    return render_template('plot.html')


# Route for logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)











    


