from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Tworzenie bazy danych SQLite
conn = sqlite3.connect('budget_management.db', check_same_thread=False)
c = conn.cursor()

# Tworzenie tabeli dla wpłat
c.execute('''CREATE TABLE IF NOT EXISTS incomes
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              amount REAL NOT NULL,
              date TEXT NOT NULL)''')
conn.commit()

# Tworzenie tabeli dla wydatków
c.execute('''CREATE TABLE IF NOT EXISTS expenses
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              category TEXT NOT NULL,
              amount REAL NOT NULL,
              date TEXT NOT NULL)''')
conn.commit()

def get_db_connection():
    conn = sqlite3.connect('budget_management.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/incomes', methods=['GET', 'POST'])
def incomes():
    conn = get_db_connection()
    if request.method == 'POST':
        amount = request.form['amount']
        date = request.form['date']
        if amount and date:
            conn.execute("INSERT INTO incomes (amount, date) VALUES (?, ?)", (amount, date))
            conn.commit()
            flash('Wpłata dodana pomyślnie!')
        else:
            flash('Wypełnij wszystkie pola!')
        return redirect(url_for('incomes'))
    incomes = conn.execute("SELECT * FROM incomes").fetchall()
    conn.close()
    return render_template('incomes.html', incomes=incomes)

@app.route('/edit_income/<int:id>', methods=['GET', 'POST'])
def edit_income(id):
    conn = get_db_connection()
    income = conn.execute("SELECT * FROM incomes WHERE id = ?", (id,)).fetchone()
    if request.method == 'POST':
        amount = request.form['amount']
        date = request.form['date']
        if amount and date:
            conn.execute("UPDATE incomes SET amount = ?, date = ? WHERE id = ?", (amount, date, id))
            conn.commit()
            flash('Wpłata zaktualizowana pomyślnie!')
            return redirect(url_for('incomes'))
        else:
            flash('Wypełnij wszystkie pola!')
    conn.close()
    return render_template('edit_income.html', income=income)

@app.route('/delete_income/<int:id>')
def delete_income(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM incomes WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash('Wpłata usunięta pomyślnie!')
    return redirect(url_for('incomes'))

@app.route('/expenses', methods=['GET', 'POST'])
def expenses():
    conn = get_db_connection()
    if request.method == 'POST':
        category = request.form['category']
        amount = request.form['amount']
        date = request.form['date']
        if category and amount and date:
            conn.execute("INSERT INTO expenses (category, amount, date) VALUES (?, ?, ?)", (category, amount, date))
            conn.commit()
            flash('Wydatek dodany pomyślnie!')
        else:
            flash('Wypełnij wszystkie pola!')
        return redirect(url_for('expenses'))
    expenses = conn.execute("SELECT * FROM expenses").fetchall()
    conn.close()
    return render_template('expenses.html', expenses=expenses)

@app.route('/edit_expense/<int:id>', methods=['GET', 'POST'])
def edit_expense(id):
    conn = get_db_connection()
    expense = conn.execute("SELECT * FROM expenses WHERE id = ?", (id,)).fetchone()
    if request.method == 'POST':
        category = request.form['category']
        amount = request.form['amount']
        date = request.form['date']
        if category and amount and date:
            conn.execute("UPDATE expenses SET category = ?, amount = ?, date = ? WHERE id = ?", (category, amount, date, id))
            conn.commit()
            flash('Wydatek zaktualizowany pomyślnie!')
            return redirect(url_for('expenses'))
        else:
            flash('Wypełnij wszystkie pola!')
    conn.close()
    return render_template('edit_expense.html', expense=expense)

@app.route('/delete_expense/<int:id>')
def delete_expense(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM expenses WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash('Wydatek usunięty pomyślnie!')
    return redirect(url_for('expenses'))

@app.route('/summary')
def summary():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Pobieranie sum wpłat
    cur.execute("SELECT SUM(amount) FROM incomes")
    total_income = cur.fetchone()[0] or 0
    
    # Pobieranie sum wydatków
    cur.execute("SELECT SUM(amount) FROM expenses")
    total_expense = cur.fetchone()[0] or 0
    
    net_balance = total_income - total_expense

    cur.close()
    conn.close()
    return render_template('summary.html', total_income=total_income, total_expense=total_expense, net_balance=net_balance)

if __name__ == '__main__':
    app.run(debug=True)