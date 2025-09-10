import tkinter as tk
from tkinter import messagebox
from src.env_validator import validate_variables

class ConfigView:
    def __init__(self, root, callback):
        self.root = root
        self.callback = callback
        self.config_window = tk.Toplevel(self.root)
        self.config_window.title("Configuration")
        self.config_window.geometry("400x400")
        self.config_window.resizable(False, False)

        var_openai = tk.StringVar()
        var_mongo = tk.StringVar()
        var_url = tk.StringVar()

        self.label_openAI = tk.Label(self.config_window, text="OpenAI API Key:")
        self.label_openAI.pack(pady=10)

        self.entry_openAi = tk.Entry(self.config_window, textvariable=var_openai, width=50)
        self.entry_openAi.pack(pady=10)

        self.label_mongo = tk.Label(self.config_window, text="MongoDB Connection String:")
        self.label_mongo.pack(pady=10)

        self.entry_mongo = tk.Entry(self.config_window, textvariable=var_mongo, width=50)
        self.entry_mongo.pack(pady=10)

        self.label_url = tk.Label(self.config_window, text="Linkedin Profile URL:")
        self.label_url.pack(pady=10)

        self.entry_url = tk.Entry(self.config_window, textvariable=var_url, width=50)
        self.entry_url.pack(pady=10)

        self.btn_set_config = tk.Button(self.config_window, text="OK", command=self.set_config, state=tk.DISABLED)
        self.btn_set_config.pack(pady=20)

        def check_fields(*args):
            if var_openai.get() and var_mongo.get() and var_url.get():
                self.btn_set_config.config(state=tk.NORMAL)
            else:
                self.btn_set_config.config(state=tk.DISABLED)

        var_openai.trace_add("write", check_fields)
        var_mongo.trace_add("write", check_fields)
        var_url.trace_add("write", check_fields)

        self.config_window.grab_set()
        self.config_window.transient(self.root)

    def set_config(self):
        results = validate_variables(self.entry_openAi.get(), self.entry_mongo.get(), self.entry_url.get())
        if results["openai"] and results["mongo"] and results["url"]:
            self._write_env_variables()
            self.callback()
            self.config_window.destroy()
        else:
            if not results["openai"]:
                messagebox.showinfo("OpenAI Key Error", "The OpenAI API key is not valid or is wrong formatted.")
            if not results["mongo"]:
                messagebox.showinfo("Mongo URI Error", "The Mongo URI is not valid or is wrong formatted.")
            if not results["url"]:
                messagebox.showinfo("LinkedIn URL Error", "The LinkedIn URL is not valid or is wrong formatted.")

    def _write_env_variables(self):
        linkedin_url = self.entry_url.get()
        if not linkedin_url.endswith("/"):
            linkedin_url += "/"
        with open(".env", "w") as file:
            file.write(f"OPENAI_API_KEY=\"{self.entry_openAi.get()}\"\n")
            file.write(f"MONGODB_URI=\"{self.entry_mongo.get()}\"\n")
            file.write(f"LINKEDIN_MAIN_PAGE=\"{linkedin_url}\"\n")
            file.write(f"LINKEDIN_FEED_PAGE=\"{linkedin_url}recent-activity/all/\"")