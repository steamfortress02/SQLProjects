import tkinter as tk
from tkinter import ttk, messagebox
from A2_user_page import InventoryDatabase
from A1_signin import UserCurrent


class HomePage(tk.Frame):
    """Homepage showing all items with simple filters and navigation."""

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Top controls (logout, userpage) and filters
        top_frame = tk.Frame(self)
        top_frame.pack(side="top", fill="x", pady=6)

        tk.Button(top_frame, text='Log Out', width=12,
                  command=lambda: (UserCurrent.clear(), self.controller.show_frame("SignInPage"))).pack(side="left", padx=6)
        tk.Button(top_frame, text='User Page', width=12,
                  command=lambda: self.controller.show_frame("UserPage")).pack(side="left", padx=6)

        filter_frame = tk.Frame(top_frame)
        filter_frame.pack(side="right", padx=8)

        tk.Label(filter_frame, text="Category:").pack(side="left")
        self.category_var = tk.StringVar(value="All")
        categories = ["All", "Electronics", "Books", "Sports", "Clothes", "Toys", "Decor", "Furniture"]
        self.cat_combo = ttk.Combobox(filter_frame, textvariable=self.category_var, values=categories, state="readonly", width=12)
        self.cat_combo.pack(side="left", padx=(4, 8))

        tk.Label(filter_frame, text="Min $").pack(side="left")
        self.min_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.min_var, width=8).pack(side="left", padx=4)
        tk.Label(filter_frame, text="Max $").pack(side="left")
        self.max_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.max_var, width=8).pack(side="left", padx=4)

        tk.Button(filter_frame, text="Apply", command=self.refresh_items).pack(side="left", padx=6)

        title = tk.Label(self, text="All Items", bg="#195379", fg="white",
                         font=("Times New Roman", 20), anchor="center")
        title.pack(fill="x", side="top")

        self.scroll_container = tk.Frame(self, bg="#2a6cc8")
        self.scroll_container.pack(side="top", fill="both", expand=True)

        self.canvas = tk.Canvas(self.scroll_container, bg="#205fb7", highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar = tk.Scrollbar(self.scroll_container, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.center_area = tk.Frame(self.canvas, bg="#195379")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.center_area, anchor="nw")

        # make two responsive columns like UserPage
        for i in range(2):
            self.center_area.columnconfigure(i, weight=1, uniform="col")
            self.center_area.rowconfigure(i, weight=1, uniform="row")

        self.center_area.bind("<Configure>", self._update_scroll)
        self.canvas.bind("<Configure>", self._update_scroll)

        # Refresh when this frame is shown (mapped)
        self.bind("<Map>", lambda e: self.refresh_items(ignore_filters=True))
        # initial load
        self.refresh_items(ignore_filters=True)

    def _update_scroll(self, event=None):
        try:
            self.canvas.itemconfig(self.canvas_window, width=self.canvas.winfo_width())
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        except Exception:
            pass

    def refresh_items(self, ignore_filters=False):
        # Clear content
        for w in self.center_area.winfo_children():
            w.destroy()

        # Load all items then filter
        # Determine filters and fetch from DB using SQL
        if ignore_filters:
            cat = None
            minp = None
            maxp = None
        else:
            cat = self.category_var.get() if hasattr(self, 'category_var') else None
            try:
                minp = float(self.min_var.get()) if self.min_var.get().strip() else None
            except Exception:
                minp = None
            try:
                maxp = float(self.max_var.get()) if self.max_var.get().strip() else None
            except Exception:
                maxp = None

        items = InventoryDatabase.get_all_items(category=cat, min_price=minp, max_price=maxp)
        filtered = items

        if not filtered:
            tk.Label(self.center_area, text="No items found.", font=("Times New Roman", 12), bg="#195379").grid(row=0, column=0, pady=20)
            return

        for i, item in enumerate(filtered):
            # match UserPage card layout and sizing: ttk.Frame with padding, wraplength=200
            frame = ttk.Frame(self.center_area, padding=10)
            frame.grid(row=i // 2, column=i % 2, sticky="nsew", padx=5, pady=5)
            frame.columnconfigure(0, weight=1)

            text_label = ttk.Label(frame, text=item.title, font=("Times New Roman", 15), wraplength=200)
            text_label.grid(row=0, column=0, sticky="n", pady=(0, 5))

            price_text = f"${item.price}" if item.price is not None else 'N/A'
            price_label = ttk.Label(frame, text=price_text, font=("Times New Roman", 14, "bold"), wraplength=200)
            price_label.grid(row=1, column=0, sticky="s")

            poster_label = ttk.Label(frame, text=f"By: {item.poster_username}", font=("Times New Roman", 9))
            poster_label.grid(row=2, column=0, sticky="s")

            frame.bind("<Button-1>", lambda event, item=item: self._open_item_popup(item))
            frame.configure(cursor="hand2")

    def _open_item_popup(self, item):
        from A2_item_info_popup import ItemInfoPopup
        ItemInfoPopup(self, item)
