import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import hashlib

# Database config
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "signin_db",
}

class UserCurrent:
    """Holds the currently signed-in user's username"""
    _current_user_id = None  # this stores the username string

    @staticmethod
    def set_current_user_id(uid):
        UserCurrent._current_user_id = uid

    @staticmethod
    def get_current_user_id():
        return UserCurrent._current_user_id

    @staticmethod
    def clear():
        UserCurrent._current_user_id = None

def verify_password(stored_password, provided_password):
    """Verifies a provided password against the stored hashed password."""
    try:
        salt_hex, key_hex = stored_password.split(':')
        salt = bytes.fromhex(salt_hex)
        new_key = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
        return key_hex == new_key.hex()
    except ValueError:
        return False

class SignInPage(tk.Frame):
    '''
    SignInPage
    '''
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        
        # Entry fields and labels
        tk.Label(self, text="Username:").grid(row=0, column=0, sticky="w", padx=10, pady=8)
        tk.Label(self, text="Password:").grid(row=1, column=0, sticky="w", padx=10, pady=8)

        self.username_entry = tk.Entry(self, width=40)
        self.password_entry = tk.Entry(self, show="*", width=40)
        self.username_entry.grid(row=0, column=1, padx=10, pady=8, sticky="ew")
        self.password_entry.grid(row=1, column=1, padx=10, pady=8, sticky="ew")

        self.status_label = tk.Label(self, text="", fg="green")
        self.status_label.grid(row=2, column=0, columnspan=2, pady=10)

        tk.Button(self, text="Sign In", width=10, command=self.sign_in).grid(row=3, column=0, columnspan=2, pady=10)
        tk.Button(self, text="Sign Up", width=10, command=lambda: controller.show_frame("SignUpPage")).grid(row=4, column=0, columnspan=2, pady=10)
        tk.Button(self, text="Exit App", width=10, command=controller.destroy).grid(row=5, column=0, columnspan=2, pady=10)

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
        password = self.password_entry.get()

        if not username or not password:
            self.status_label.config(text="Enter username and password.", fg="red")
            return

        conn = None
        cursor = None
        try:
            conn = self.connect_mysql()
            cursor = conn.cursor(dictionary=True)

            # Using parameterized query to prevent SQL injection and fetch user details.
            cursor.execute(
                "SELECT username, password, firstName, lastName, email, phone FROM users WHERE username = %s",
                (username,),
            )
            row = cursor.fetchone()

            if not row:
                self.status_label.config(text="Invalid username or password.", fg="red")
                return

            stored_password = row["password"]
            if verify_password(stored_password, password):
                # store current username for other modules to use
                UserCurrent.set_current_user_id(row.get("username"))

                self.status_label.config(text="", fg="green")
                self.username_entry.delete(0, tk.END)
                self.password_entry.delete(0, tk.END)

                user_data = {
                    "username": row.get("username", ""),
                    "password": "********",
                    "firstName": row.get("firstName", ""),
                    "lastName": row.get("lastName", ""),
                    "email": row.get("email", ""),
                    "phone": row.get("phone", ""),
                }
                # show the UserPage and ask it to refresh its items
                self.controller.show_frame("UserPage")
                user_page = getattr(self.controller, "frames", {}).get("UserPage")
                if user_page and hasattr(user_page, "refresh_items"):
                    user_page.refresh_items()

            else:
                self.status_label.config(text="Invalid username or password.", fg="red")

        except mysql.connector.Error as exc:
            self.status_label.config(text=f"MySQL error: {exc}", fg="red")
        except Exception as exc:
            self.status_label.config(text=f"Error: {exc}", fg="red")
        finally:
            try:
                if cursor:
                    cursor.close()
            except Exception:
                pass
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
