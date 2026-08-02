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
        controller.geometry("800x700")

        # Entry fields and labels
        tk.Label(self, text="Username:").grid(row=0, column=0, sticky="w", padx=10, pady=8)
        tk.Label(self, text="Password:").grid(row=1, column=0, sticky="w", padx=10, pady=8)

        self.username_entry = tk.Entry(self)
        self.password_entry = tk.Entry(self, show="*")
        self.username_entry.grid(row=0, column=1, padx=10, pady=8, sticky="ew")
        self.password_entry.grid(row=1, column=1, padx=10, pady=8, sticky="ew")

        # Buttons
        tk.Button(self, text="Sign In", width=10, command=self.sign_in).grid(row=2, column=0, columnspan=2, pady=10)
        tk.Button(self, text="Exit App", width=10, command=controller.destroy).grid(row=3, column=0, columnspan=2)

        self.status_label = tk.Label(self, text="", fg="green")
        self.status_label.grid(row=4, column=0, columnspan=2, pady=10)

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
        return


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Sign In")
    app = SignInPage(root, root)
    app.pack(fill="both", expand=True, padx=20, pady=20)
    root.mainloop()