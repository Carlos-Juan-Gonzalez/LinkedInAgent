import asyncio
import tkinter as tk
from tkinter import messagebox
from src.graph import Graph
from src.scrapping.posting import create_post
from src.scrapping.scrapping import get_impressions
from src.mongoDB import set_posts_impressions, get_last_series_id, set_posts, get_last_post_id

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Control de Impresiones y Post")
        self.root.geometry("600x400")

        self.btn_set_impressions = tk.Button(root, text="Actualizar impresiones", command=self.run_set_impressions)
        self.btn_set_impressions.pack(pady=5)

        self.btn_run_graph = tk.Button(root, text="Correr Graph", command=self.run_graph)
        self.btn_run_graph.pack(pady=5)

        self.text_post = tk.Text(root, width=70, height=10)
        self.text_post.pack(pady=10)

        self.frame_buttons = tk.Frame(root)
        self.frame_buttons.pack(pady=5)

        self.btn_aceptar = tk.Button(self.frame_buttons, text="Aceptar", command=self.aceptar, state=tk.DISABLED)
        self.btn_aceptar.grid(row=0, column=0, padx=10)

        self.btn_rechazar = tk.Button(self.frame_buttons, text="Rechazar", command=self.rechazar, state=tk.DISABLED)
        self.btn_rechazar.grid(row=0, column=1, padx=10)

        self.final_state = None

    def run_set_impressions(self):
        self.btn_set_impressions.config(state=tk.DISABLED)
        self.btn_run_graph.config(state=tk.DISABLED)
        self.text_post.delete("1.0", tk.END)
        self.text_post.insert(tk.END, "Actualizando impresiones, por favor espera...")
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
        self.text_post.delete("1.0", tk.END)
        self.btn_set_impressions.config(state=tk.NORMAL)
        self.btn_run_graph.config(state=tk.NORMAL)

    def run_graph(self):
        self.btn_set_impressions.config(state=tk.DISABLED)
        self.btn_run_graph.config(state=tk.DISABLED)
        self.text_post.delete("1.0", tk.END)
        self.text_post.insert(tk.END, "Ejecutando graph, por favor espera...")
        self.root.update()

        graph = Graph()
        final_state = graph.run()

        self.post = final_state.post
        self.topic = final_state.topic
        self.series_id = get_last_series_id() if final_state.position != "StandAlone" else None

        self.text_post.delete("1.0", tk.END)
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
        self.text_post.delete("1.0", tk.END)
        self.text_post.insert(tk.END, "Creando post, por favor espera...")
        self.root.update()

        async def wrapper():
            await create_post(texto)
            
        
        asyncio.run(wrapper())

        set_posts((get_last_post_id() + 1), texto, self.topic, self.series_id)

        messagebox.showinfo("Info", "Post creado correctamente.")
        self.text_post.delete("1.0", tk.END)
        self.btn_aceptar.config(state=tk.NORMAL)
        self.btn_rechazar.config(state=tk.NORMAL)

    def rechazar(self):
        self.text_post.delete("1.0", tk.END)
        messagebox.showinfo("Info", "Post borrado.")
        self.btn_aceptar.config(state=tk.DISABLED)
        self.btn_rechazar.config(state=tk.DISABLED)
        self.root.update()

def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
