import asyncio
import tkinter as tk
from tkinter import messagebox
from src.graph import Graph
from src.scrapping.posting import create_post
from src.scrapping.scrapping import get_impressions
from src.mongoDB import set_posts_impressions, get_last_series_id, set_posts, get_last_post_id
from src.env_validator import validate_variables

class View:
    def __init__(self, root):
        self.root = root
        self.root.title("Control de Impresiones y Post")
        self.root.geometry("750x600")

        self.btn_set_impressions = tk.Button(root, text="Actualizar impresiones", command=self.run_set_impressions)
        self.btn_set_impressions.pack(pady=5)

        self.btn_run_graph = tk.Button(root, text="Correr Graph", command=self.run_graph)
        self.btn_run_graph.pack(pady=5)

        self.text_post = tk.Text(root, width=70, height=25)
        self.text_post.config(state=tk.DISABLED)
        self.text_post.pack(pady=10)

        self.frame_buttons = tk.Frame(root)
        self.frame_buttons.pack(pady=5)

        self.btn_aceptar = tk.Button(self.frame_buttons, text="Aceptar", command=self.aceptar, state=tk.DISABLED)
        self.btn_aceptar.grid(row=0, column=0, padx=10)

        self.btn_rechazar = tk.Button(self.frame_buttons, text="Rechazar", command=self.rechazar, state=tk.DISABLED)
        self.btn_rechazar.grid(row=0, column=1, padx=10)

        self.frame_config = tk.Frame(root)
        self.frame_config.pack(side="right",anchor="s")

        self.btn_config = tk.Button(self.frame_config, text="config", command=self.config)
        self.btn_config.pack(padx=10,pady=10)

        self.final_state = None

    def run_set_impressions(self):
        self.btn_set_impressions.config(state=tk.DISABLED)
        self.btn_run_graph.config(state=tk.DISABLED)
        self.insertInfo("Actualizando impresiones, por favor espera...")
        self.root.update()

        async def wrapper():
            data = await get_impressions()
            for post in data:
                post_content = post["post"]
                num_impressions = post["impressions"][0]["num_impressions"]
                date = post["impressions"][0]["date"]
                set_posts_impressions(post_content, num_impressions, date)
        
        asyncio.run(wrapper())

        messagebox.showinfo("Info", "Impresiones actualizadas correctamente.")
        self.insertInfo("")
        self.btn_set_impressions.config(state=tk.NORMAL)
        self.btn_run_graph.config(state=tk.NORMAL)

    def run_graph(self):
        self.btn_set_impressions.config(state=tk.DISABLED)
        self.btn_run_graph.config(state=tk.DISABLED)
        self.insertInfo("")
        self.insertInfo("Ejecutando graph, por favor espera...")
        self.root.update()

        graph = Graph()
        final_state = graph.run()

        self.post = final_state.post
        self.topic = final_state.topic
        self.series_id = get_last_series_id() if final_state.position != "StandAlone" else None

        self.insertInfo("")
        self.text_post.config(state=tk.NORMAL)
        self.text_post.insert(tk.END, self.post)

        self.btn_aceptar.config(state=tk.NORMAL)
        self.btn_rechazar.config(state=tk.NORMAL)
        self.btn_set_impressions.config(state=tk.NORMAL)
        self.btn_run_graph.config(state=tk.NORMAL)

    def aceptar(self):
        texto = self.text_post.get("1.0", tk.END).strip()
        if not texto:
            messagebox.showwarning("Aviso", "El texto del post está vacío.")
            return
        
        self.btn_aceptar.config(state=tk.DISABLED)
        self.btn_rechazar.config(state=tk.DISABLED)
        self.insertInfo("")
        self.insertInfo("Creando post, por favor espera...")
        self.root.update()

        async def wrapper():
            await create_post(texto)
            
        
        asyncio.run(wrapper())

        set_posts((get_last_post_id() + 1), texto, self.topic, self.series_id)

        messagebox.showinfo("Info", "Post creado correctamente.")
        self.insertInfo("")
        self.btn_aceptar.config(state=tk.NORMAL)
        self.btn_rechazar.config(state=tk.NORMAL)

    def rechazar(self):
        self.insertInfo("")
        messagebox.showinfo("Info", "Post borrado.")
        self.btn_aceptar.config(state=tk.DISABLED)
        self.btn_rechazar.config(state=tk.DISABLED)
        self.text_post.config(tk.DISABLED)
        self.root.update()

    def config(self):
        self.config_window = tk.Toplevel(self.root)
        self.config_window.title("Configuration")
        self.config_window.geometry("400x500")
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
        self.root.wait_window(self.config_window)

    def set_config(self):
        results = validate_variables(self.entry_openAi.get(),self.entry_mongo.get(),self.entry_url.get())
        if results["openai"] == True and results["mongo"] == True and results["url"] == True:
            print("Estan todas correctas")
        else:
            if results["openai"] != True:
                messagebox.showinfo("Openai key error", "The OpenAI API key is not valid or is wrong formatted.")
            if results["mongo"] != True:
                messagebox.showinfo("Mongo uri error", "The Mongo uri is not valid or is wrong formatted.")
            if results["url"] != True:
                messagebox.showinfo("LinkedIn url error", "The LinkedIn url is not valid or is wrong formatted.")


    def insertInfo(self,info):
        self.text_post.config(state=tk.NORMAL)
        if info:
            self.text_post.insert("1.0",info)
        else:
            self.text_post.delete("1.0",tk.END)
        self.text_post.config(state=tk.DISABLED)

def runView():
    root = tk.Tk()
    view = View(root)
    root.mainloop()
