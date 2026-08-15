import tkinter as tk
from tkinter import ttk
import mysql.connector
import hashlib
import os

# Database config
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "1234",
    "database": "signin_db",
}

def hash_password(password):
    """Hashes a password."""
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt.hex() + ':' + key.hex()

class SignUpPage(tk.Frame):
    '''
    SignUpPage
    '''
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Entry fields and labels
        tk.Label(self, text="Username:").grid(row=0, column=0, sticky="w", padx=10, pady=8)
        tk.Label(self, text="Password:").grid(row=1, column=0, sticky="w", padx=10, pady=8)
        tk.Label(self, text="Confirm Password:").grid(row=2, column=0, sticky="w", padx=10, pady=8)
        tk.Label(self, text="First Name:").grid(row=3, column=0, sticky="w", padx=10, pady=8)
        tk.Label(self, text="Last Name:").grid(row=4, column=0, sticky="w", padx=10, pady=8)
        tk.Label(self, text="Email:").grid(row=5, column=0, sticky="w", padx=10, pady=8)
        tk.Label(self, text="Phone Number:").grid(row=6, column=0, sticky="w", padx=10, pady=8)

        self.username_entry = tk.Entry(self, width=40)
        self.password_entry = tk.Entry(self, show="*", width=40)
        self.confirm_password_entry = tk.Entry(self, show="*", width=40)
        self.first_name_entry = tk.Entry(self, width=40)
        self.last_name_entry = tk.Entry(self, width=40)
        self.email_entry = tk.Entry(self, width=40)
        self.phone_number_entry = tk.Entry(self, width=40)
        
        self.username_entry.grid(row=0, column=1, padx=10, pady=8, sticky="ew")
        self.password_entry.grid(row=1, column=1, padx=10, pady=8, sticky="ew")
        self.confirm_password_entry.grid(row=2, column=1, padx=10, pady=8, sticky="ew")
        self.first_name_entry.grid(row=3, column=1, padx=10, pady=8, sticky="ew")
        self.last_name_entry.grid(row=4, column=1, padx=10, pady=8, sticky="ew")
        self.email_entry.grid(row=5, column=1, padx=10, pady=8, sticky="ew")
        self.phone_number_entry.grid(row=6, column=1, padx=10, pady=8, sticky="ew")

        # Buttons
        tk.Button(self, text="Sign Up", width=10, command=self.sign_up).grid(row=7, column=0, columnspan=2, pady=10)
        tk.Button(self, text="Back to Sign In", width=15, command=lambda: self.go_back()).grid(row=8, column=0, columnspan=2, pady=10)
        tk.Button(self, text="Exit App", width=10, command=controller.destroy).grid(row=9, column=0, columnspan=2, pady=10)

        self.status_label = tk.Label(self, text="", fg="green")
        self.status_label.grid(row=10, column=0, columnspan=2, pady=10)

        self.columnconfigure(1, weight=1)
        self.username_entry.focus()

    def connect_mysql(self):
        # Connect to the MySQL database using the provided configuration.
        return mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
        )
        
    def go_back(self):
        self.status_label.config(text="")
        self.controller.show_frame("SignInPage")

    def sign_up(self):
        # Retrieve form data
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        confirm = self.confirm_password_entry.get()
        fname = self.first_name_entry.get().strip()
        lname = self.last_name_entry.get().strip()
        email = self.email_entry.get().strip()
        phone = self.phone_number_entry.get().strip()

        # 1. Validation checks
        if not all([username, password, confirm, fname, lname, email, phone]):
            self.status_label.config(text="All fields are required.", fg="red")
            return
            
        if password != confirm:
            self.status_label.config(text="Passwords do not match.", fg="red")
            return

        try:
            phone_int = int(phone)
        except ValueError:
            self.status_label.config(text="Phone must contain numbers only.", fg="red")
            return

        try:
            conn = self.connect_mysql()
            cursor = conn.cursor()
            
            # 2. Duplicate detection
            cursor.execute('''
                SELECT username, email, phone FROM users 
                WHERE username = %s OR email = %s OR phone = %s
            ''', (username, email, phone_int))
            
            existing = cursor.fetchone()
            if existing:
                if existing[0] == username:
                    self.status_label.config(text="Username already exists.", fg="red")
                elif existing[1] == email:
                    self.status_label.config(text="Email is already registered.", fg="red")
                elif existing[2] == phone_int:
                    self.status_label.config(text="Phone number is already registered.", fg="red")
                return
                
            # 3. Hash and Insert
            hashed_pw = hash_password(password)
            
            cursor.execute('''
                INSERT INTO users (username, password, firstName, lastName, email, phone)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (username, hashed_pw, fname, lname, email, phone_int))
            
            conn.commit()
            
            # 4. Success Reset
            self.status_label.config(text="Registration successful!", fg="green")
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            self.confirm_password_entry.delete(0, tk.END)
            self.first_name_entry.delete(0, tk.END)
            self.last_name_entry.delete(0, tk.END)
            self.email_entry.delete(0, tk.END)
            self.phone_number_entry.delete(0, tk.END)
            
        except mysql.connector.Error as exc:
            self.status_label.config(text=f"Database Error: {exc}", fg="red")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()
