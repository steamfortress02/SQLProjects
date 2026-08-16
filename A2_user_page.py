import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from collections import namedtuple
from datetime import date
from A1_signin import UserCurrent

# Anthony Langers data base config
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "signin_db",
}


class InventoryDatabase:
    """Minimal DB adapter for item table used by UserPage."""

    Item = namedtuple("Item", ["itemID", "title", "description",
                               "date", "price", "poster_username",
                               "cat_electronics", "cat_books", "cat_sports",
                               "cat_clothes", "cat_toys", "cat_decor",
                               "cat_furnitture"])

    @staticmethod
    def _connect():
        return mysql.connector.connect(**DB_CONFIG)

    @staticmethod
    def get_items_with_username(username):
        if not username:
            return []
        conn = None
        try:
            conn = InventoryDatabase._connect()
            cur = conn.cursor()
            cur.execute(
                "SELECT itemID, title, description, date, price, poster_username, "
                "cat_electronics, cat_books, cat_sports, cat_clothes, cat_toys, cat_decor, cat_furnitture "
                "FROM item WHERE poster_username = %s ORDER BY itemID DESC",
                (username,)
            )
            rows = cur.fetchall()
            items = [InventoryDatabase.Item(*row) for row in rows]
            return items
        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_all_items(category=None, min_price=None, max_price=None):
        """Return items filtered by optional category and price bounds, ordered by itemID desc.

        category: one of 'Electronics','Books','Sports','Clothes','Toys','Decor','Furniture' or None/'All'
        min_price/max_price: numeric or None
        """
        conn = None
        try:
            conn = InventoryDatabase._connect()
            cur = conn.cursor()

            where_clauses = []
            params = []

            # category mapping to column name
            cat_map = {
                'Electronics': 'cat_electronics',
                'Books': 'cat_books',
                'Sports': 'cat_sports',
                'Clothes': 'cat_clothes',
                'Toys': 'cat_toys',
                'Decor': 'cat_decor',
                'Furniture': 'cat_furnitture',
            }
            if category and category != 'All':
                col = cat_map.get(category)
                if col:
                    where_clauses.append(f"{col} = %s")
                    params.append(1)

            if min_price is not None:
                where_clauses.append("price >= %s")
                params.append(float(min_price))
            if max_price is not None:
                where_clauses.append("price <= %s")
                params.append(float(max_price))

            sql = (
                "SELECT itemID, title, description, date, price, poster_username, "
                "cat_electronics, cat_books, cat_sports, cat_clothes, cat_toys, cat_decor, cat_furnitture "
                "FROM item"
            )
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)
            sql += " ORDER BY itemID DESC"

            cur.execute(sql, tuple(params))
            rows = cur.fetchall()
            items = [InventoryDatabase.Item(*row) for row in rows]
            return items
        finally:
            if conn:
                conn.close()

    @staticmethod
    def create_new_item(name, description, price, categories):
        """
        Insert a new item row.
        'categories' is a dict mapping cat_* keys to 0/1 (multiple allowed).
        itemID, date and poster_username are set automatically.
        """
        username = UserCurrent.get_current_user_id()
        if not username:
            raise RuntimeError("No user logged in; cannot create item.")

        # ensure all category keys exist and are ints
        flags = {
            "cat_electronics": int(bool(categories.get("cat_electronics", 0))),
            "cat_books": int(bool(categories.get("cat_books", 0))),
            "cat_sports": int(bool(categories.get("cat_sports", 0))),
            "cat_clothes": int(bool(categories.get("cat_clothes", 0))),
            "cat_toys": int(bool(categories.get("cat_toys", 0))),
            "cat_decor": int(bool(categories.get("cat_decor", 0))),
            "cat_furnitture": int(bool(categories.get("cat_furnitture", 0))),
        }

        today = date.today()
        conn = None
        try:
            conn = InventoryDatabase._connect()
            cur = conn.cursor()
            # Determine next itemID if the table is not AUTO_INCREMENT
            cur.execute("SELECT MAX(itemID) FROM item")
            row = cur.fetchone()
            max_id = row[0] if row and row[0] is not None else 0
            next_id = int(max_id) + 1

            cur.execute(
                "INSERT INTO item (itemID, title, description, date, price, poster_username, "
                "cat_electronics, cat_books, cat_sports, cat_clothes, cat_toys, cat_decor, cat_furnitture) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    next_id,
                    name,
                    description[:200] if description else "",  # enforce column length
                    today,
                    float(price) if price is not None else 0.0,
                    username,
                    flags["cat_electronics"],
                    flags["cat_books"],
                    flags["cat_sports"],
                    flags["cat_clothes"],
                    flags["cat_toys"],
                    flags["cat_decor"],
                    flags["cat_furnitture"],
                ),
            )
            conn.commit()
        finally:
            if conn:
                conn.close()


class UserPage(tk.Frame):
    '''
    UserPage

    UserPage class is responsible for displaying the items and user information
    posted by the currently logged-in user.
    '''

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.items_frame = None

    def refresh_items(self):
        """Refresh the page when user logs in."""
        for widget in self.winfo_children():
            widget.destroy()

        # enforce a standard window size so layout is predictable
        try:
            if hasattr(self.controller, "geometry"):
                self.controller.geometry("900x650")
            if hasattr(self.controller, "minsize"):
                self.controller.minsize(700, 480)
        except Exception:
            pass

        # top navigation buttons (moved to top to fix layout issue)
        top_frame = tk.Frame(self)
        top_frame.pack(side="top", fill="x", pady=6)
        tk.Button(top_frame, text='Log Out', width=15,
                  command=lambda: (UserCurrent.clear(), self.controller.show_frame("SignInPage"))).pack(side="left", padx=8)
        tk.Button(top_frame, text='Add New Item', width=15,
                  command=self.prompt_new_item).pack(side="left", padx=8)
        tk.Button(top_frame, text='Home Page', width=15,
                  command=lambda: self.controller.show_frame("HomePage")).pack(side="right", padx=8)

        username = UserCurrent.get_current_user_id()

        if not username:
            messagebox.showwarning("Error", "No user logged in.")
            self.controller.show_frame("SignInPage")
            return

        # Create title
        title = tk.Label(self, text=f"Your Items", bg="#195379", fg="white",
                         font=("Times New Roman", 20), anchor="center")
        title.pack(fill="x", side="top")

        # Create scrollable area
        scroll_container = tk.Frame(self, bg="#2a6cc8")
        scroll_container.pack(side="top", fill="both", expand=True)

        canvas = tk.Canvas(scroll_container, bg="#205fb7", highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)

        center_area = tk.Frame(canvas, bg="#195379")
        canvas_window = canvas.create_window((0, 0), window=center_area, anchor="nw")

        for i in range(2):
            center_area.columnconfigure(i, weight=1, uniform="col")
            center_area.rowconfigure(i, weight=1, uniform="row")

        items = InventoryDatabase.get_items_with_username(username)

        if items:
            for i, item in enumerate(items):
                # only show title and price per request
                self.User_post(center_area, item.title, item.price,
                               row=i // 2, col=i % 2, item=item)
        else:
            no_items_label = tk.Label(center_area, text="No items found.", font=("Times New Roman", 12))
            no_items_label.grid(row=0, column=0, pady=20)

        def update_scroll_region(event=None):
            # keep canvas window width in sync and update scrollregion
            try:
                canvas.itemconfig(canvas_window, width=canvas.winfo_width())
                canvas.configure(scrollregion=canvas.bbox("all"))
            except Exception:
                pass

        center_area.bind("<Configure>", update_scroll_region)
        canvas.bind("<Configure>", update_scroll_region)

    def User_post(self, parent, caption, price, row, col, item=None):
        frame = ttk.Frame(parent, padding=10)
        frame.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
        frame.columnconfigure(0, weight=1)

        # Title
        text_label = ttk.Label(frame, text=caption, font=("Times New Roman", 15), wraplength=200)
        text_label.grid(row=0, column=0, sticky="n", pady=(0, 5))

        # Price in larger text
        price_text = f"${price}" if price is not None else "N/A"
        price_label = ttk.Label(frame, text=price_text, font=("Times New Roman", 14, "bold"), wraplength=200)
        price_label.grid(row=1, column=0, sticky="s")

        frame.bind("<Button-1>", lambda event, item=item: self._open_item_popup(item))
        frame.configure(cursor="hand2")

    def _open_item_popup(self, item):
        from A2_item_info_popup import ItemInfoPopup
        ItemInfoPopup(self, item)

    def prompt_new_item(self):
        """Open a dialog to collect new item details and add to InventoryDatabase."""
        username = UserCurrent.get_current_user_id()
        if not username:
            messagebox.showwarning("Error", "No user logged in.")
            self.controller.show_frame("SignInPage")
            return

        dlg = tk.Toplevel(self)
        dlg.title("Add New Item")
        dlg.grab_set()

        ttk.Label(dlg, text="Title:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        title_var = tk.StringVar()
        ttk.Entry(dlg, textvariable=title_var, width=40).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(dlg, text="Price:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        price_var = tk.StringVar()
        ttk.Entry(dlg, textvariable=price_var, width=20).grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Category checkboxes (multiple allowed)
        ttk.Label(dlg, text="Categories:").grid(row=2, column=0, sticky="ne", padx=5, pady=5)
        cats_frame = ttk.Frame(dlg)
        cats_frame.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        elect_var = tk.IntVar()
        books_var = tk.IntVar()
        sports_var = tk.IntVar()
        clothes_var = tk.IntVar()
        toys_var = tk.IntVar()
        decor_var = tk.IntVar()
        furn_var = tk.IntVar()

        ttk.Checkbutton(cats_frame, text="Electronics", variable=elect_var).grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(cats_frame, text="Books", variable=books_var).grid(row=0, column=1, sticky="w")
        ttk.Checkbutton(cats_frame, text="Sports", variable=sports_var).grid(row=0, column=2, sticky="w")
        ttk.Checkbutton(cats_frame, text="Clothes", variable=clothes_var).grid(row=1, column=0, sticky="w")
        ttk.Checkbutton(cats_frame, text="Toys", variable=toys_var).grid(row=1, column=1, sticky="w")
        ttk.Checkbutton(cats_frame, text="Decor", variable=decor_var).grid(row=1, column=2, sticky="w")
        ttk.Checkbutton(cats_frame, text="Furniture", variable=furn_var).grid(row=2, column=0, sticky="w")

        ttk.Label(dlg, text="Description:").grid(row=3, column=0, sticky="ne", padx=5, pady=5)
        desc_text = tk.Text(dlg, width=40, height=6)
        desc_text.grid(row=3, column=1, padx=5, pady=5)

        def on_save():
            title = title_var.get().strip()
            price_s = price_var.get().strip()
            description = desc_text.get("1.0", "end").strip()

            if not title:
                messagebox.showwarning("Validation", "Title is required.")
                return
            try:
                price = float(price_s) if price_s else 0.0
            except ValueError:
                messagebox.showwarning("Validation", "Price must be a number.")
                return

            categories = {
                "cat_electronics": elect_var.get(),
                "cat_books": books_var.get(),
                "cat_sports": sports_var.get(),
                "cat_clothes": clothes_var.get(),
                "cat_toys": toys_var.get(),
                "cat_decor": decor_var.get(),
                "cat_furnitture": furn_var.get(),
            }

            try:
                InventoryDatabase.create_new_item(title, description, price, categories)
            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to add item: {e}")
                return
            finally:
                dlg.destroy()
                self.refresh_items()
                # Get the HomePage frame and refresh it
                home_page = getattr(self.controller, "frames", {}).get("HomePage")
                if home_page and hasattr(home_page, "update_items"):
                    home_page.update_items()

        btn_frame = ttk.Frame(dlg)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Save", command=on_save).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dlg.destroy).pack(side="left", padx=5)