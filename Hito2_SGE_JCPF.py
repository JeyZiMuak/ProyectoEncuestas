import tkinter as tk
from tkinter import ttk, messagebox, Menu
import mysql.connector
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Función para conectar a la base de datos
def connect_db():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="campusfp",
            database="ENCUESTAS"
        )
    except mysql.connector.Error as e:
        messagebox.showerror("Error de Conexión", str(e))
        return None

# Clase principal de la aplicación
class EncuestaApp(tk.Tk):
    def create_menu(self):
        # Crear barra de menú
        menu_bar = Menu(self)
        self.config(menu=menu_bar)

        # Menú de operaciones
        operaciones_menu = Menu(menu_bar, tearoff=0)
        operaciones_menu.add_command(label="Agregar Encuesta", command=self.add_encuesta)
        operaciones_menu.add_command(label="Actualizar Encuesta", command=self.update_encuesta)
        operaciones_menu.add_command(label="Eliminar Encuesta", command=self.delete_encuesta)
        menu_bar.add_cascade(label="Operaciones", menu=operaciones_menu)

        # Menú de consultas
        consultas_menu = Menu(menu_bar, tearoff=0)
        consultas_menu.add_command(label="Consulta por Edad", command=self.query_by_age)
        consultas_menu.add_command(label="Filtrar por Sexo", command=self.filter_by_gender)
        consultas_menu.add_command(label="Perdidas de Control > 3", command=self.filter_loss_of_control)
        menu_bar.add_cascade(label="Consultas", menu=consultas_menu)

        # Menú de exportación y gráficos
        extras_menu = Menu(menu_bar, tearoff=0)
        extras_menu.add_command(label="Exportar a Excel", command=self.export_to_excel)
        extras_menu.add_command(label="Mostrar Gráficos", command=self.show_graph)
        menu_bar.add_cascade(label="Extras", menu=extras_menu)

    def create_widgets(self):
        # Frame para tabla de datos
        self.tree = ttk.Treeview(self, columns=("id", "edad", "sexo", "bebidas", "cervezas", "vinos", "tensionAlta", "dolorCabeza"), 
                                 show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("edad", text="Edad")
        self.tree.heading("sexo", text="Sexo")
        self.tree.heading("bebidas", text="Bebidas/Semana")
        self.tree.heading("cervezas", text="Cervezas/Semana")
        self.tree.heading("vinos", text="Vinos/Semana")
        self.tree.heading("tensionAlta", text="Tensión Alta")
        self.tree.heading("dolorCabeza", text="Dolor de Cabeza")
        self.tree.pack(fill="both", expand=True)

        # Botón para cargar encuestas al iniciar
        self.view_encuestas()

    def view_encuestas(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT idEncuesta, edad, Sexo, BebidasSemana, CervezasSemana, VinosSemana, TensionAlta, DolorCabeza FROM ENCUESTA")
            rows = cursor.fetchall()
            for row in rows:
                self.tree.insert("", tk.END, values=row)
            conn.close()

    def add_encuesta(self):
        self.input_window("Agregar Encuesta", self.insert_data)

    def insert_data(self, edad, sexo, bebidas, cervezas, vinos, tensionAlta, dolorCabeza):
        try:
            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                query = """INSERT INTO ENCUESTA (edad, Sexo, BebidasSemana, CervezasSemana, VinosSemana, TensionAlta, DolorCabeza) 
                           VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(query, (edad, sexo, bebidas, cervezas, vinos, tensionAlta, dolorCabeza))
                conn.commit()
                conn.close()
                messagebox.showinfo("Éxito", "Encuesta agregada correctamente.")
                self.view_encuestas()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_encuesta(self):
        selected_item = self.tree.selection()
        if selected_item:
            item = self.tree.item(selected_item)
            encuesta_id = item["values"][0]
            self.input_window("Actualizar Encuesta", lambda *args: self.update_data(encuesta_id, *args), item["values"])

    def update_data(self, encuesta_id, edad, sexo, bebidas, cervezas, vinos, tensionAlta, dolorCabeza):
        try:
            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                query = """UPDATE ENCUESTA SET edad=%s, Sexo=%s, BebidasSemana=%s, CervezasSemana=%s, 
                           VinosSemana=%s, TensionAlta=%s, DolorCabeza=%s WHERE idEncuesta=%s"""
                cursor.execute(query, (edad, sexo, bebidas, cervezas, vinos, tensionAlta, dolorCabeza, encuesta_id))
                conn.commit()
                conn.close()
                messagebox.showinfo("Éxito", "Encuesta actualizada correctamente.")
                self.view_encuestas()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_encuesta(self):
        selected_item = self.tree.selection()
        if selected_item:
            try:
                item = self.tree.item(selected_item)
                encuesta_id = item["values"][0]
                conn = connect_db()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM ENCUESTA WHERE idEncuesta=%s", (encuesta_id,))
                    conn.commit()
                    conn.close()
                    self.tree.delete(selected_item)
                    messagebox.showinfo("Éxito", "Encuesta eliminada correctamente.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def query_by_age(self):
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ENCUESTA WHERE edad > 20")
            result = cursor.fetchall()
            messagebox.showinfo("Consulta", f"Total de encuestas mayores de 20 años: {len(result)}")
            conn.close()

    def filter_by_gender(self):
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ENCUESTA WHERE Sexo='Mujer'")
            result = cursor.fetchall()
            messagebox.showinfo("Consulta", f"Encuestas realizadas por mujeres: {len(result)}")
            conn.close()

    def filter_loss_of_control(self):
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ENCUESTA WHERE PerdidasControl > 3")
            result = cursor.fetchall()
            messagebox.showinfo("Consulta", f"Encuestados con más de 3 pérdidas de control: {len(result)}")
            conn.close()

    def export_to_excel(self):
        try:
            conn = connect_db()
            if conn:
                cursor = conn.cursor()

                # Realizar la consulta
                cursor.execute("SELECT * FROM ENCUESTA")
                rows = cursor.fetchall()

                # Verificar si se obtuvieron datos
                if not rows:
                    messagebox.showwarning("Advertencia", "No hay datos para exportar.")
                    conn.close()
                    return

                # Obtener nombres de columnas
                columns = [desc[0] for desc in cursor.description]
                print(f"Columnas: {columns}")  # Depuración

                # Crear un DataFrame
                df = pd.DataFrame(rows, columns=columns)
                print(f"Datos exportados:\n{df}")  # Depuración

                # Exportar a Excel
                df.to_excel("encuestas_exportadas.xlsx", index=False, engine="openpyxl")
                conn.close()
                messagebox.showinfo("Éxito", "Datos exportados a Excel con éxito.")
            else:
                messagebox.showerror("Error", "No se pudo conectar a la base de datos.")
        except Exception as e:
            messagebox.showerror("Error", f"Error durante la exportación: {e}")


    def show_graph(self):
        conn = connect_db()
        if conn:
            df = pd.read_sql("SELECT edad, BebidasSemana, CervezasSemana FROM ENCUESTA", conn)
            conn.close()

            fig, ax = plt.subplots(figsize=(8, 6))
            ax.bar(df['edad'], df['BebidasSemana'], label='Bebidas/Semana')
            ax.bar(df['edad'], df['CervezasSemana'], label='Cervezas/Semana', alpha=0.7)
            ax.set_xlabel('Edad')
            ax.set_ylabel('Consumo')
            ax.set_title('Consumo de Bebidas y Cervezas por Edad')
            ax.legend()

            canvas = FigureCanvasTkAgg(fig, master=self)
            canvas.draw()
            canvas.get_tk_widget().pack()

    def input_window(self, title, callback, values=None):
        win = tk.Toplevel(self)
        win.title(title)

        labels = ["Edad", "Sexo", "Bebidas/Semana", "Cervezas/Semana", "Vinos/Semana", "Tensión Alta", "Dolor de Cabeza"]
        entries = []

        for i, label in enumerate(labels):
            tk.Label(win, text=label).grid(row=i, column=0, padx=10, pady=5)
            entry = tk.Entry(win)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries.append(entry)
            if values:
                entry.insert(0, values[i + 1])

        tk.Button(
            win, 
            text="Confirmar", 
            command=lambda: self.get_entry_data(entries, callback, win)
        ).grid(row=len(labels), column=0, columnspan=2, pady=10)

    def get_entry_data(self, entries, callback, win):
        data = [entry.get() for entry in entries]
        callback(*data)
        win.destroy()

# Crear instancia de la aplicación
app = EncuestaApp()

# Configurar título, tamaño y comportamiento inicial
app.title("Gestión de Encuestas de Consumo de Alcohol")
app.geometry("1200x700")
app.resizable(False, False)

# Configurar barra de menú y widgets iniciales
app.create_menu()
app.create_widgets()

# Ejecutar el bucle principal de la aplicación
app.mainloop()
