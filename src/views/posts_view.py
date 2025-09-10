import tkinter as tk

class PostsView:
    def __init__(self, root, callback):
        self.root = root
        self.callback = callback
        self.config_window = tk.Toplevel(self.root)
        self.config_window.title("Configuration")
        self.config_window.geometry("400x400")
        self.config_window.resizable(False, False)