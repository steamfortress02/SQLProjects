import tkinter as tk
from tkinter import ttk
from A1_signin import SignInPage
from A1_signup import SignUpPage
from A2_user_page import UserPage
from A2_home_page import HomePage

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sign In")
        self.geometry("900x650")
        self.minsize(700, 480)

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        self.frames = {}
        # Load and stack frames
        for FrameClass in (SignInPage, SignUpPage, UserPage, HomePage):
            page_name = FrameClass.__name__
            frame = FrameClass(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("SignInPage")

    def show_frame(self, page_name):
        frame = self.frames.get(page_name)
        if frame:
            frame.tkraise()

    def set_user_details(self, user_data):
        user_page = self.frames.get("UserPage")
        if user_page:
            user_page.set_user_details(user_data)

if __name__ == "__main__":
    app = App()
    app.mainloop()