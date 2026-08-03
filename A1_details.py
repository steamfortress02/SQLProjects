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

class DetailsPage(tk.Frame):
    '''
    DetailsPage
    '''
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Set window size
        controller.geometry("400x400")

        # Account Details Labels 
        tk.Label(self, text="Username:").grid(row=0, column=0, sticky="w", padx=10, pady=8)
        tk.Label(self, text="Password:").grid(row=1, column=0, sticky="w", padx=10, pady=8)
        tk.Label(self, text="First Name:").grid(row=2, column=0, sticky="w", padx=10, pady=8)
        tk.Label(self, text="Last Name:").grid(row=3, column=0, sticky="w", padx=10, pady=8)
        tk.Label(self, text="Email:").grid(row=4, column=0, sticky="w", padx=10, pady=8)
        tk.Label(self, text="Phone Number:").grid(row=5, column=0, sticky="w", padx=10, pady=8)

        self.username_value = tk.Label(self, text="", anchor="w")
        self.password_value = tk.Label(self, text="", anchor="w")
        self.first_name_value = tk.Label(self, text="", anchor="w")
        self.last_name_value = tk.Label(self, text="", anchor="w")
        self.email_value = tk.Label(self, text="", anchor="w")
        self.phone_number_value = tk.Label(self, text="", anchor="w")

        self.username_value.grid(row=0, column=1, sticky="w", padx=10, pady=8)
        self.password_value.grid(row=1, column=1, sticky="w", padx=10, pady=8)
        self.first_name_value.grid(row=2, column=1, sticky="w", padx=10, pady=8)
        self.last_name_value.grid(row=3, column=1, sticky="w", padx=10, pady=8)
        self.email_value.grid(row=4, column=1, sticky="w", padx=10, pady=8)
        self.phone_number_value.grid(row=5, column=1, sticky="w", padx=10, pady=8)

        # Buttons
        tk.Button(self, text="Sign Out", width=10, command=lambda: controller.show_frame("SignInPage")).grid(row=6, column=0, columnspan=2, pady=10)
        tk.Button(self, text="Exit App", width=10, command=controller.destroy).grid(row=7, column=0, columnspan=2)

        self.columnconfigure(1, weight=1)

    def set_user_details(self, details):
        self.username_value.config(text=details.get("username", ""))
        self.password_value.config(text=details.get("password", ""))
        self.first_name_value.config(text=details.get("firstName", details.get("first_name", "")))
        self.last_name_value.config(text=details.get("lastName", details.get("last_name", "")))
        self.email_value.config(text=details.get("email", ""))
        self.phone_number_value.config(text=details.get("phone", details.get("phone_number", "")))
