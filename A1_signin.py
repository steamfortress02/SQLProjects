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


class SignInPage(tk.Frame):
    '''
    SignInPage
    '''
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Set window size
        controller.geometry("400x400")

        # Entry fields and labels
        tk.Label(self, text="Username:").grid(row=0, column=0, sticky="w", padx=10, pady=8)
        tk.Label(self, text="Password:").grid(row=1, column=0, sticky="w", padx=10, pady=8)

        self.username_entry = tk.Entry(self, width=35)
        self.password_entry = tk.Entry(self, show="*", width=35)
        self.username_entry.grid(row=0, column=1, padx=10, pady=8, sticky="ew")
        self.password_entry.grid(row=1, column=1, padx=10, pady=8, sticky="ew")

        # Buttons
        tk.Button(self, text="Sign In", width=10, command=self.sign_in).grid(row=2, column=0, columnspan=2, pady=10)
        tk.Button(self, text="Sign Up", width=10, command=lambda: controller.show_frame("SignUpPage")).grid(row=3, column=0, columnspan=2, pady=10)
        tk.Button(self, text="Exit App", width=10, command=controller.destroy).grid(row=4, column=0, columnspan=2, pady=10)

        self.status_label = tk.Label(self, text="", fg="green")
        self.status_label.grid(row=5, column=0, columnspan=2, pady=10)

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

    def sign_in(self):
        # Sign in method to validate user credentials against the MySQL database.
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            self.status_label.config(text="Enter username and password.", fg="red")
            return

        try:
            conn = self.connect_mysql()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT username, password, first_name, last_name, email, phone_number "
                "FROM users WHERE username = %s",
                (username,),
            )
            row = cursor.fetchone()
            cursor.close()
            conn.close()

            if not row:
                self.status_label.config(text="Invalid username or password.", fg="red")
                return

            stored_password = row["password"]
            if stored_password == password:
                self.status_label.config(text="Login successful.", fg="green")
                user_data = {
                    "username": row.get("username", ""),
                    "password": stored_password,
                    "first_name": row.get("first_name", ""),
                    "last_name": row.get("last_name", ""),
                    "email": row.get("email", ""),
                    "phone_number": row.get("phone_number", ""),
                }
                self.controller.set_user_details(user_data)
                self.controller.show_frame("DetailsPage")
            else:
                self.status_label.config(text="Invalid username or password.", fg="red")

        except mysql.connector.Error as exc:
            self.status_label.config(text=f"MySQL error: {exc}", fg="red")
        except Exception as exc:
            self.status_label.config(text=f"Error: {exc}", fg="red")
