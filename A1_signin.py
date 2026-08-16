import tkinter as tk
from tkinter import ttk
import mysql.connector
import hashlib

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root", # Update if necessary
    "database": "signin_db",
}

def verify_password(stored_password, provided_password):
    try:
        salt_hex, key_hex = stored_password.split(':')
        salt = bytes.fromhex(salt_hex)
        new_key = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
        return key_hex == new_key.hex()
    except ValueError:
        return False

class SignInPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        tk.Label(self, text="Username:").grid(row=0, column=0, sticky="w", padx=10, pady=8)
        tk.Label(self, text="Password:").grid(row=1, column=0, sticky="w", padx=10, pady=8)
        self.username_entry = tk.Entry(self, width=35)
        self.password_entry = tk.Entry(self, show="*", width=35)
        self.username_entry.grid(row=0, column=1, padx=10, pady=8, sticky="ew")
        self.password_entry.grid(row=1, column=1, padx=10, pady=8, sticky="ew")

        tk.Button(self, text="Sign In", width=10, command=self.sign_in).grid(row=2, column=0, columnspan=2, pady=10)
        tk.Button(self, text="Sign Up", width=10, command=lambda: controller.show_frame("SignUpPage")).grid(row=3, column=0, columnspan=2, pady=10)
        tk.Button(self, text="Exit App", width=10, command=controller.destroy).grid(row=4, column=0, columnspan=2, pady=10)

        self.status_label = tk.Label(self, text="", fg="green")
        self.status_label.grid(row=5, column=0, columnspan=2, pady=10)
        self.columnconfigure(1, weight=1)

    def sign_in(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT username, password FROM users WHERE username = %s", (username,))
            row = cursor.fetchone()

            if row and verify_password(row["password"], password):
                self.status_label.config(text="")
                self.username_entry.delete(0, tk.END)
                self.password_entry.delete(0, tk.END)
                
                # Pass details to dashboard and swap frames
                self.controller.set_user_details({"username": row["username"]})
                self.controller.show_frame("DashboardPage")
            else:
                self.status_label.config(text="Invalid username or password.", fg="red")
        except Exception as exc:
            self.status_label.config(text=f"Error: {exc}", fg="red")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()