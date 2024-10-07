import sqlite3
import pandas as pd 
import matplotlib.pyplot as plt
from datetime import datetime


# Connect to the database
def connect_db():
    return sqlite3.connect('finance.db')

# Add a new transaction (income or expense)
def add_transaction(user_id, type, category, amount):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO transactions (user_id, type, category, amount, date)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, type, category, amount, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()

# View all transactions
def view_transactions(user_id):
    conn = connect_db()
    df = pd.read_sql_query('SELECT * FROM transactions WHERE user_id = ?', conn, params=(user_id,))
    conn.close()
    return df

# Generate a report for income and expenses
def generate_report(user_id):
    df = view_transactions(user_id)
    report = df.groupby(['type', 'category'])['amount'].sum().reset_index()
    return report
   
# Visualize expenses vs income using a barchart

def visualize_data(user_id):
    df = view_transactions(user_id)
    print("DataFrame fetched:", df)  # Debugging: Check fetched data

    # Grouping expenses and income
    expenses = df[df['type'] == 'expense'].groupby('category')['amount'].sum()
    income = df[df['type'] == 'income'].groupby('category')['amount'].sum()

    print("Grouped Expenses:", expenses)  # Debugging: Check grouped expenses
    print("Grouped Income:", income)  # Debugging: Check grouped income

    # Check if there are any expenses or income to visualize
    if expenses.empty and income.empty:
        print("No data to visualize.")  # Handle no data
        return None

    # Create a combined DataFrame for better visualization
    combined = pd.DataFrame({'Income': income, 'Expenses': expenses}).fillna(0)

    # Plotting
    combined.plot(kind='bar', figsize=(10, 6))
    plt.title('Income and Expenses by Category')
    plt.xlabel('Category')
    plt.ylabel('Amount')
    plt.xticks(rotation=45)
    plt.legend(loc='upper right')

    # Save the bar chart
    filename = f'static/income_expenses_chart_{user_id}.png'
    plt.savefig(filename)
    print("Bar chart saved successfully.")  # Confirm save
    plt.close()  # Close the plot

    return filename  # Return the path of the saved image




   