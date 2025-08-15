import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import csv
import os

# ======================= User Database (SQLite) =======================
conn = sqlite3.connect('users.db')
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL)''')
conn.commit()
conn.close()

# ======================= STUDENT APP VARIABLES =======================
DATA_FILE = "students.csv"
students = []
edit_index = None

# ======================= AUTHENTICATION WINDOW =======================
def open_login_window():
    login_window = tk.Tk()
    login_window.title("Login")
    login_window.geometry("300x300")

    def login():
        username = user_var.get()
        password = pass_var.get()
        if not username or not password:
            messagebox.showwarning("Error", "All fields required.")
            return

        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cur.fetchone()
        conn.close()

        if user:
            messagebox.showinfo("Success", "Login successful!")
            login_window.destroy()
            open_student_crud_app()
        else:
            messagebox.showerror("Failed", "Invalid credentials.")

    def signup():
        username = user_var.get()
        password = pass_var.get()
        if not username or not password:
            messagebox.showwarning("Error", "All fields required.")
            return

        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users(username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            messagebox.showinfo("Success", "Signup successful. Welcome!")
            conn.close()
            login_window.destroy()
            open_student_crud_app()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists.")
        finally:
            conn.close()

    tk.Label(login_window, text="Username").pack(pady=5)
    user_var = tk.StringVar()
    tk.Entry(login_window, textvariable=user_var).pack(pady=5)

    tk.Label(login_window, text="Password").pack(pady=5)
    pass_var = tk.StringVar()
    tk.Entry(login_window, textvariable=pass_var, show='*').pack(pady=5)

    tk.Button(login_window, text="Login", command=login, bg='green', fg='white').pack(pady=10)
    tk.Button(login_window, text="Signup", command=signup, bg='blue', fg='white').pack()

    login_window.mainloop()


# ======================= STUDENT CRUD APP =======================
def open_student_crud_app():
    root = tk.Tk()
    root.title("Student CRUD App")
    root.geometry("700x400")
    root.configure(bg="skyblue")

    def logout():
        root.destroy()
        open_login_window()

    def refresh_table():
        for row in tree.get_children():
            tree.delete(row)
        for i, student in enumerate(students, start=1):
            tree.insert('', 'end', values=(i, student['name'], student['email'], student['password']))

    def clear_fields():
        name_var.set("")
        email_var.set("")
        password_var.set("")

    def save_data(show_message=True):
        with open(DATA_FILE, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["name", "email", "password"])
            for student in students:
                writer.writerow([student['name'], student['email'], student['password']])
        if show_message:
            messagebox.showinfo("Saved", "Student data saved to CSV successfully.")
        else:
            messagebox.showwarning("Deleted", "Student deleted and saved.")

    def load_data():
        students.clear()
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, mode='r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    students.append(row)
            refresh_table()

    def add_student():
        name = name_var.get().strip()
        email = email_var.get().strip()
        password = password_var.get().strip()

        if not name or not email or not password:
            messagebox.showwarning("Input Error", "All fields are required.")
            return

        students.append({'name': name, 'email': email, 'password': password})
        refresh_table()
        clear_fields()
        save_data()

    def delete_student():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a student to delete.")
            return
        index = int(tree.item(selected[0])['values'][0]) - 1
        del students[index]
        refresh_table()
        save_data(show_message=False)

    def edit_student():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a student to edit.")
            return
        nonlocal edit_index
        edit_index = int(tree.item(selected[0])['values'][0]) - 1
        student = students[edit_index]
        name_var.set(student['name'])
        email_var.set(student['email'])
        password_var.set(student['password'])

    def update_student():
        if edit_index is None:
            return
        name = name_var.get().strip()
        email = email_var.get().strip()
        password = password_var.get().strip()
        if not name or not email or not password:
            messagebox.showwarning("Input Error", "All fields are required.")
            return
        students[edit_index] = {'name': name, 'email': email, 'password': password}
        refresh_table()
        clear_fields()
        save_data()
        messagebox.showinfo("Success", "Student updated successfully.")

    name_var = tk.StringVar()
    email_var = tk.StringVar()
    password_var = tk.StringVar()
    edit_index = None

    form_frame = tk.Frame(root, bg="white")
    form_frame.pack(side=tk.LEFT, padx=20, pady=20, fill=tk.Y)

    tk.Label(form_frame, text="Add / Edit Student", bg="white", font=("Arial", 14, "bold")).pack(pady=10)
    tk.Label(form_frame, text="Name:", bg="lightgrey").pack(anchor=tk.W)
    tk.Entry(form_frame, textvariable=name_var, width=30).pack(pady=5)
    tk.Label(form_frame, text="Email:", bg="lightgrey").pack(anchor=tk.W)
    tk.Entry(form_frame, textvariable=email_var, width=30).pack(pady=5)
    tk.Label(form_frame, text="Password:", bg="lightgrey").pack(anchor=tk.W)
    tk.Entry(form_frame, textvariable=password_var, show="*", width=30).pack(pady=5)

    tk.Button(form_frame, text="Add Student", command=add_student, width=25, bg="green", fg="white").pack(pady=5)
    tk.Button(form_frame, text="Update Student", command=update_student, width=25, bg="blue", fg="white").pack(pady=5)
    tk.Button(form_frame, text="Clear", command=clear_fields, width=25).pack(pady=5)

    table_frame = tk.Frame(root)
    table_frame.pack(padx=10, pady=20, fill=tk.BOTH, expand=True)

    tk.Label(table_frame, text="Student Information", font=("Arial", 14, "bold")).pack()

    columns = ('ID', 'Name', 'Email', 'Password')
    tree = ttk.Treeview(table_frame, columns=columns, show='headings')
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center")  # <-- Center align the data
    tree.pack(fill=tk.BOTH, expand=True)

    btn_frame = tk.Frame(root, bg="white")
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Edit", command=edit_student, bg="orange", width=12).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Delete", command=delete_student, bg="red", fg="white", width=12).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Save", command=save_data, bg="purple", fg="white", width=12).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Exit", command=root.destroy, bg="gray", width=12).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Logout", command=logout, bg="black", fg="white", width=12).pack(side=tk.LEFT, padx=5)

    load_data()
    root.mainloop()


# Run the authentication window first
open_login_window()
