import sqlite3
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import io
from PIL import Image, ImageTk

# Tworzenie bazy danych SQLite
conn = sqlite3.connect('budget_management.db')
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

# Funkcje do zarządzania danymi

# Wpłaty
def add_income():
    amount = income_amount_entry.get()
    date = income_date_entry.get()
    if amount and date:
        c.execute("INSERT INTO incomes (amount, date) VALUES (?, ?)", (amount, date))
        conn.commit()
        refresh_income_list()
        income_amount_entry.delete(0, END)
        income_date_entry.delete(0, END)
    else:
        messagebox.showwarning("Błąd", "Wypełnij wszystkie pola")

def edit_income():
    selected_item = income_list.selection()
    if selected_item:
        item_id = income_list.item(selected_item, 'values')[0]
        amount = income_amount_entry.get()
        date = income_date_entry.get()
        if amount and date:
            c.execute("UPDATE incomes SET amount=?, date=? WHERE id=?", (amount, date, item_id))
            conn.commit()
            refresh_income_list()
            income_amount_entry.delete(0, END)
            income_date_entry.delete(0, END)
        else:
            messagebox.showwarning("Błąd", "Wypełnij wszystkie pola")
    else:
        messagebox.showwarning("Błąd", "Wybierz wpłatę do edycji")

def delete_income():
    selected_item = income_list.selection()
    if selected_item:
        item_id = income_list.item(selected_item, 'values')[0]
        c.execute("DELETE FROM incomes WHERE id=?", (item_id,))
        conn.commit()
        refresh_income_list()
    else:
        messagebox.showwarning("Błąd", "Wybierz wpłatę do usunięcia")

# Wydatki
def add_expense():
    category = expense_category_entry.get()
    amount = expense_amount_entry.get()
    date = expense_date_entry.get()
    if category and amount and date:
        c.execute("INSERT INTO expenses (category, amount, date) VALUES (?, ?, ?)", (category, amount, date))
        conn.commit()
        refresh_expense_list()
        expense_category_entry.delete(0, END)
        expense_amount_entry.delete(0, END)
        expense_date_entry.delete(0, END)
    else:
        messagebox.showwarning("Błąd", "Wypełnij wszystkie pola")

def edit_expense():
    selected_item = expense_list.selection()
    if selected_item:
        item_id = expense_list.item(selected_item, 'values')[0]
        category = expense_category_entry.get()
        amount = expense_amount_entry.get()
        date = expense_date_entry.get()
        if category and amount and date:
            c.execute("UPDATE expenses SET category=?, amount=?, date=? WHERE id=?", (category, amount, date, item_id))
            conn.commit()
            refresh_expense_list()
            expense_category_entry.delete(0, END)
            expense_amount_entry.delete(0, END)
            expense_date_entry.delete(0, END)
        else:
            messagebox.showwarning("Błąd", "Wypełnij wszystkie pola")
    else:
        messagebox.showwarning("Błąd", "Wybierz wydatek do edycji")

def delete_expense():
    selected_item = expense_list.selection()
    if selected_item:
        item_id = expense_list.item(selected_item, 'values')[0]
        c.execute("DELETE FROM expenses WHERE id=?", (item_id,))
        conn.commit()
        refresh_expense_list()
    else:
        messagebox.showwarning("Błąd", "Wybierz wydatek do usunięcia")

# Odświeżanie list
def refresh_income_list():
    for row in income_list.get_children():
        income_list.delete(row)
    c.execute("SELECT * FROM incomes")
    rows = c.fetchall()
    for row in rows:
        income_list.insert("", END, values=row)

def refresh_expense_list():
    for row in expense_list.get_children():
        expense_list.delete(row)
    c.execute("SELECT * FROM expenses")
    rows = c.fetchall()
    for row in rows:
        expense_list.insert("", END, values=row)

# Podsumowanie
def calculate_summary():
    c.execute("SELECT SUM(amount) FROM incomes")
    total_income = c.fetchone()[0] or 0
    c.execute("SELECT SUM(amount) FROM expenses")
    total_expense = c.fetchone()[0] or 0
    net_balance = total_income - total_expense

    summary_text.set(f"Suma wpłat: {total_income}\nSuma wydatków: {total_expense}\nSaldo netto: {net_balance}")

# Filtracja
def filter_data():
    start_date = start_date_entry.get()
    end_date = end_date_entry.get()
    category = category_filter_entry.get()

    query = "SELECT * FROM expenses"
    params = []

    if start_date and end_date:
        query += " WHERE date BETWEEN ? AND ?"
        params = [start_date, end_date]
        if category:
            query += " AND category = ?"
            params.append(category)
    elif category:
        query += " WHERE category = ?"
        params.append(category)

    for row in expense_list.get_children():
        expense_list.delete(row)
    c.execute(query, params)
    rows = c.fetchall()
    for row in rows:
        expense_list.insert("", END, values=row)

# Generowanie raportu PDF
def generate_pdf_report():
    c.execute("SELECT * FROM incomes")
    incomes = c.fetchall()
    c.execute("SELECT * FROM expenses")
    expenses = c.fetchall()
    c.execute("SELECT SUM(amount) FROM incomes")
    total_income = c.fetchone()[0] or 0
    c.execute("SELECT SUM(amount) FROM expenses")
    total_expense = c.fetchone()[0] or 0
    net_balance = total_income - total_expense

    filename = "budget_report.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    # Nagłówek
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 50, "Raport Budżetowy")

    # Wpłaty
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, height - 100, "Wpłaty:")
    c.setFont("Helvetica", 12)
    y = height - 120
    for income in incomes:
        c.drawString(100, y, f"ID: {income[0]}, Kwota: {income[1]}, Data: {income[2]}")
        y -= 20

    # Wydatki
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, y - 20, "Wydatki:")
    c.setFont("Helvetica", 12)
    y -= 40
    for expense in expenses:
        c.drawString(100, y, f"ID: {expense[0]}, Kategoria: {expense[1]}, Kwota: {expense[2]}, Data: {expense[3]}")
        y -= 20

    # Podsumowanie
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, y - 20, "Podsumowanie:")
    c.setFont("Helvetica", 12)
    y -= 40
    c.drawString(100, y, f"Suma wpłat: {total_income}")
    c.drawString(100, y - 20, f"Suma wydatków: {total_expense}")
    c.drawString(100, y - 40, f"Saldo netto: {net_balance}")

    c.save()
    messagebox.showinfo("Sukces", f"Raport został zapisany jako {filename}")

# Wizualizacja danych
def plot_data():
    c.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    category_data = c.fetchall()
    categories = [row[0] for row in category_data]
    amounts = [row[1] for row in category_data]

    fig, ax = plt.subplots()
    ax.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    # Konwersja wykresu do formatu obrazu
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img = Image.open(buf)
    img = img.resize((400, 400), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(img)

    # Wyświetlanie obrazu w aplikacji
    plot_label.config(image=img)
    plot_label.image = img

# Interfejs GUI
root = Tk()
root.title("Zarządzanie Budżetem")

# Sekcja wpłat
income_frame = LabelFrame(root, text="Wpłaty")
income_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

income_amount_label = Label(income_frame, text="Kwota:")
income_amount_label.grid(row=0, column=0, padx=10, pady=10)
income_amount_entry = Entry(income_frame)
income_amount_entry.grid(row=0, column=1, padx=10, pady=10)

income_date_label = Label(income_frame, text="Data:")
income_date_label.grid(row=1, column=0, padx=10, pady=10)
income_date_entry = Entry(income_frame)
income_date_entry.grid(row=1, column=1, padx=10, pady=10)

income_add_button = Button(income_frame, text="Dodaj Wpłatę", command=add_income)
income_add_button.grid(row=2, column=0, pady=10)

income_edit_button = Button(income_frame, text="Edytuj Wpłatę", command=edit_income)
income_edit_button.grid(row=2, column=1, pady=10)

income_delete_button = Button(income_frame, text="Usuń Wpłatę", command=delete_income)
income_delete_button.grid(row=2, column=2, pady=10)

income_list = ttk.Treeview(income_frame, columns=("ID", "Kwota", "Data"), show='headings')
income_list.heading("ID", text="ID")
income_list.heading("Kwota", text="Kwota")
income_list.heading("Data", text="Data")
income_list.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

refresh_income_list()

# Sekcja wydatków
expense_frame = LabelFrame(root, text="Wydatki")
expense_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

expense_category_label = Label(expense_frame, text="Kategoria:")
expense_category_label.grid(row=0, column=0, padx=10, pady=10)
expense_category_entry = Entry(expense_frame)
expense_category_entry.grid(row=0, column=1, padx=10, pady=10)

expense_amount_label = Label(expense_frame, text="Kwota:")
expense_amount_label.grid(row=1, column=0, padx=10, pady=10)
expense_amount_entry = Entry(expense_frame)
expense_amount_entry.grid(row=1, column=1, padx=10, pady=10)

expense_date_label = Label(expense_frame, text="Data:")
expense_date_label.grid(row=2, column=0, padx=10, pady=10)
expense_date_entry = Entry(expense_frame)
expense_date_entry.grid(row=2, column=1, padx=10, pady=10)

expense_add_button = Button(expense_frame, text="Dodaj Wydatek", command=add_expense)
expense_add_button.grid(row=3, column=0, pady=10)

expense_edit_button = Button(expense_frame, text="Edytuj Wydatek", command=edit_expense)
expense_edit_button.grid(row=3, column=1, pady=10)

expense_delete_button = Button(expense_frame, text="Usuń Wydatek", command=delete_expense)
expense_delete_button.grid(row=3, column=2, pady=10)

expense_list = ttk.Treeview(expense_frame, columns=("ID", "Kategoria", "Kwota", "Data"), show='headings')
expense_list.heading("ID", text="ID")
# Sekcja wydatków (kontynuacja)
expense_list.heading("Kategoria", text="Kategoria")
expense_list.heading("Kwota", text="Kwota")
expense_list.heading("Data", text="Data")
expense_list.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

refresh_expense_list()

# Sekcja filtrowania
filter_frame = LabelFrame(root, text="Filtrowanie Wydatków")
filter_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

start_date_label = Label(filter_frame, text="Data od:")
start_date_label.grid(row=0, column=0, padx=10, pady=10)
start_date_entry = Entry(filter_frame)
start_date_entry.grid(row=0, column=1, padx=10, pady=10)

end_date_label = Label(filter_frame, text="Data do:")
end_date_label.grid(row=1, column=0, padx=10, pady=10)
end_date_entry = Entry(filter_frame)
end_date_entry.grid(row=1, column=1, padx=10, pady=10)

category_filter_label = Label(filter_frame, text="Kategoria:")
category_filter_label.grid(row=2, column=0, padx=10, pady=10)
category_filter_entry = Entry(filter_frame)
category_filter_entry.grid(row=2, column=1, padx=10, pady=10)

filter_button = Button(filter_frame, text="Filtruj", command=filter_data)
filter_button.grid(row=3, column=0, columnspan=2, pady=10)

# Sekcja podsumowania
summary_frame = LabelFrame(root, text="Podsumowanie")
summary_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

summary_text = StringVar()
summary_label = Label(summary_frame, textvariable=summary_text, justify="left")
summary_label.grid(row=0, column=0, padx=10, pady=10)

calculate_summary_button = Button(summary_frame, text="Oblicz Podsumowanie", command=calculate_summary)
calculate_summary_button.grid(row=1, column=0, pady=10)

# Sekcja raportu PDF
report_frame = LabelFrame(root, text="Generowanie Raportu PDF")
report_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

generate_pdf_button = Button(report_frame, text="Generuj Raport PDF", command=generate_pdf_report)
generate_pdf_button.grid(row=0, column=0, pady=10)

# Sekcja wizualizacji danych
plot_frame = LabelFrame(root, text="Wizualizacja Danych")
plot_frame.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")

plot_label = Label(plot_frame)
plot_label.grid(row=0, column=0, padx=10, pady=10)

plot_button = Button(plot_frame, text="Wygeneruj Wykres", command=plot_data)
plot_button.grid(row=1, column=0, pady=10)

calculate_summary()

root.mainloop()

# Zamknięcie połączenia z bazą danych
conn.close()