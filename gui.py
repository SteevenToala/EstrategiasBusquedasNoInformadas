import tkinter as tk
from tkinter import ttk, messagebox
import math
import random

from modelo import ANCHO, LARGO, OBJETIVO, generar_estado_inicial
from algoritmos import ejecutar_comparacion, mejor_solucion, bfs, dfs, dfs_iterativa, bidireccional

# ==============================================================================
# APLICACIÓN DE ESCRITORIO NATIVA (TKINTER GUI) - BÚSQUEDAS NO INFORMADAS
# ==============================================================================

class BusquedasGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Búsquedas No Informadas — Aula 20x10 (IA)")
        self.geometry("1380x860")
        self.minsize(1100, 700)
        
        # Paleta de Colores Moderna (Dark Mode)
        self.COLOR_BG = "#0f172a"
        self.COLOR_PANEL = "#1e293b"
        self.COLOR_BORDER = "#334155"
        self.COLOR_TEXT = "#f8fafc"
        self.COLOR_TEXT_MUTED = "#94a3b8"
        self.COLOR_START = "#10b981"       # Verde esmeralda
        self.COLOR_GOAL = "#ec4899"        # Rosa magenta
        self.COLOR_PATH = "#38bdf8"        # Azul cian
        self.COLOR_CURRENT = "#f59e0b"     # Dorado / Ámbar
        self.COLOR_CELL_BG = "#090d16"
        self.COLOR_CELL_BORDER = "#1e293b"

        self.configure(bg=self.COLOR_BG)

        # Estado de la Simulación
        self.inicio = (6, 1)
        self.objetivo = OBJETIVO
        self.algoritmo_actual = "BFS"
        self.modo_arbol = "solucion"  # 'solucion' | 'acotado' | 'completo'
        self.resultados = []
        self.mejor = None

        # Control de Animación
        self.anim_paso = 0
        self.anim_activa = False
        self.anim_job = None
        self.anim_velocidad_ms = 120

        # Zoom y Pan del Árbol
        self.zoom_arbol = 1.0
        self.pan_start_x = 0
        self.pan_start_y = 0

        self.setup_styles()
        self.setup_layout()

        # Ejecución inicial
        self.resolver_todo()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Configuración general de ttk
        self.style.configure(".", background=self.COLOR_PANEL, foreground=self.COLOR_TEXT, font=("Segoe UI", 9))
        self.style.configure("TFrame", background=self.COLOR_PANEL)
        self.style.configure("Main.TFrame", background=self.COLOR_BG)
        self.style.configure("TLabelframe", background=self.COLOR_PANEL, foreground=self.COLOR_TEXT, bordercolor=self.COLOR_BORDER)
        self.style.configure("TLabelframe.Label", background=self.COLOR_PANEL, foreground=self.COLOR_TEXT, font=("Segoe UI", 10, "bold"))
        
        # Botones
        self.style.configure("Primary.TButton", background="#0284c7", foreground="#ffffff", font=("Segoe UI", 9, "bold"), padding=6)
        self.style.map("Primary.TButton", background=[("active", "#0369a1")])

        self.style.configure("Secondary.TButton", background="#334155", foreground="#ffffff", font=("Segoe UI", 9), padding=5)
        self.style.map("Secondary.TButton", background=[("active", "#475569")])

        # Pestañas Notebook
        self.style.configure("TNotebook", background=self.COLOR_BG, borderwidth=0)
        self.style.configure("TNotebook.Tab", background="#1e293b", foreground=self.COLOR_TEXT_MUTED, padding=[16, 8], font=("Segoe UI", 10, "bold"))
        self.style.map("TNotebook.Tab", background=[("selected", "#0284c7")], foreground=[("selected", "#ffffff")])

        # Tabla Treeview
        self.style.configure("Treeview", background="#090d16", foreground=self.COLOR_TEXT, fieldbackground="#090d16", rowheight=26, font=("Segoe UI", 9))
        self.style.configure("Treeview.Heading", background="#1e293b", foreground=self.COLOR_TEXT, font=("Segoe UI", 9, "bold"))
        self.style.map("Treeview", background=[("selected", "#0284c7")])

    def setup_layout(self):
        # 1. BARRA SUPERIOR
        header_frame = tk.Frame(self, bg=self.COLOR_PANEL, height=54, highlightbackground=self.COLOR_BORDER, highlightthickness=1)
        header_frame.pack(fill=tk.X, side=tk.TOP)

        title_lbl = tk.Label(header_frame, text="🤖 Búsquedas No Informadas (IA)", font=("Segoe UI", 14, "bold"), bg=self.COLOR_PANEL, fg=self.COLOR_TEXT)
        title_lbl.pack(side=tk.LEFT, padx=18, pady=8)

        self.lbl_coords = tk.Label(header_frame, text="Inicio: (3, 0)  |  Objetivo: (11, 8)", font=("Consolas", 11, "bold"), bg=self.COLOR_CELL_BG, fg=self.COLOR_PATH, padx=12, pady=4, relief=tk.SOLID, bd=1)
        self.lbl_coords.pack(side=tk.LEFT, padx=20)

        btn_random = ttk.Button(header_frame, text="🎲 Origen Aleatorio", style="Secondary.TButton", command=self.on_random_start)
        btn_random.pack(side=tk.RIGHT, padx=10, pady=8)

        btn_solve = ttk.Button(header_frame, text="⚡ Resolver Todo", style="Primary.TButton", command=self.resolver_todo)
        btn_solve.pack(side=tk.RIGHT, padx=8, pady=8)

        # 2. CUERPO PRINCIPAL DIVIDIDO (Izquierda: Grid y Métricas, Derecha: Árbol y Tablas)
        main_paned = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # PANEL IZQUIERDO: Cuadrícula y Controles
        left_frame = tk.Frame(main_paned, bg=self.COLOR_PANEL, width=440)
        main_paned.add(left_frame, weight=0)

        # Canvas Cuadrícula 20x10
        grid_labelframe = ttk.LabelFrame(left_frame, text=" 📍 Espacio del Aula (20x10) — Clic para mover Inicio (I) ")
        grid_labelframe.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        self.canvas_grid = tk.Canvas(grid_labelframe, bg=self.COLOR_CELL_BG, highlightthickness=0, width=380, height=480)
        self.canvas_grid.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        self.canvas_grid.bind("<Button-1>", self.on_grid_click)

        # Barra de Controles de Animación
        anim_bar = tk.Frame(left_frame, bg=self.COLOR_PANEL)
        anim_bar.pack(fill=tk.X, padx=8, pady=4)

        self.btn_play = ttk.Button(anim_bar, text="▶ Reproducir", style="Primary.TButton", width=12, command=self.toggle_animacion)
        self.btn_play.pack(side=tk.LEFT, padx=4)

        self.btn_step = ttk.Button(anim_bar, text="⏭ Paso", style="Secondary.TButton", width=8, command=self.paso_siguiente)
        self.btn_step.pack(side=tk.LEFT, padx=4)

        self.btn_reset = ttk.Button(anim_bar, text="🔄 Reset", style="Secondary.TButton", width=8, command=self.reset_animacion)
        self.btn_reset.pack(side=tk.LEFT, padx=4)

        self.lbl_paso_info = tk.Label(anim_bar, text="Paso: 0 / 0", font=("Consolas", 10, "bold"), bg=self.COLOR_PANEL, fg=self.COLOR_TEXT_MUTED)
        self.lbl_paso_info.pack(side=tk.RIGHT, padx=8)

        # Leyenda de Colores
        legend_frame = tk.Frame(left_frame, bg=self.COLOR_PANEL)
        legend_frame.pack(fill=tk.X, padx=8, pady=4)
        tk.Label(legend_frame, text="🟩 Inicio (I)   🟪 Objetivo (O)   🟦 Camino (*)   ⬛ Libre (.)", font=("Segoe UI", 8), bg=self.COLOR_PANEL, fg=self.COLOR_TEXT_MUTED).pack(anchor="w")

        # PANEL DERECHO: Pestañas de Algoritmo y Visualizador de Árbol / Tablas
        right_frame = tk.Frame(main_paned, bg=self.COLOR_BG)
        main_paned.add(right_frame, weight=1)

        # Pestañas Superiores de Algoritmo
        self.algo_notebook = ttk.Notebook(right_frame)
        self.algo_notebook.pack(fill=tk.X, padx=4, pady=2)
        self.algo_notebook.add(tk.Frame(self.algo_notebook), text="  BFS (Anchura)  ")
        self.algo_notebook.add(tk.Frame(self.algo_notebook), text="  DFS (Profundidad)  ")
        self.algo_notebook.add(tk.Frame(self.algo_notebook), text="  DFS Iterativa  ")
        self.algo_notebook.add(tk.Frame(self.algo_notebook), text="  Bidireccional  ")
        self.algo_notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        # Tarjetas Rápidas de Métricas (KPIs)
        self.kpi_frame = tk.Frame(right_frame, bg=self.COLOR_PANEL, relief=tk.SOLID, bd=1)
        self.kpi_frame.pack(fill=tk.X, padx=4, pady=6)
        
        self.lbl_kpi_costo = self.crear_kpi(self.kpi_frame, "COSTO", "-- pasos", 0)
        self.lbl_kpi_expandidos = self.crear_kpi(self.kpi_frame, "EXPANDIDOS", "-- nodos", 1)
        self.lbl_kpi_generados = self.crear_kpi(self.kpi_frame, "GENERADOS", "-- nodos", 2)
        self.lbl_kpi_memoria = self.crear_kpi(self.kpi_frame, "MÁX. MEMORIA", "-- nodos", 3)
        self.lbl_kpi_tiempo = self.crear_kpi(self.kpi_frame, "TIEMPO", "-- ms", 4)
        self.lbl_kpi_mejor = self.crear_kpi(self.kpi_frame, "CALIDAD", "--", 5)

        # Selector de Modo de Árbol y Controles de Zoom
        tree_ctrl_frame = tk.Frame(right_frame, bg=self.COLOR_PANEL)
        tree_ctrl_frame.pack(fill=tk.X, padx=4, pady=4)

        tk.Label(tree_ctrl_frame, text="Modo de Árbol:", font=("Segoe UI", 9, "bold"), bg=self.COLOR_PANEL, fg=self.COLOR_TEXT).pack(side=tk.LEFT, padx=6)
        
        self.var_modo_arbol = tk.StringVar(value="solucion")
        rb1 = tk.Radiobutton(tree_ctrl_frame, text="⭐ Solo Camino Solución", variable=self.var_modo_arbol, value="solucion", command=self.on_tree_mode_change, bg=self.COLOR_PANEL, fg=self.COLOR_TEXT, selectcolor=self.COLOR_BG, activebackground=self.COLOR_PANEL, activeforeground=self.COLOR_PATH)
        rb1.pack(side=tk.LEFT, padx=4)
        rb2 = tk.Radiobutton(tree_ctrl_frame, text="🌿 Árbol Acotado (Nivel ≤ 4)", variable=self.var_modo_arbol, value="acotado", command=self.on_tree_mode_change, bg=self.COLOR_PANEL, fg=self.COLOR_TEXT, selectcolor=self.COLOR_BG, activebackground=self.COLOR_PANEL, activeforeground=self.COLOR_PATH)
        rb2.pack(side=tk.LEFT, padx=4)
        rb3 = tk.Radiobutton(tree_ctrl_frame, text="🌳 Árbol Completo", variable=self.var_modo_arbol, value="completo", command=self.on_tree_mode_change, bg=self.COLOR_PANEL, fg=self.COLOR_TEXT, selectcolor=self.COLOR_BG, activebackground=self.COLOR_PANEL, activeforeground=self.COLOR_PATH)
        rb3.pack(side=tk.LEFT, padx=4)

        # Botones Zoom
        btn_zoom_fit = ttk.Button(tree_ctrl_frame, text="⛶ Centrar", style="Secondary.TButton", width=8, command=self.reset_tree_zoom)
        btn_zoom_fit.pack(side=tk.RIGHT, padx=4)
        btn_zoom_out = ttk.Button(tree_ctrl_frame, text="🔍-", style="Secondary.TButton", width=4, command=lambda: self.zoom_tree(0.8))
        btn_zoom_out.pack(side=tk.RIGHT, padx=2)
        btn_zoom_in = ttk.Button(tree_ctrl_frame, text="🔍+", style="Secondary.TButton", width=4, command=lambda: self.zoom_tree(1.25))
        btn_zoom_in.pack(side=tk.RIGHT, padx=2)

        # Canvas del Árbol de Búsqueda
        tree_box = ttk.LabelFrame(right_frame, text=" 🌳 Visualización del Árbol de Búsqueda (Arrastra o haz clic en nodos) ")
        tree_box.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        self.canvas_tree = tk.Canvas(tree_box, bg="#070b13", highlightthickness=0)
        self.canvas_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        # Scrollbars para el árbol
        scroll_y = ttk.Scrollbar(tree_box, orient=tk.VERTICAL, command=self.canvas_tree.yview)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x = ttk.Scrollbar(right_frame, orient=tk.HORIZONTAL, command=self.canvas_tree.xview)
        scroll_x.pack(fill=tk.X, padx=4)

        self.canvas_tree.configure(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)

        # Bindings para Drag/Pan y Clic en nodos del árbol
        self.canvas_tree.bind("<ButtonPress-1>", self.on_tree_press)
        self.canvas_tree.bind("<B1-Motion>", self.on_tree_drag)

        # Barra de Inspección de Nodos
        self.node_info_bar = tk.Label(right_frame, text="💡 Pasa el ratón o haz clic en un nodo del árbol para inspeccionar su estado, acción y costo.", font=("Segoe UI", 9), bg=self.COLOR_CELL_BG, fg=self.COLOR_TEXT_MUTED, anchor="w", padx=12, pady=4)
        self.node_info_bar.pack(fill=tk.X, padx=4, pady=2)

        # 3. PANEL INFERIOR: Tabla de Métricas y Complejidad
        bottom_frame = ttk.LabelFrame(self, text=" 📊 Tabla Comparativa de Complejidades y Métricas Experimentales ")
        bottom_frame.pack(fill=tk.X, padx=10, pady=6)

        columnas = ("algoritmo", "estructura", "solucion", "costo", "nivel", "generados", "expandidos", "memoria", "tiempo", "comp_t", "comp_e")
        self.tree_table = ttk.Treeview(bottom_frame, columns=columnas, show="headings", height=4)
        
        headers = [
            ("algoritmo", "Algoritmo", 110),
            ("estructura", "Estructura de Datos", 140),
            ("solucion", "Solución", 70),
            ("costo", "Costo", 60),
            ("nivel", "Nivel", 60),
            ("generados", "Generados", 90),
            ("expandidos", "Expandidos", 90),
            ("memoria", "Máx. Memoria", 100),
            ("tiempo", "Tiempo (s)", 90),
            ("comp_t", "Tiempo Teórico", 100),
            ("comp_e", "Espacio Teórico", 100)
        ]

        for col, title, w in headers:
            self.tree_table.heading(col, text=title)
            self.tree_table.column(col, width=w, anchor=tk.CENTER)

        self.tree_table.pack(fill=tk.X, expand=True, padx=6, pady=4)

    def crear_kpi(self, parent, titulo, valor_def, col):
        f = tk.Frame(parent, bg=self.COLOR_PANEL, padx=8, pady=4)
        f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk.Label(f, text=titulo, font=("Segoe UI", 7, "bold"), fg=self.COLOR_TEXT_MUTED, bg=self.COLOR_PANEL).pack(anchor="w")
        lbl = tk.Label(f, text=valor_def, font=("Consolas", 12, "bold"), fg=self.COLOR_PATH, bg=self.COLOR_PANEL)
        lbl.pack(anchor="w")
        return lbl

    # ==========================================================================
    # LÓGICA DE RESOLUCIÓN Y ACTUALIZACIÓN
    # ==========================================================================

    def on_random_start(self):
        self.inicio = generar_estado_inicial()
        self.resolver_todo()

    def resolver_todo(self):
        self.reset_animacion()
        self.lbl_coords.config(text=f"Inicio: ({self.inicio[0]}, {self.inicio[1]})  |  Objetivo: ({self.objetivo[0]}, {self.objetivo[1]})")

        # Ejecutar los 4 algoritmos con Tree Search puro
        self.inicio, self.resultados = ejecutar_comparacion(estado_inicial=self.inicio, objetivo=self.objetivo)
        self.mejor = mejor_solucion(self.resultados)

        self.actualizar_vistas()

    def actualizar_vistas(self):
        # 1. Dibujar Cuadrícula
        self.dibujar_cuadricula()

        # 2. Actualizar KPIs del algoritmo activo
        res = next((r for r in self.resultados if r["algoritmo"] == self.algoritmo_actual), None)
        if res:
            self.lbl_kpi_costo.config(text=f"{res['costo']} pasos" if res["encontrado"] else "--")
            self.lbl_kpi_expandidos.config(text=f"{res['nodos_expandidos']:,}")
            self.lbl_kpi_generados.config(text=f"{res['nodos_generados']:,}")
            self.lbl_kpi_memoria.config(text=f"{res['max_estructura']} nodos")
            self.lbl_kpi_tiempo.config(text=f"{res['tiempo']*1000:.3f} ms")
            
            es_mejor = self.mejor and self.mejor["algoritmo"] == res["algoritmo"]
            self.lbl_kpi_mejor.config(
                text="🏆 MEJOR SOLUCIÓN" if es_mejor else "Solución Válida",
                fg="#f59e0b" if es_mejor else self.COLOR_TEXT_MUTED
            )

            total_pasos = len(res["camino"]) - 1 if res["camino"] else 0
            self.lbl_paso_info.config(text=f"Paso: 0 / {total_pasos}")

        # 3. Dibujar Árbol de Búsqueda
        self.dibujar_arbol_canvas()

        # 4. Actualizar Tabla Comparativa
        self.actualizar_tabla_resultados()

    def on_tab_changed(self, event):
        idx = self.algo_notebook.index(self.algo_notebook.select())
        nombres = ["BFS", "DFS", "DFS iterativa", "Bidireccional"]
        if 0 <= idx < len(nombres):
            self.algoritmo_actual = nombres[idx]
            self.reset_animacion()
            self.actualizar_vistas()

    def on_tree_mode_change(self):
        self.modo_arbol = self.var_modo_arbol.get()
        self.dibujar_arbol_canvas()

    # ==========================================================================
    # RENDERIZADO DE CUADRÍCULA (AULA 20x10)
    # ==========================================================================

    def dibujar_cuadricula(self, paso_activo=None):
        self.canvas_grid.delete("all")
        w = self.canvas_grid.winfo_width() or 380
        h = self.canvas_grid.winfo_height() or 480

        cell_w = w / ANCHO
        cell_h = h / LARGO

        res = next((r for r in self.resultados if r["algoritmo"] == self.algoritmo_actual), None)
        camino = res["camino"] if (res and res["encontrado"]) else []
        camino_set = set(camino)

        limite_paso = paso_activo if paso_activo is not None else len(camino)

        for r in range(LARGO):
            for c in range(ANCHO):
                x1 = c * cell_w
                y1 = r * cell_h
                x2 = x1 + cell_w
                y2 = y1 + cell_h

                estado = (r, c)
                color = self.COLOR_CELL_BG
                txt = f"{r},{c}"
                txt_color = "#334155"

                # Color según estado
                if estado == self.inicio:
                    color = self.COLOR_START
                    txt = "I"
                    txt_color = "#ffffff"
                elif estado == self.objetivo:
                    color = self.COLOR_GOAL
                    txt = "O"
                    txt_color = "#ffffff"
                elif estado in camino[:limite_paso]:
                    color = self.COLOR_PATH
                    txt = "*"
                    txt_color = "#000000"

                # Paso actual animado
                if paso_activo is not None and paso_activo < len(camino) and camino[paso_activo] == estado:
                    color = self.COLOR_CURRENT
                    txt_color = "#000000"

                self.canvas_grid.create_rectangle(x1 + 1, y1 + 1, x2 - 1, y2 - 1, fill=color, outline=self.COLOR_CELL_BORDER, tags=f"cell_{r}_{c}")
                self.canvas_grid.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=txt, fill=txt_color, font=("Segoe UI", 7, "bold"))

    def on_grid_click(self, event):
        w = self.canvas_grid.winfo_width()
        h = self.canvas_grid.winfo_height()
        c = int(event.x // (w / ANCHO))
        r = int(event.y // (h / LARGO))

        if 0 <= r < LARGO and 0 <= c < ANCHO:
            if (r, c) != self.objetivo:
                self.inicio = (r, c)
                self.resolver_todo()

    # ==========================================================================
    # ANIMACIÓN PASO A PASO DEL CAMINO
    # ==========================================================================

    def toggle_animacion(self):
        if self.anim_activa:
            self.pausar_animacion()
        else:
            self.iniciar_animacion()

    def iniciar_animacion(self):
        res = next((r for r in self.resultados if r["algoritmo"] == self.algoritmo_actual), None)
        if not res or not res["encontrado"]:
            return
        
        self.anim_activa = True
        self.btn_play.config(text="⏸ Pausar")
        self.loop_animacion()

    def pausar_animacion(self):
        self.anim_activa = False
        self.btn_play.config(text="▶ Reproducir")
        if self.anim_job:
            self.after_cancel(self.anim_job)
            self.anim_job = None

    def paso_siguiente(self):
        self.pausar_animacion()
        res = next((r for r in self.resultados if r["algoritmo"] == self.algoritmo_actual), None)
        if not res or not res["encontrado"]:
            return
        
        camino = res["camino"]
        if self.anim_paso < len(camino):
            self.dibujar_cuadricula(self.anim_paso)
            self.lbl_paso_info.config(text=f"Paso: {self.anim_paso} / {len(camino)-1}")
            self.anim_paso += 1

    def reset_animacion(self):
        self.pausar_animacion()
        self.anim_paso = 0
        self.dibujar_cuadricula()
        res = next((r for r in self.resultados if r["algoritmo"] == self.algoritmo_actual), None)
        total = len(res["camino"]) - 1 if (res and res["encontrado"]) else 0
        self.lbl_paso_info.config(text=f"Paso: 0 / {total}")

    def loop_animacion(self):
        if not self.anim_activa:
            return
        res = next((r for r in self.resultados if r["algoritmo"] == self.algoritmo_actual), None)
        camino = res["camino"] if (res and res["encontrado"]) else []

        if self.anim_paso < len(camino):
            self.dibujar_cuadricula(self.anim_paso)
            self.lbl_paso_info.config(text=f"Paso: {self.anim_paso} / {len(camino)-1}")
            self.anim_paso += 1
            self.anim_job = self.after(self.anim_velocidad_ms, self.loop_animacion)
        else:
            self.pausar_animacion()

    # ==========================================================================
    # RENDERIZADO VISUAL DEL ÁRBOL DE BÚSQUEDA
    # ==========================================================================

    def dibujar_arbol_canvas(self):
        self.canvas_tree.delete("all")
        res = next((r for r in self.resultados if r["algoritmo"] == self.algoritmo_actual), None)
        if not res:
            return

        raiz = res["raiz"]
        camino_set = set(res["camino"]) if res["encontrado"] else set()

        if self.algoritmo_actual == "Bidireccional" and isinstance(raiz, tuple):
            raiz_ini, raiz_obj = raiz
            self.render_tree_hierarchy(raiz_ini, camino_set, start_x=80, start_y=60, tag_prefix="ini", color="#38bdf8")
            self.render_tree_hierarchy(raiz_obj, camino_set, start_x=650, start_y=60, tag_prefix="obj", color="#ec4899")
        else:
            self.render_tree_hierarchy(raiz, camino_set, start_x=120, start_y=60, tag_prefix="root", color="#38bdf8")

        self.canvas_tree.config(scrollregion=self.canvas_tree.bbox("all"))

    def render_tree_hierarchy(self, root_node, camino_set, start_x, start_y, tag_prefix, color):
        if not root_node:
            return

        # Filtrar o podar según modo
        max_depth = 4 if self.modo_arbol == "acotado" else 12
        solo_solucion = (self.modo_arbol == "solucion")

        # 1. Asignar coordenadas X, Y a cada nodo
        nodes_data = []
        links_data = []
        counter = [0]
        cur_x = [start_x]

        def layout_node(nodo, depth=0):
            if not nodo or depth > max_depth:
                return None

            if solo_solucion and nodo.estado not in camino_set:
                return None

            n_id = f"{tag_prefix}_{counter[0]}"
            counter[0] += 1

            children_objs = []
            for h in nodo.hijos:
                ch = layout_node(h, depth + 1)
                if ch:
                    children_objs.append(ch)
                    links_data.append((n_id, ch["id"], nodo.estado in camino_set and ch["nodo"].estado in camino_set))

            item = {
                "id": n_id,
                "nodo": nodo,
                "depth": depth,
                "children": children_objs,
                "x": 0,
                "y": start_y + depth * int(65 * self.zoom_arbol)
            }

            if not children_objs:
                item["x"] = cur_x[0]
                cur_x[0] += int(48 * self.zoom_arbol)
            else:
                first_x = children_objs[0]["x"]
                last_x = children_objs[-1]["x"]
                item["x"] = (first_x + last_x) / 2

            nodes_data.append(item)
            return item

        layout_node(root_node, 0)
        node_map = {n["id"]: n for n in nodes_data}

        # 2. Dibujar Enlaces (Líneas)
        for s_id, t_id, is_sol in links_data:
            s = node_map.get(s_id)
            t = node_map.get(t_id)
            if s and t:
                line_color = "#f59e0b" if is_sol else "#334155"
                line_width = int(3 * self.zoom_arbol) if is_sol else int(1.5 * self.zoom_arbol)
                self.canvas_tree.create_line(s["x"], s["y"], t["x"], t["y"], fill=line_color, width=line_width, smooth=True)

        # 3. Dibujar Nodos (Círculos)
        r = int(14 * self.zoom_arbol)
        for n in nodes_data:
            nodo = n["nodo"]
            x, y = n["x"], n["y"]
            es_sol = nodo.estado in camino_set

            fill_c = "#f59e0b" if es_sol else self.COLOR_PANEL
            outline_c = "#ffffff" if es_sol else color
            width_c = int(2.5 * self.zoom_arbol) if es_sol else int(1.5 * self.zoom_arbol)

            tag_id = f"node_{n['id']}"
            self.canvas_tree.create_oval(x - r, y - r, x + r, y + r, fill=fill_c, outline=outline_c, width=width_c, tags=tag_id)
            self.canvas_tree.create_text(x, y, text=f"{nodo.estado[0]},{nodo.estado[1]}", fill="#000000" if es_sol else "#ffffff", font=("Segoe UI", max(6, int(7 * self.zoom_arbol)), "bold"), tags=tag_id)

            # Binding clic en nodo para inspección
            self.canvas_tree.tag_bind(tag_id, "<Button-1>", lambda e, nd=nodo, sol=es_sol: self.inspeccionar_nodo(nd, sol))

    def inspeccionar_nodo(self, nodo, es_sol):
        tag_sol = " ★ [EN CAMINO SOLUCIÓN]" if es_sol else ""
        accion_str = f"[{nodo.accion}]" if nodo.accion else "[Inicio]"
        self.node_info_bar.config(
            text=f"🔍 Nodo: ({nodo.estado[0]}, {nodo.estado[1]})  |  Acción: {accion_str}  |  Nivel: {nodo.level if hasattr(nodo, 'level') else nodo.nivel}  |  Costo: {nodo.costo}{tag_sol}",
            fg="#f59e0b" if es_sol else self.COLOR_TEXT
        )

    # Zoom y Pan del Árbol
    def zoom_tree(self, factor):
        self.zoom_arbol = max(0.4, min(2.5, self.zoom_arbol * factor))
        self.dibujar_arbol_canvas()

    def reset_tree_zoom(self):
        self.zoom_arbol = 1.0
        self.dibujar_arbol_canvas()

    def on_tree_press(self, event):
        self.canvas_tree.scan_mark(event.x, event.y)

    def on_tree_drag(self, event):
        self.canvas_tree.scan_dragto(event.x, event.y, gain=1)

    # ==========================================================================
    # ACTUALIZACIÓN DE TABLA COMPARATIVA
    # ==========================================================================

    def actualizar_tabla_resultados(self):
        for item in self.tree_table.get_children():
            self.tree_table.delete(item)

        for r in self.resultados:
            es_mejor = self.mejor and self.mejor["algoritmo"] == r["algoritmo"]
            nombre = f"🏆 {r['algoritmo']}" if es_mejor else r['algoritmo']
            
            valores = (
                nombre,
                r["estructura"],
                "Sí" if r["encontrado"] else "No",
                r["costo"] if r["encontrado"] else "-",
                r["nivel"] if r["encontrado"] else "-",
                f"{r['nodos_generados']:,}",
                f"{r['nodos_expandidos']:,}",
                f"{r['max_estructura']}",
                f"{r['tiempo']:.6f}",
                r["comp_tiempo_t"],
                r["comp_espacio_t"]
            )
            self.tree_table.insert("", tk.END, values=valores)


def main():
    app = BusquedasGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
