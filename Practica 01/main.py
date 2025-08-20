import time
import random
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

#busqueda

def busqueda_lineal(lista, x):
    for i, v in enumerate(lista):
        if v == x:
            return i
    return -1

def busqueda_binaria(lista, x):

    # si no esta ordenada, aca se ordena
    if lista != sorted(lista):
        lista = sorted(lista)  # orrdenada pendiente

    izq, der = 0, len(lista) - 1
    while izq <= der:
        mid = (izq + der) // 2
        if lista[mid] == x:
            return mid
        elif lista[mid] < x:
            izq = mid + 1
        else:
            der = mid - 1
    return -1

#generar datos

def generar_lista(tamano):
    """
    Crea una lista ORDENADA de enteros únicos.
    Usamos NumPy para generar rápidamente números sin repetición y luego ordenar.
    """
    arr = np.random.choice(tamano * 10, size=tamano, replace=False)
    arr.sort()  # aqui ordena
    return arr.tolist()  

# medir tiempos

def medir_tiempo(funcion, lista, x, repeticiones=5):
    """
    Ejecuta la función 'repeticiones' veces y devuelve el promedio en milisegundos.
    """
    tiempos_ms = []
    for _ in range(repeticiones):
        inicio = time.perf_counter()
        funcion(lista, x)
        fin = time.perf_counter()
        tiempos_ms.append((fin - inicio) * 1000.0)  # a ms
    return sum(tiempos_ms) / len(tiempos_ms)

# Tkinter

TAMANOS_PERMITIDOS = [100, 1000, 10000, 100000]

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Comparación de Búsquedas (Lineal vs Binaria) - NumPy + Tkinter")
        self.geometry("960x640")
        self.minsize(900, 600)

        self.lista_actual = []
        self.rep_default = 5

        self._construir_ui()

    def _construir_ui(self):
        cont = ttk.Frame(self, padding=12)
        cont.pack(side=tk.TOP, fill=tk.X)

        # egenerador datos
        ttk.Label(cont, text="Tamaño de la lista:").grid(row=0, column=0, sticky="w")
        self.cmb_tamano = ttk.Combobox(cont, values=TAMANOS_PERMITIDOS, state="readonly", width=10)
        self.cmb_tamano.current(0)
        self.cmb_tamano.grid(row=0, column=1, padx=6)

        ttk.Label(cont, text="Repeticiones (≥5):").grid(row=0, column=2, sticky="w", padx=(12, 0))
        self.spn_rep = tk.Spinbox(cont, from_=5, to=100, width=6)
        self.spn_rep.delete(0, tk.END)
        self.spn_rep.insert(0, str(self.rep_default))
        self.spn_rep.grid(row=0, column=3, padx=6)

        btn_generar = ttk.Button(cont, text="Generar datos", command=self.generar_datos)
        btn_generar.grid(row=0, column=4, padx=6)

        ttk.Separator(cont, orient="horizontal").grid(row=1, column=0, columnspan=6, sticky="ew", pady=10)

        # buscar
        ttk.Label(cont, text="Valor a buscar:").grid(row=2, column=0, sticky="w")
        self.entry_valor = ttk.Entry(cont, width=14)
        self.entry_valor.grid(row=2, column=1, padx=6)

        btn_lineal = ttk.Button(cont, text="Búsqueda lineal", command=lambda: self.ejecutar_busqueda("lineal"))
        btn_lineal.grid(row=2, column=2, padx=6)

        btn_binaria = ttk.Button(cont, text="Búsqueda binaria", command=lambda: self.ejecutar_busqueda("binaria"))
        btn_binaria.grid(row=2, column=3, padx=6)

        btn_graficar = ttk.Button(cont, text="Actualizar gráfica (4 tamaños)", command=self.actualizar_grafica)
        btn_graficar.grid(row=2, column=4, padx=6)

        # Resultado
        self.lbl_result = ttk.Label(self, text="Sin datos generados.", padding=10)
        self.lbl_result.pack(side=tk.TOP, anchor="w")

        # grafica
        self.fig = Figure(figsize=(6.4, 4.0), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Tiempos promedio por tamaño")
        self.ax.set_xlabel("Tamaño de la lista")
        self.ax.set_ylabel("Tiempo (ms)")
        self.ax.set_xscale("log")         


        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas.draw()


    def _leer_repeticiones(self):
        try:
            rep = int(self.spn_rep.get())
            if rep < 5:
                raise ValueError
            return rep
        except Exception:
            messagebox.showerror("Error", "Repeticiones debe ser un entero ≥ 5.")
            return None

    def generar_datos(self):
        try:
            tam = int(self.cmb_tamano.get())
            if tam not in TAMANOS_PERMITIDOS:
                raise ValueError
        except Exception:
            messagebox.showerror("Error", "Selecciona un tamaño válido.")
            return

        self.lista_actual = generar_lista(tam)
        self.lbl_result.config(text=f"Lista generada: tamaño={tam}. (Ordenada para binaria)")
        messagebox.showinfo("OK", f"Se generó una lista ordenada de tamaño {tam}.")

    def ejecutar_busqueda(self, tipo):

        if not self.lista_actual:
            messagebox.showerror("Error", "Primero genera la lista.")
            return

        valor_txt = self.entry_valor.get().strip()
        if not valor_txt or not valor_txt.lstrip("-").isdigit():
            messagebox.showerror("Error", "Ingresa un entero en 'Valor a buscar'.")
            return

        rep = self._leer_repeticiones()
        if rep is None:
            return

        x = int(valor_txt)
        funcion = busqueda_lineal if tipo == "lineal" else busqueda_binaria

        # 1 ejecucion
        t0 = time.perf_counter()
        indice = funcion(self.lista_actual, x)
        t1 = time.perf_counter()
        tiempo_exacto_ms = (t1 - t0) * 1000.0

        encontrado = f"Encontrado en índice {indice}" if indice != -1 else "No encontrado"

        # promedio
        promedio_ms = medir_tiempo(funcion, self.lista_actual, x, repeticiones=rep)

        self.lbl_result.config(
            text=(
                f"Tamaño={len(self.lista_actual)} | {encontrado} | "
                f"Tiempo exacto: {tiempo_exacto_ms:.5f} ms | "
                f"Promedio: {promedio_ms:.5f} ms ({rep} rep.)"
            )
        )

    def actualizar_grafica(self):
        
        #promedios de 4 tamanos yyy se actualiza en la misma ventana
        
        rep = self._leer_repeticiones()
        if rep is None:
            return

        tamanos = TAMANOS_PERMITIDOS
        tiempos_lin, tiempos_bin = [], []

        for t in tamanos:
            lista = generar_lista(t)
            x = lista[np.random.randint(0, t)]

            tiempos_lin.append(medir_tiempo(busqueda_lineal, lista, x, repeticiones=rep))
            tiempos_bin.append(medir_tiempo(busqueda_binaria, lista, x, repeticiones=rep))

        
        self.ax.clear()
        self.ax.set_title("Tiempos promedio por tamaño")
        self.ax.set_xlabel("Tamaño de la lista")
        self.ax.set_ylabel("Tiempo (ms)")
        self.ax.set_xscale("log")

        self.ax.plot(tamanos, tiempos_lin, marker="o", label="Lineal")
        self.ax.plot(tamanos, tiempos_bin, marker="o", label="Binaria")
        self.ax.legend()
        self.canvas.draw()

        self.lbl_result.config(text=f"Gráfica actualizada con {rep} repeticiones por tamaño.")

if __name__ == "__main__":
    app = App()
    app.mainloop()