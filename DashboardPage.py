import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import date

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root", # Update if necessary
    "database": "signin_db",
}

class DashboardPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.username = ""
        
        # UI Tab Setup
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.tab_items = ttk.Frame(self.notebook)
        self.tab_cats = ttk.Frame(self.notebook)
        self.tab_reviews = ttk.Frame(self.notebook)
        self.tab_queries = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_items, text="Items")
        self.notebook.add(self.tab_cats, text="Categories")
        self.notebook.add(self.tab_reviews, text="Reviews")
        self.notebook.add(self.tab_queries, text="Queries")

        self.build_items_tab()
        self.build_cats_tab()
        self.build_reviews_tab()
        self.build_queries_tab()

        tk.Button(self, text="Sign Out", bg="red", fg="white", command=lambda: controller.show_frame("SignInPage")).pack(pady=5)

    def set_user_details(self, details):
        self.username = details.get("username", "")

    def get_conn(self):
        return mysql.connector.connect(**DB_CONFIG)

    # --- ITEMS TAB ---
    def build_items_tab(self):
        # Add Item
        tk.Label(self.tab_items, text="Add New Item", font="bold").grid(row=0, column=0, columnspan=2, pady=5)
        tk.Label(self.tab_items, text="Title:").grid(row=1, column=0)
        self.item_title = tk.Entry(self.tab_items, width=30)
        self.item_title.grid(row=1, column=1)
        
        tk.Label(self.tab_items, text="Description:").grid(row=2, column=0)
        self.item_desc = tk.Entry(self.tab_items, width=30)
        self.item_desc.grid(row=2, column=1)
        
        tk.Label(self.tab_items, text="Price:").grid(row=3, column=0)
        self.item_price = tk.Entry(self.tab_items, width=30)
        self.item_price.grid(row=3, column=1)
        
        tk.Label(self.tab_items, text="Categories (csv):").grid(row=4, column=0)
        self.item_cats = tk.Entry(self.tab_items, width=30)
        self.item_cats.grid(row=4, column=1)
        
        tk.Button(self.tab_items, text="Post Item", command=self.add_item).grid(row=5, column=0, columnspan=2, pady=5)
        
        ttk.Separator(self.tab_items, orient='horizontal').grid(row=6, column=0, columnspan=2, sticky='ew', pady=10)
        
        # Modify Items
        tk.Label(self.tab_items, text="Update / Delete Your Items", font="bold").grid(row=7, column=0, columnspan=2, pady=5)
        tk.Label(self.tab_items, text="Item ID:").grid(row=8, column=0)
        self.mod_item_id = tk.Entry(self.tab_items, width=15)
        self.mod_item_id.grid(row=8, column=1, sticky='w')
        
        tk.Label(self.tab_items, text="New Price:").grid(row=9, column=0)
        self.mod_price = tk.Entry(self.tab_items, width=15)
        self.mod_price.grid(row=9, column=1, sticky='w')
        
        tk.Button(self.tab_items, text="Update Price", command=self.update_price).grid(row=10, column=0, pady=5)
        tk.Button(self.tab_items, text="Delete Item", command=self.delete_item).grid(row=10, column=1, pady=5)

    def add_item(self):
        today = date.today()
        try:
            conn = self.get_conn()
            cursor = conn.cursor()
            # Enforce single lowercase word categories at application layer
            cat_list = [c.strip().lower().split()[0] for c in self.item_cats.get().split(",") if c.strip()]
            
            cursor.execute(
                "INSERT INTO items (title, description, price, date_posted, seller) VALUES (%s, %s, %s, %s, %s)",
                (self.item_title.get(), self.item_desc.get(), float(self.item_price.get()), today, self.username)
            )
            item_id = cursor.lastrowid
            for c in set(cat_list):
                cursor.execute("INSERT IGNORE INTO categories (category_name) VALUES (%s)", (c,))
                cursor.execute("INSERT IGNORE INTO item_categories (item_id, category_name) VALUES (%s, %s)", (item_id, c))
            conn.commit()
            messagebox.showinfo("Success", f"Item posted! ID: {item_id}")
        except mysql.connector.Error as e:
            messagebox.showerror("Database Rule Violation", str(e))
        finally:
            if 'conn' in locals(): conn.close()

    def update_price(self):
        try:
            conn = self.get_conn()
            cursor = conn.cursor()
            cursor.execute("UPDATE items SET price = %s WHERE item_id = %s AND seller = %s", 
                           (float(self.mod_price.get()), self.mod_item_id.get(), self.username))
            if cursor.rowcount > 0:
                conn.commit()
                messagebox.showinfo("Success", "Price updated.")
            else:
                messagebox.showerror("Error", "Item not found or you are not the seller.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            if 'conn' in locals(): conn.close()

    def delete_item(self):
        try:
            conn = self.get_conn()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM items WHERE item_id = %s AND seller = %s", (self.mod_item_id.get(), self.username))
            if cursor.rowcount > 0:
                conn.commit()
                messagebox.showinfo("Success", "Item deleted.")
            else:
                messagebox.showerror("Error", "Item not found or you are not the seller.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            if 'conn' in locals(): conn.close()

    # --- CATEGORIES TAB ---
    def build_cats_tab(self):
        tk.Label(self.tab_cats, text="Item ID:").grid(row=0, column=0, pady=5)
        self.cat_item_id = tk.Entry(self.tab_cats, width=15)
        self.cat_item_id.grid(row=0, column=1)
        
        tk.Label(self.tab_cats, text="Category Name:").grid(row=1, column=0, pady=5)
        self.cat_name = tk.Entry(self.tab_cats, width=15)
        self.cat_name.grid(row=1, column=1)
        
        tk.Button(self.tab_cats, text="Assign", command=lambda: self.mod_cat('assign')).grid(row=2, column=0, pady=5)
        tk.Button(self.tab_cats, text="Remove", command=lambda: self.mod_cat('remove')).grid(row=2, column=1, pady=5)
        
        ttk.Separator(self.tab_cats, orient='horizontal').grid(row=3, column=0, columnspan=2, sticky='ew', pady=10)
        
        tk.Label(self.tab_cats, text="Search Category:").grid(row=4, column=0)
        self.cat_search = tk.Entry(self.tab_cats, width=15)
        self.cat_search.grid(row=4, column=1)
        tk.Button(self.tab_cats, text="Search", command=self.search_cats).grid(row=5, column=0, columnspan=2)
        
        self.cat_results = tk.Text(self.tab_cats, height=10, width=40)
        self.cat_results.grid(row=6, column=0, columnspan=2, pady=5)

    def mod_cat(self, action):
        cat = self.cat_name.get().strip().lower().split()[0]
        try:
            conn = self.get_conn()
            cursor = conn.cursor()
            if action == 'assign':
                cursor.execute("INSERT IGNORE INTO categories (category_name) VALUES (%s)", (cat,))
                cursor.execute("INSERT IGNORE INTO item_categories (item_id, category_name) VALUES (%s, %s)", (self.cat_item_id.get(), cat))
                messagebox.showinfo("Success", "Category Assigned.")
            elif action == 'remove':
                cursor.execute("DELETE FROM item_categories WHERE item_id = %s AND category_name = %s", (self.cat_item_id.get(), cat))
                messagebox.showinfo("Success", "Category Removed.")
            conn.commit()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            if 'conn' in locals(): conn.close()

    def search_cats(self):
        cat = self.cat_search.get().strip().lower()
        try:
            conn = self.get_conn()
            cursor = conn.cursor()
            cursor.execute("SELECT i.item_id, i.title FROM items i JOIN item_categories ic ON i.item_id = ic.item_id WHERE ic.category_name = %s", (cat,))
            results = cursor.fetchall()
            self.cat_results.delete(1.0, tk.END)
            for row in results:
                self.cat_results.insert(tk.END, f"ID: {row[0]} | Title: {row[1]}\n")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            if 'conn' in locals(): conn.close()

    # --- REVIEWS TAB ---
    def build_reviews_tab(self):
        tk.Label(self.tab_reviews, text="Item ID:").grid(row=0, column=0, pady=5)
        self.rev_item = tk.Entry(self.tab_reviews)
        self.rev_item.grid(row=0, column=1)
        
        tk.Label(self.tab_reviews, text="Rating:").grid(row=1, column=0, pady=5)
        self.rev_rating = ttk.Combobox(self.tab_reviews, values=["Excellent", "Good", "Fair", "Poor"], state="readonly")
        self.rev_rating.grid(row=1, column=1)
        
        tk.Label(self.tab_reviews, text="Comment:").grid(row=2, column=0, pady=5)
        self.rev_comment = tk.Entry(self.tab_reviews)
        self.rev_comment.grid(row=2, column=1)
        
        tk.Button(self.tab_reviews, text="Submit Review", command=self.add_review).grid(row=3, column=0, columnspan=2, pady=10)

    def add_review(self):
        try:
            conn = self.get_conn()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO reviews (item_id, reviewer, rating, comment, review_date) VALUES (%s, %s, %s, %s, %s)",
                (self.rev_item.get(), self.username, self.rev_rating.get(), self.rev_comment.get(), date.today())
            )
            conn.commit()
            messagebox.showinfo("Success", "Review Submitted.")
        except mysql.connector.Error as e:
            messagebox.showerror("Database Rule Violation", str(e))
        finally:
            if 'conn' in locals(): conn.close()

    # --- ADVANCED QUERIES TAB ---
    def build_queries_tab(self):
        frame_inputs = tk.Frame(self.tab_queries)
        frame_inputs.pack(pady=5)
        
        # Inputs needed for specific queries
        tk.Label(frame_inputs, text="Q2 Cat X & Y:").grid(row=0, column=0)
        self.q2_x = tk.Entry(frame_inputs, width=10); self.q2_x.grid(row=0, column=1)
        self.q2_y = tk.Entry(frame_inputs, width=10); self.q2_y.grid(row=0, column=2)
        
        tk.Label(frame_inputs, text="Q3 User:").grid(row=1, column=0)
        self.q3_user = tk.Entry(frame_inputs, width=20); self.q3_user.grid(row=1, column=1, columnspan=2)
        
        tk.Label(frame_inputs, text="Q4 Date (YYYY-MM-DD):").grid(row=2, column=0)
        self.q4_date = tk.Entry(frame_inputs, width=20); self.q4_date.grid(row=2, column=1, columnspan=2)

        frame_btns = tk.Frame(self.tab_queries)
        frame_btns.pack(pady=5)
        for i in range(1, 7):
            tk.Button(frame_btns, text=f"Q{i}", command=lambda idx=i: self.run_query(idx)).grid(row=0, column=i)
            
        self.query_results = tk.Text(self.tab_queries, height=12, width=45)
        self.query_results.pack()

    def run_query(self, query_id):
        self.query_results.delete(1.0, tk.END)
        sql = ""
        params = ()
        try:
            if query_id == 1:
                sql = """SELECT c.category_name, i.item_id, i.title, i.price
                         FROM categories c
                         JOIN item_categories ic ON c.category_name = ic.category_name
                         JOIN items i ON ic.item_id = i.item_id
                         WHERE i.price = (
                             SELECT MAX(i2.price) FROM item_categories ic2
                             JOIN items i2 ON ic2.item_id = i2.item_id
                             WHERE ic2.category_name = c.category_name)"""
            elif query_id == 2:
                sql = """SELECT DISTINCT i1.seller FROM items i1
                         JOIN item_categories ic1 ON i1.item_id = ic1.item_id
                         JOIN items i2 ON i1.seller = i2.seller AND i1.date_posted = i2.date_posted AND i1.item_id != i2.item_id
                         JOIN item_categories ic2 ON i2.item_id = ic2.item_id
                         WHERE ic1.category_name = %s AND ic2.category_name = %s"""
                params = (self.q2_x.get(), self.q2_y.get())
            elif query_id == 3:
                sql = """SELECT i.item_id, i.title FROM items i
                         WHERE i.seller = %s
                           AND (SELECT COUNT(*) FROM reviews r WHERE r.item_id = i.item_id) > 0
                           AND (SELECT COUNT(*) FROM reviews r WHERE r.item_id = i.item_id AND r.rating NOT IN ('Excellent', 'Good')) = 0"""
                params = (self.q3_user.get(),)
            elif query_id == 4:
                sql = """SELECT seller, COUNT(item_id) as item_count FROM items
                         WHERE date_posted = %s GROUP BY seller
                         HAVING item_count = (
                             SELECT MAX(cnt) FROM (SELECT COUNT(item_id) as cnt FROM items WHERE date_posted = %s GROUP BY seller) as sub
                         )"""
                params = (self.q4_date.get(), self.q4_date.get())
            elif query_id == 5:
                sql = """SELECT reviewer FROM reviews GROUP BY reviewer
                         HAVING COUNT(*) > 0 AND SUM(CASE WHEN rating != 'Poor' THEN 1 ELSE 0 END) = 0"""
            elif query_id == 6:
                sql = """SELECT username FROM users WHERE username NOT IN (
                             SELECT i.seller FROM items i JOIN reviews r ON i.item_id = r.item_id WHERE r.rating = 'Poor'
                         )"""

            conn = self.get_conn()
            cursor = conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            for r in rows:
                self.query_results.insert(tk.END, str(r) + "\n")
            if not rows: self.query_results.insert(tk.END, "No results found.")
        except Exception as e:
            self.query_results.insert(tk.END, f"Error: {str(e)}")
        finally:
            if 'conn' in locals(): conn.close()