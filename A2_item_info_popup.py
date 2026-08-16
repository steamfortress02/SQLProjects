import tkinter as tk
from tkinter import ttk, messagebox
from A1_signin import UserCurrent
from A2_user_page import InventoryDatabase


class ItemInfoPopup(tk.Toplevel):
    def __init__(self, parent, item):
        super().__init__(parent)
        self.title("Item Details")
        self.transient(parent)
        self.grab_set()

        self.item = item
        self.current_user = UserCurrent.get_current_user_id()
        self.is_poster = bool(self.current_user and self.current_user == item.poster_username)

        self.geometry("420x300")
        self.resizable(False, False)

        main = ttk.Frame(self, padding=16)
        main.pack(fill="both", expand=True)

        ttk.Label(main, text=item.title, font=("Times New Roman", 18, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 10)
        )

        ttk.Label(main, text="Price:").grid(row=1, column=0, sticky="w", padx=(0, 12), pady=6)
        ttk.Label(main, text=f"${item.price}", font=("Times New Roman", 14, "bold")).grid(
            row=1, column=1, sticky="w", pady=6
        )

        ttk.Label(main, text="Posted by:").grid(row=2, column=0, sticky="w", padx=(0, 12), pady=6)
        ttk.Label(main, text=item.poster_username).grid(row=2, column=1, sticky="w", pady=6)

        ttk.Label(main, text="Description:").grid(row=3, column=0, sticky="nw", padx=(0, 12), pady=6)
        desc = tk.Text(main, width=32, height=6, wrap="word", state="disabled")
        desc.grid(row=3, column=1, sticky="nsew", pady=6)
        desc.configure(state="normal")
        desc.insert("1.0", item.description or "No description provided.")
        desc.configure(state="disabled")

        button_row = ttk.Frame(main)
        button_row.grid(row=4, column=0, columnspan=2, pady=(12, 0), sticky="e")

        if self.is_poster:
            ttk.Button(button_row, text="Update Price", command=self.update_price).pack(side="left", padx=(0, 8))
            ttk.Button(button_row, text="Delete Item", command=self.delete_item).pack(side="left", padx=(0, 8))
            ttk.Button(button_row, text="Close", command=self.destroy).pack(side="left")
        else:
            ttk.Button(button_row, text="Leave Review", command=self.leave_review).pack(side="left", padx=(0, 8))
            ttk.Button(button_row, text="Close", command=self.destroy).pack(side="left")

    def update_price(self):
        if not self.current_user:
            messagebox.showwarning("Error", "No user logged in.")
            return

        if self.current_user != self.item.poster_username:
            messagebox.showwarning("Error", "Only the item poster can update the price.")
            return

        dlg = tk.Toplevel(self)
        dlg.title("Update Price")
        dlg.transient(self)
        dlg.grab_set()

        ttk.Label(dlg, text="New Price:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        price_var = tk.StringVar(value=str(self.item.price))
        ttk.Entry(dlg, textvariable=price_var, width=20).grid(row=0, column=1, padx=10, pady=10)

        def save_price():
            try:
                new_price = float(price_var.get())
                if new_price < 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Invalid Price", "Please enter a valid non-negative number.")
                return

            try:
                conn = InventoryDatabase._connect()
                cur = conn.cursor()
                cur.execute(
                    "UPDATE item SET price = %s WHERE itemID = %s AND poster_username = %s",
                    (new_price, self.item.itemID, self.current_user),
                )
                conn.commit()
                if cur.rowcount == 0:
                    raise RuntimeError("Price update failed.")
                messagebox.showinfo("Success", "Price updated successfully.")
                dlg.destroy()
                self.destroy()
            except Exception as exc:
                messagebox.showerror("Error", f"Failed to update price: {exc}")
            finally:
                if 'conn' in locals():
                    conn.close()

        ttk.Button(dlg, text="Save", command=save_price).grid(row=1, column=0, columnspan=2, pady=(0, 10))

    def delete_item(self):
        if not self.current_user:
            messagebox.showwarning("Error", "No user logged in.")
            return

        if self.current_user != self.item.poster_username:
            messagebox.showwarning("Error", "Only the item poster can delete this item.")
            return

        confirm = messagebox.askyesno("Delete Item", f"Delete '{self.item.title}'? This cannot be undone.")
        if not confirm:
            return

        try:
            conn = InventoryDatabase._connect()
            cur = conn.cursor()
            cur.execute(
                "DELETE FROM item WHERE itemID = %s AND poster_username = %s",
                (self.item.itemID, self.current_user),
            )
            conn.commit()

            if cur.rowcount == 0:
                messagebox.showerror("Error", "Item could not be deleted.")
                return

            messagebox.showinfo("Success", "Item deleted successfully.")
            self.destroy()
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to delete item: {exc}")
        finally:
            if 'conn' in locals():
                conn.close()

    def leave_review(self):
        if not self.current_user:
            messagebox.showwarning("Error", "Please sign in to leave a review.")
            return

        if self.current_user == self.item.poster_username:
            messagebox.showwarning("Error", "You cannot review your own item.")
            return

        dlg = tk.Toplevel(self)
        dlg.title("Leave Review")
        dlg.transient(self)
        dlg.grab_set()

        ttk.Label(dlg, text="Rating:").grid(row=0, column=0, padx=10, pady=8, sticky="w")
        rating_var = tk.StringVar(value="Good")
        rating_box = ttk.Combobox(dlg, textvariable=rating_var, values=["Excellent", "Good", "Fair", "Poor"], state="readonly", width=18)
        rating_box.grid(row=0, column=1, padx=10, pady=8, sticky="ew")

        ttk.Label(dlg, text="Comment:").grid(row=1, column=0, padx=10, pady=8, sticky="nw")
        comment = tk.Text(dlg, width=32, height=6)
        comment.grid(row=1, column=1, padx=10, pady=8)

        def submit_review():
            rating = rating_var.get().strip()
            review_text = comment.get("1.0", "end").strip()

            if not rating:
                messagebox.showwarning("Validation", "Please select a rating.")
                return

            try:
                conn = InventoryDatabase._connect()
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO review (itemID, username, rating, comment, date) VALUES (%s, %s, %s, %s, %s)",
                    (self.item.itemID, self.current_user, rating, review_text, __import__('datetime').date.today()),
                )
                conn.commit()
                messagebox.showinfo("Success", "Review submitted successfully.")
                dlg.destroy()
                self.destroy()
            except Exception as exc:
                messagebox.showerror("Error", f"Unable to leave review: {exc}")
            finally:
                if 'conn' in locals():
                    conn.close()

        ttk.Button(dlg, text="Submit Review", command=submit_review).grid(row=2, column=0, columnspan=2, pady=(0, 10))
