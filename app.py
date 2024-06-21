from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Kvn@852456',
        database='diya',
        auth_plugin='mysql_native_password'
    )
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/customers')
def customer_list():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Customer')
    customers = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('customers.html', customers=customers)

@app.route('/transactions', methods=['GET', 'POST'])
def transactions():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Customer')
    customers = cursor.fetchall()

    # Fetch all transactions initially
    cursor.execute('SELECT * FROM Transaction')
    transactions = cursor.fetchall()

    if request.method == 'POST':
        from_customer = request.form['from_customer']
        to_customer = request.form['to_customer']
        amount = request.form['amount']

        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except ValueError as e:
            return render_template('transactions.html', customers=customers, transactions=transactions, error=str(e))

        cursor.execute('SELECT balance FROM Customer WHERE customer_id = %s', (from_customer,))
        from_balance = cursor.fetchone()['balance']

        if from_balance >= amount:
            cursor.execute('UPDATE Customer SET balance = balance - %s WHERE customer_id = %s', (amount, from_customer))
            cursor.execute('UPDATE Customer SET balance = balance + %s WHERE customer_id = %s', (amount, to_customer))
            cursor.execute('INSERT INTO Transaction (sender_id, receiver_id, transaction_amount) VALUES (%s, %s, %s)', (from_customer, to_customer, amount))
            conn.commit()

            # Update transactions after committing the new transaction
            cursor.execute('SELECT * FROM Transaction')
            transactions = cursor.fetchall()

            cursor.close()
            conn.close()

            return render_template('transactions.html', customers=customers, transactions=transactions)
        else:
            cursor.close()
            conn.close()
            return render_template('transactions.html', customers=customers, transactions=transactions, error="Insufficient balance")

    cursor.close()
    conn.close()
    return render_template('transactions.html', customers=customers, transactions=transactions)

@app.route('/customer/<int:customer_id>')
def customer_transactions(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Transaction WHERE sender_id = %s OR receiver_id = %s', (customer_id, customer_id))
    transactions = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('customer_transactions.html', transactions=transactions)

if __name__ == '__main__':
    app.run(debug=True)
