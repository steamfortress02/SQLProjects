import tkinter as tk
from tkinter import ttk
from A1_signin import SignInPage
from A1_signup import SignUpPage
from DashboardPage import DashboardPage

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Online Marketplace")
        self.geometry("500x600")
        self.resizable(False, False)

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        self.frames = {}
        for FrameClass in (SignInPage, SignUpPage, DashboardPage):
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
        dash_page = self.frames.get("DashboardPage")
        if dash_page:
            dash_page.set_user_details(user_data)

if __name__ == "__main__":
    app = App()
    app.mainloop()