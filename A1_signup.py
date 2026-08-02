import tkinter as tk
from tkinter import ttk
import mysql.connector

# Anthony Langers data base config
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "signin_db",
}


class SignUpPage(tk.Frame):
    '''
    SignUpPage
    '''
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Set window size
        controller.geometry("500x600")

        # Entry fields and labels
        tk.Label(self, text="Username:").grid(row=0, column=0, sticky="w", padx=10, pady=8)
        tk.Label(self, text="Password:").grid(row=1, column=0, sticky="w", padx=10, pady=8)
        tk.Label(self, text="Confirm Password:").grid(row=2, column=0, sticky="w", padx=10, pady=8)
        tk.Label(self, text="First Name:").grid(row=3, column=0, sticky="w", padx=10, pady=8)
        tk.Label(self, text="Last Name:").grid(row=4, column=0, sticky="w", padx=10, pady=8)
        tk.Label(self, text="Email:").grid(row=5, column=0, sticky="w", padx=10, pady=8)
        tk.Label(self, text="Phone Number:").grid(row=6, column=0, sticky="w", padx=10, pady=8)

        self.username_entry = tk.Entry(self)
        self.password_entry = tk.Entry(self, show="*")
        self.confirm_password_entry = tk.Entry(self, show="*")
        self.first_name_entry = tk.Entry(self)
        self.last_name_entry = tk.Entry(self)
        self.email_entry = tk.Entry(self)
        self.phone_number_entry = tk.Entry(self)
        self.username_entry.grid(row=0, column=1, padx=10, pady=8, sticky="ew")
        self.password_entry.grid(row=1, column=1, padx=10, pady=8, sticky="ew")
        self.confirm_password_entry.grid(row=2, column=1, padx=10, pady=8, sticky="ew")
        self.first_name_entry.grid(row=3, column=1, padx=10, pady=8, sticky="ew")
        self.last_name_entry.grid(row=4, column=1, padx=10, pady=8, sticky="ew")
        self.email_entry.grid(row=5, column=1, padx=10, pady=8, sticky="ew")
        self.phone_number_entry.grid(row=6, column=1, padx=10, pady=8, sticky="ew")

        # Buttons
        tk.Button(self, text="Sign Up", width=10, command=self.sign_up).grid(row=7, column=0, columnspan=2, pady=10)
        tk.Button(self, text="Back to Sign In", width=15, command=lambda: controller.show_frame("SignInPage")).grid(row=8, column=0, columnspan=2, pady=10)
        tk.Button(self, text="Exit App", width=10, command=controller.destroy).grid(row=9, column=0, columnspan=2)

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

    def sign_up(self):
        # Sign up method to create a new user in the MySQL database.
        return