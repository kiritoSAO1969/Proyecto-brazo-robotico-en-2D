"""
Programa: Brazo robotico 2D
Fecha: 27/12/24
Descripción: Este programa permite la simulación gráfica y la exportación de datos para un brazo robótico.
Utiliza bibliotecas de Python como tkinter para la interfaz gráfica, matplotlib para las gráficas,y pandas para la gestión de datos en formato CSV.

Características destacadas:
    1. Ajuste en tiempo real de los ángulos del brazo robótico mediante deslizadores.
    2. Exportación de los datos calculados (longitudes, ángulos y posiciones) en un archivo CSV.
    3. Representación gráfica interactiva que permite inspeccionar las coordenadas de las articulaciones.
    4. Manejo intuitivo de la interfaz con colores y elementos que facilitan la experiencia del usuario.
"""

import mplcursors  # Herramienta para interactuar con gráficos de Matplotlib
import numpy as np  # Biblioteca para manejo de cálculos numéricos
import matplotlib.pyplot as plt  # Biblioteca para creación de gráficos
import os  # Biblioteca para manejo de archivos y directorios
import pandas as pd  # Biblioteca para manejo de datos en formato tabular
import tkinter as tk  # Biblioteca para creación de interfaces gráficas
from tkinter import filedialog, messagebox  # Elementos de interacción de Tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # Conexión entre Matplotlib y Tkinter

# Variables globales y estilos
ubicacion_archivo_csv = ""  # Ruta donde se guardará el archivo CSV
longitudes = [5, 4, 2, 2]  # Longitudes de los segmentos del brazo robótico


# ====================================
# FUNCIONES PRINCIPALES
# ====================================

def rotacion(angulo):
    """
    Calcula la matriz de rotación en dos dimensiones para un ángulo dado.

    Argumentos:
    angulo -- Ángulo en grados que se desea convertir a radianes para calcular la matriz de rotación.

    Retorno:
    Una matriz 2x2 que representa la rotación en el plano.

    Comportamiento:
    Convierte el ángulo a radianes y aplica fórmulas trigonométricas para calcular la matriz de rotación. Se redondean los valores
    para evitar errores numéricos.
    """
    rad = np.deg2rad(angulo)  # Conversión del ángulo de grados a radianes
    # Redondeo a 10 decimales para evitar errores numéricos pequeños
    return np.array([[np.round(np.cos(rad), 10), np.round(-np.sin(rad), 10)],
                    [np.round(np.sin(rad), 10), np.round(np.cos(rad), 10)]])

def matriz_transicion(x,y,tx, ty):
    """
    Calcula las coordenadas finales para los movimientos de todas las articulaciones mediante la matriz de
    transicion, al ya tener la cantidad de traslado en x y y respectivamente, resultando la matriz resultante para 
    la extraccion de los dos primeros elementos, es decir las coordenadas finales en x y y.

    Argumentos:
    x,y --Puntos iniciales
    tx, ty -- Cantidades de traslación en x y y respectivamente.

    Retorno:
    Matriz columna que da las coordenadas del vector ya rotado y trasladado.
    """
    #Creacion matriz de transicion
    matriz_1 = np.array([[1, 0, tx], 
                        [0, 1, ty], 
                        [0, 0, 1]])

    #Creacion matriz columna con coord originales
    matriz_2 = np.array([[x], [y], [1]])

    resultado = matriz_1 @ matriz_2
    return resultado

def calcular_posiciones(longitudes, angulos):
    """
    Calcula las posiciones de cada articulación y segmento del brazo robótico.

    Argumentos:
    longitudes -- Lista de longitudes de los segmentos del brazo.
    angulos -- Lista de ángulos en grados para cada articulación.

    Retorno:
    Lista de tuplas con las coordenadas de cada articulación y las posiciones iniciales.

    Comportamiento:
    Se calcula la posición de cada articulación aplicando primero la rotacion con matrices y luego la traslacion igualmente con 
    matrices, con la respectiva llamada a las funciones y manejo de los valores para la traslacion de las articulaciones, ademas se hace
    la rotacion de vectores para las posiciones iniciales
    """
    
    posiciones = [(0, 0)]  # Inicializa con la posición del origen
    coords_aux_suma = np.array([[0], [0]])  # Inicialización de matriz auxiliar
    angulo_aux=0 # Inicialización de variable auxiliar para el angulo
    
    #Bucle de obtencion de valores respectivos a las articulaciones necesarias para el movimiento
    for i in range(len(longitudes)):
        #Obtencion de la nueva posicion de codo y mano respectivamente siendo que se hace actualiza el valor del angulo_aux
        #dependiendo de la rotacion del miembro anterior, siendo que el hombro es el unico que no depende del angulo del otro valor
        #posteriormente se hace la llamada a la funcion matriz transicion pasandole los valores de x y y originales y luego los valores 
        #a trasladar para luego modificar los valores de traslacion con el valor obtenido y usarlos para la siguiente articulacion, 
        #este if va del hombro al codo,pues las manos son apartir del codo y no se requiere cambiar los valores de
        #traslacion en las manos ya que parten del codo
        if i <= 1:
            angulo_aux=angulo_aux+angulos[i]
            # Aplica rotacion de vector en punto de origen con longitudes correspondiente
            Resultado_temporal = rotacion(angulo_aux) @ np.array([[longitudes[i]], [0]])
            Coord_final = matriz_transicion(Resultado_temporal[0, 0], Resultado_temporal[1, 0],coords_aux_suma[0,0],coords_aux_suma[1,0])
            coords_aux_suma= coords_aux_suma + Resultado_temporal
        #Obtencion de la nueva posicion de mano1 y 2 respectivamente, partiendo primero de que el angulo_rot_mano partira del angulo en que
        #se encuentra el codo mas el angulo de la rotacion respectiva de la mano, posteriormente se hace
        #la llamada a matriz transicion pasandole los valores de x y y originales y luego los valores a trasladar
        else:
            angulo_rot_mano=angulo_aux+angulos[i]
            Resultado_temporal = rotacion(angulo_rot_mano) @ np.array([[longitudes[i]], [0]])
            Coord_final = matriz_transicion(Resultado_temporal[0, 0], Resultado_temporal[1, 0],coords_aux_suma[0,0],coords_aux_suma[1,0])

        # Agrega la coordenada obtenida a la lista de posiciones
        posiciones.append((Coord_final[0, 0], Coord_final[1, 0]))

    
    # Cálculo de posiciones originales mediante matrices de rotación
    R1 = rotacion(angulos[0])
    hombro = R1 @ np.array([longitudes[0], 0])

    R2 = rotacion(angulos[1]+angulos[0])
    codo = R2 @ np.array([longitudes[1], 0])+hombro

    # Posiciones originales de cada segmento
    hombro_original = np.array([longitudes[0], 0])
    codo_original = np.array([longitudes[1], 0]) + hombro
    minmano1_original = np.array([longitudes[2], 0]) + codo
    minmano2_original = np.array([longitudes[3], 0]) + codo

    # Agregar las posiciones originales a la lista
    posiciones.append(hombro_original)
    posiciones.append(codo_original)
    posiciones.append(minmano1_original)
    posiciones.append(minmano2_original)
    
    return posiciones

def graficar_brazo(posiciones, canvas):
    """
    Dibuja el brazo robótico y sus articulaciones en un gráfico.

    Argumentos:
    posiciones -- Lista de coordenadas calculadas para las articulaciones del brazo.
    canvas -- Lienzo de matplotlib incrustado en la interfaz gráfica.

    Comportamiento:
    Dibuja las articulaciones, segmentos del brazo y la base,
    además de configurar detalles estéticos y funcionales del gráfico.
    """
    # Definición de la base del brazo robótico
    posicion_base = [(0, 0), (0, -11), (-5, -11), (5, -11)]
    x_base, y_base = zip(*posicion_base)

    ax.clear()

    # Extraer las coordenadas X e Y de las articulaciones
    x_coords, y_coords = zip(*posiciones)

    # Configuración de los ejes y el fondo
    ax.set_facecolor('lightgray')
    ax.set_xlim(-15, 15)
    ax.set_ylim(-15, 15)
    ax.set_aspect('equal', adjustable='box')
    ax.set_xticks(np.arange(-15, 16, 2))
    ax.set_yticks(np.arange(-15, 16, 2))
    ax.grid(True, linestyle='--', color='gray', alpha=0.7)

    # Etiquetas de los ejes y título
    ax.set_xlabel('X', fontsize=12, fontweight='bold', color='white')
    ax.set_ylabel('Y', fontsize=12, fontweight='bold', color='white')
    ax.set_title('Simulación de Brazo Robótico', fontsize=14, fontweight='bold', color='white')
    ax.tick_params(axis='both', colors='white', width=1, labelsize=10)

    # Dibujo de las articulaciones y los segmentos
    ax.scatter(x_coords[0:5], y_coords[0:5], marker='o', s=100, color='#FFD700', label='Articulaciones y extensiones', zorder=5)
    ax.plot([x_coords[0], x_coords[1]], [y_coords[0], y_coords[1]], color='#708090', linewidth=6, label='Hombro', zorder=1)
    ax.plot([x_coords[1], x_coords[2]], [y_coords[1], y_coords[2]], color='#4682B4', linewidth=6, label='Codo', zorder=1)
    ax.plot([x_coords[2], x_coords[3]], [y_coords[2], y_coords[3]], color='#5F9EA0', linewidth=6, label='Mano 1', zorder=1)
    ax.plot([x_coords[2], x_coords[4]], [y_coords[2], y_coords[4]], color='#5F9EA9', linewidth=6, label='Mano 2', zorder=1)
    ax.plot([x_base[0], x_base[1]], [y_base[0], y_base[1]], color='#2F4F4F', linewidth=6, label='Base vertical', zorder=1)
    ax.plot([x_base[2], x_base[3]], [y_base[2], y_base[3]], color='#2F4F4F', linewidth=6, label='Base horizontal', zorder=1)

    # Agrega la leyenda después de definir todos los elementos gráficos con etiquetas
    ax.legend()

    # Interactividad: mostrar coordenadas al pasar el cursor
    puntos_articulaciones = ax.scatter(x_coords[0:5], y_coords[0:5], s=100, color='#FFD700')
    cursor = mplcursors.cursor(puntos_articulaciones, hover=mplcursors.HoverMode.Transient)
    cursor.connect("add", lambda sel: (
        sel.annotation.set_text(f'({x_coords[sel.index]:.2f}, {y_coords[sel.index]:.2f})'),
        sel.annotation.get_bbox_patch().set_facecolor('blue')
    ))

    # Actualización del lienzo
    canvas.draw()

def guardar_csv(longitudes, angulos, posiciones):
    """
    Guarda los datos del brazo robótico en un archivo CSV, incluyendo longitudes, ángulos y posiciones.

    Argumentos:
    longitudes -- Lista con las longitudes de los segmentos del brazo robótico.
    angulos -- Lista con los ángulos de las articulaciones del brazo.
    posiciones -- Lista con las coordenadas calculadas de las articulaciones.

    Comportamiento:
    - Si el archivo ya existe, pregunta si se desea agregar nuevos datos.
    - Si no existe, crea un nuevo archivo y guarda los datos.
    - Si no se selecciona un archivo, muestra un mensaje de advertencia.
    """
    global ubicacion_archivo_csv

    # Datos organizados en un diccionario para su exportación
    data = {
        'Longitud Segmento 1': longitudes[0],
        'Longitud Segmento 2': longitudes[1],
        'Longitud de las manos': longitudes[2],
        'Angulo Hombro en grados': angulos[0],
        'Angulo Codo en grados': angulos[1],
        'Angulo Mano 1 en grados': angulos[2],
        'Angulo Mano 2 en grados': angulos[3],
        'Angulo Codo final en grados': angulos[1]+angulos[0],
        'Angulo Mano 1 final en grados': angulos[2]+angulos[1]+angulos[0],
        'Angulo Mano 2 final en grados': angulos[3]+angulos[1]+angulos[0],
        'Posicion X Hombro inicial': posiciones[5][0], 'Posicion X Hombro': posiciones[1][0],
        'Posicion Y Hombro inicial': posiciones[5][1], 'Posicion Y Hombro': posiciones[1][1],
        'Posicion X Codo inicial': posiciones[6][0], 'Posicion X Codo': posiciones[2][0],
        'Posicion Y Codo inicial': posiciones[6][1], 'Posicion Y Codo': posiciones[2][1],
        'Posicion X Mano 1 inicial': posiciones[7][0], 'Posicion X Mano 1': posiciones[3][0],
        'Posicion Y Mano 1 inicial': posiciones[7][1], 'Posicion Y Mano 1': posiciones[3][1],
        'Posicion X Mano 2 inicial': posiciones[8][0], 'Posicion X Mano 2': posiciones[4][0],
        'Posicion Y Mano 2 inicial': posiciones[8][1], 'Posicion Y Mano 2': posiciones[4][1]
    }

    df = pd.DataFrame([data])

    # Verifica si se seleccionó previamente un archivo
    if not ubicacion_archivo_csv:
        ubicacion_archivo_csv = filedialog.asksaveasfilename(defaultextension=".csv",
                                                             filetypes=[("CSV files", "*.csv")])
        if not ubicacion_archivo_csv:
            messagebox.showwarning("Advertencia", "No se ha seleccionado ningún archivo, no se guardó nada.")
            return

    try:
        # Agrega o crea el archivo CSV
        if os.path.exists(ubicacion_archivo_csv):
            respuesta = messagebox.askyesno("Archivo existente",
                                            "El archivo ya tiene datos. ¿Desea agregar datos nuevos aun así?")
            if respuesta:
                df.to_csv(ubicacion_archivo_csv, mode='a', header=False, index=False)
                messagebox.showinfo("Éxito", "Datos añadidos correctamente.")
            else:
                messagebox.showinfo("Operación cancelada", "No se han añadido datos.")
        else:
            df.to_csv(ubicacion_archivo_csv, mode='w', header=True, index=False)
            messagebox.showinfo("Éxito", "Archivo guardado correctamente.")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al guardar el archivo: {e}")

def exportar_datos():
    """
    Exporta los datos actuales del brazo robótico a un archivo CSV.
    Incluye los ángulos, longitudes y posiciones calculadas.
    """
    angulo_hombro = desliz_hombro.get()
    angulo_codo = desliz_codo.get()
    angulo_mano1 = desliz_mano1.get()
    angulo_mano2 = desliz_mano2.get()
    posiciones = calcular_posiciones(longitudes, [angulo_hombro, angulo_codo, angulo_mano1, angulo_mano2])
    guardar_csv(longitudes, [angulo_hombro, angulo_codo, angulo_mano1, angulo_mano2], posiciones)

def actualizar_grafica():
    """
    Actualiza el gráfico del brazo robótico basándose en los ángulos seleccionados en los controles deslizantes.
    """
    angulo_hombro = desliz_hombro.get()
    angulo_codo = desliz_codo.get()
    angulo_mano1 = desliz_mano1.get()
    angulo_mano2 = desliz_mano2.get()
    posiciones = calcular_posiciones(longitudes, [angulo_hombro, angulo_codo, angulo_mano1, angulo_mano2])
    graficar_brazo(posiciones, canvas)

def crear_ventana():
    """
    Crea la ventana principal de la interfaz gráfica con controles y gráfico para la simulación del brazo robótico.
    """
    global ventana, ax, canvas, desliz_hombro, desliz_codo, desliz_mano1, desliz_mano2
    ventana = tk.Tk()
    ventana.title("Simulación de Brazo Robótico")
    ventana.iconbitmap('C:\\Users\\zaddk\\Documents\\Algebra lineal\\icono_brazo_robot.ico') #modificar con ruta hacia la imagen para
                                                                                            #correcto funcionamiento, la img tiene q ser .ico
    ventana.geometry("1500x900")
    ventana.configure(bg="#2E2E2E")

    # Configuración de frames
    frame_controles = tk.Frame(ventana, bg="#2E2E2E")
    frame_controles.grid(row=0, column=0, padx=(0, 0), pady=10, sticky='nsew')

    frame_grafica = tk.Frame(ventana, bg="#2E2E2E")
    frame_grafica.grid(row=0, column=1, padx=(0, 40), pady=10, sticky='nsew')

    # Gráfico del brazo robótico
    fig, ax = plt.subplots(figsize=(9, 9), facecolor="#2E2E2E")
    canvas = FigureCanvasTkAgg(fig, master=frame_grafica)
    canvas_grafico = canvas.get_tk_widget()
    canvas_grafico.grid(row=0, column=0, sticky='nsew')

    # Controles deslizantes y botones
    tk.Label(frame_controles, text="PROYECTO BRAZO ROBOTICO", **label_style_titulo).grid(row=0, column=0, sticky=tk.W, padx=(50, 0), pady=(150, 0))

    tk.Label(frame_controles, text="Ángulo de la articulación θ1", **label_style).grid(row=1, column=0, sticky=tk.W, padx=(50, 0), pady=(40, 0))
    desliz_hombro = tk.Scale(frame_controles, from_=0, to=360, orient='horizontal', command=lambda x: actualizar_grafica(), **desliz_style)
    desliz_hombro.grid(row=1, column=1, pady=(80, 40))

    tk.Label(frame_controles, text="Ángulo de la articulación θ2", **label_style).grid(row=2, column=0, sticky=tk.W, padx=(50, 0))
    desliz_codo = tk.Scale(frame_controles, from_=0, to=360, orient='horizontal', command=lambda x: actualizar_grafica(), **desliz_style)
    desliz_codo.grid(row=2, column=1, pady=40)

    tk.Label(frame_controles, text="Ángulo de la articulación θ3, minibrazo 1", **label_style).grid(row=3, column=0, sticky=tk.W, padx=(50, 0))
    desliz_mano1 = tk.Scale(frame_controles, from_=0, to=360, orient='horizontal', command=lambda x: actualizar_grafica(), **desliz_style)
    desliz_mano1.grid(row=3, column=1, pady=40)

    tk.Label(frame_controles, text="Ángulo de la articulación θ4, minibrazo 2", **label_style).grid(row=4, column=0, sticky=tk.W, padx=(50, 0))
    desliz_mano2 = tk.Scale(frame_controles, from_=0, to=360, orient='horizontal', command=lambda x: actualizar_grafica(), **desliz_style)
    desliz_mano2.grid(row=4, column=1, pady=40)

    tk.Label(frame_controles, text="Para almacenar los datos calculados, presione el botón.Si es la primera vez, se solicitará un archivo\n o crear uno nuevo.", **label_style).grid(row=5, column=0, columnspan=2, sticky=tk.W, padx=(50, 0))
    btn_exportar = tk.Button(frame_controles, text="Exportar Datos a CSV", command=exportar_datos, bg="#4B4B4B", fg="#FFFFFF", font=("Arial", 20))
    btn_exportar.grid(row=6, column=0, columnspan=2, pady=20)

    # Se rota una de las manos inicialmente para que se puedan ver las dos al inicio del programa
    desliz_mano1.set(0)

    # Inicializar
    actualizar_grafica()
    ventana.mainloop()

# Estilos para etiquetas y sliders
label_style = {
    'bg': "#2E2E2E",  # Fondo oscuro
    'fg': "#FFFFFF",  # Texto blanco
    'font': ("Arial", 16)  # Fuente de tamaño mediano
}

label_style_titulo = {
    'bg': "#2E2E2E",  # Fondo oscuro
    'fg': "#FFFFFF",  # Texto blanco
    'font': ("Arial", 22)  # Fuente de mayor tamaño para títulos
}

desliz_style = {
    'bg': "#4B4B4B",  # Fondo del slider
    'fg': "#FFFFFF",  # Texto blanco
    'font': ("Arial", 15),  # Fuente del texto asociado al slider
    'sliderlength': 60,  # Tamaño del cursor del slider
    'length': 450,  # Longitud del slider
    'highlightbackground': "#4B4B4B",  # Color del borde
    'highlightcolor': "#000854"  # Color cuando el slider está activo
}

# Llamada a la función principal para crear la ventana
crear_ventana()