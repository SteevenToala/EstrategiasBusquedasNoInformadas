import random
import time
from collections import deque

# ==============================================================================
# 1. DEFINICIÓN DEL PROBLEMA Y AMBIENTE
# ==============================================================================

ANCHO = 10   # Columnas del aula (X)
LARGO = 20   # Filas del aula (Y)

# Punto objetivo fijo
OBJETIVO = (11, 8)

# Acciones opuestas para reconstrucción del camino en búsqueda bidireccional
ACCION_OPUESTA = {
    "Arriba": "Abajo",
    "Abajo": "Arriba",
    "Derecha": "Izquierda",
    "Izquierda": "Derecha",
}

def estado_valido(estado):
    """Verifica que las coordenadas estén dentro de los límites del aula."""
    fila, col = estado
    return 0 <= fila < LARGO and 0 <= col < ANCHO

def generar_estado_inicial(semilla=None):
    """Genera un estado inicial aleatorio dentro del aula distinto del objetivo."""
    rng = random.Random(semilla) if semilla is not None else random.Random()
    while True:
        estado = (rng.randint(0, LARGO - 1), rng.randint(0, ANCHO - 1))
        if estado_valido(estado) and estado != OBJETIVO:
            return estado

def funcion_sucesora(estado):
    """Genera los estados alcanzables aplicando los 4 operadores de movimiento."""
    fila, col = estado
    movimientos = [
        ("Arriba", (-1, 0)),
        ("Abajo", (1, 0)),
        ("Derecha", (0, 1)),
        ("Izquierda", (0, -1)),
    ]
    sucesores = []
    for nombre, (dfila, dcol) in movimientos:
        nuevo = (fila + dfila, col + dcol)
        if estado_valido(nuevo):
            sucesores.append((nombre, nuevo, 1))
    return sucesores

def test_objetivo(estado):
    """Prueba si el estado actual corresponde a la meta final."""
    return estado == OBJETIVO


# ==============================================================================
# 2. CLASE NODO DEL ÁRBOL DE BÚSQUEDA
# ==============================================================================

class Nodo:
    def __init__(self, estado, padre=None, accion=None, costo=0, nivel=0):
        self.estado = estado          # Coordenadas (fila, columna)
        self.padre = padre            # Nodo padre
        self.accion = accion          # Acción que generó este nodo
        self.costo = costo            # Costo acumulado del camino
        self.nivel = nivel            # Profundidad en el árbol
        self.hijos = []               # Lista de nodos hijos

    def agregar_hijo(self, hijo):
        self.hijos.append(hijo)

    def camino(self):
        """Retorna la lista de coordenadas desde la raíz hasta este nodo."""
        nodo, camino = self, []
        while nodo is not None:
            camino.append(nodo.estado)
            nodo = nodo.padre
        camino.reverse()
        return camino

    def acciones(self):
        """Retorna la lista de acciones tomadas desde la raíz hasta este nodo."""
        nodo, accs = self, []
        while nodo is not None:
            if nodo.accion is not None:
                accs.append(nodo.accion)
            nodo = nodo.padre
        accs.reverse()
        return accs

    def __repr__(self):
        return f"Nodo(estado={self.estado}, nivel={self.nivel}, costo={self.costo})"


def _empaquetar_resultado(nombre, estructura, comp_tiempo_t, comp_espacio_t,
                           nodo, nodos_generados, nodos_expandidos,
                           max_estructura, inicio_t, raiz=None):
    tiempo = time.perf_counter() - inicio_t
    if nodo is None:
        return {
            "algoritmo": nombre,
            "estructura": estructura,
            "comp_tiempo_t": comp_tiempo_t,
            "comp_espacio_t": comp_espacio_t,
            "encontrado": False,
            "camino": [],
            "acciones": [],
            "costo": None,
            "nivel": None,
            "nodos_generados": nodos_generados,
            "nodos_expandidos": nodos_expandidos,
            "max_estructura": max_estructura,
            "tiempo": tiempo,
            "raiz": raiz
        }
    return {
        "algoritmo": nombre,
        "estructura": estructura,
        "comp_tiempo_t": comp_tiempo_t,
        "comp_espacio_t": comp_espacio_t,
        "encontrado": True,
        "camino": nodo.camino(),
        "acciones": nodo.acciones(),
        "costo": nodo.costo,
        "nivel": nodo.nivel,
        "nodos_generados": nodos_generados,
        "nodos_expandidos": nodos_expandidos,
        "max_estructura": max_estructura,
        "tiempo": tiempo,
        "raiz": raiz
    }


# ==============================================================================
# 3. ALGORITMOS DE BÚSQUEDA NO INFORMADA
# ==============================================================================

# --- 3.1 Búsqueda en Anchura (BFS) ---
def bfs(estado_inicial):
    inicio_t = time.perf_counter()
    raiz = Nodo(estado_inicial)

    if test_objetivo(estado_inicial):
        return _empaquetar_resultado(
            "BFS", "Cola FIFO (deque)", "O(b^d)", "O(b^d)",
            raiz, 1, 0, 1, inicio_t, raiz
        )

    frontera = deque([raiz])          # COLA FIFO
    visitados = {estado_inicial}      # Control de estados visitados (Búsqueda en Grafo)
    nodos_generados = 1
    nodos_expandidos = 0
    max_frontera = 1

    while frontera:
        max_frontera = max(max_frontera, len(frontera))
        nodo = frontera.popleft()
        nodos_expandidos += 1

        for accion, estado, costo_paso in funcion_sucesora(nodo.estado):
            if estado not in visitados:
                visitados.add(estado)
                hijo = Nodo(estado, padre=nodo, accion=accion,
                            costo=nodo.costo + costo_paso, nivel=nodo.nivel + 1)
                nodo.agregar_hijo(hijo)
                nodos_generados += 1

                if test_objetivo(estado):
                    return _empaquetar_resultado(
                        "BFS", "Cola FIFO (deque)", "O(b^d)", "O(b^d)",
                        hijo, nodos_generados, nodos_expandidos, max_frontera, inicio_t, raiz
                    )
                frontera.append(hijo)

    return _empaquetar_resultado(
        "BFS", "Cola FIFO (deque)", "O(b^d)", "O(b^d)",
        None, nodos_generados, nodos_expandidos, max_frontera, inicio_t, raiz
    )


# --- 3.2 Búsqueda en Profundidad (DFS) ---
def dfs(estado_inicial):
    inicio_t = time.perf_counter()
    raiz = Nodo(estado_inicial)

    if test_objetivo(estado_inicial):
        return _empaquetar_resultado(
            "DFS", "Pila LIFO (list)", "O(b^m)", "O(b·m)",
            raiz, 1, 0, 1, inicio_t, raiz
        )

    pila = [raiz]                      # PILA LIFO
    visitados = {estado_inicial}
    nodos_generados = 1
    nodos_expandidos = 0
    max_pila = 1

    while pila:
        max_pila = max(max_pila, len(pila))
        nodo = pila.pop()
        nodos_expandidos += 1

        for accion, estado, costo_paso in funcion_sucesora(nodo.estado):
            if estado not in visitados:
                visitados.add(estado)
                hijo = Nodo(estado, padre=nodo, accion=accion,
                            costo=nodo.costo + costo_paso, nivel=nodo.nivel + 1)
                nodo.agregar_hijo(hijo)
                nodos_generados += 1

                if test_objetivo(estado):
                    return _empaquetar_resultado(
                        "DFS", "Pila LIFO (list)", "O(b^m)", "O(b·m)",
                        hijo, nodos_generados, nodos_expandidos, max_pila, inicio_t, raiz
                    )
                pila.append(hijo)

    return _empaquetar_resultado(
        "DFS", "Pila LIFO (list)", "O(b^m)", "O(b·m)",
        None, nodos_generados, nodos_expandidos, max_pila, inicio_t, raiz
    )


# --- 3.3 Búsqueda en Profundidad Iterativa (IDDFS) ---
def dfs_iterativa(estado_inicial):
    inicio_t = time.perf_counter()
    raiz_principal = Nodo(estado_inicial)

    if test_objetivo(estado_inicial):
        return _empaquetar_resultado(
            "DFS iterativa", "Pila LIFO + Limite", "O(b^d)", "O(b*d)",
            raiz_principal, 1, 0, 1, inicio_t, raiz_principal
        )

    total_generados = 0
    total_expandidos = 0
    global_max_pila = 0
    limite = 0

    while True:
        raiz = Nodo(estado_inicial)
        pila = [raiz]                  # PILA LIFO
        mejor_nivel = {estado_inicial: 0}
        nodos_generados = 1
        max_pila = 1
        hubo_poda = False

        while pila:
            max_pila = max(max_pila, len(pila))
            nodo = pila.pop()
            total_expandidos += 1

            if nodo.nivel < limite:
                for accion, estado, costo_paso in funcion_sucesora(nodo.estado):
                    nuevo_nivel = nodo.nivel + 1
                    if estado not in mejor_nivel or nuevo_nivel < mejor_nivel[estado]:
                        mejor_nivel[estado] = nuevo_nivel
                        hijo = Nodo(estado, padre=nodo, accion=accion,
                                    costo=nodo.costo + costo_paso, nivel=nuevo_nivel)
                        nodo.agregar_hijo(hijo)
                        nodos_generados += 1

                        if test_objetivo(estado):
                            total_generados += nodos_generados
                            global_max_pila = max(global_max_pila, max_pila)
                            return _empaquetar_resultado(
                                "DFS iterativa", "Pila LIFO + Limite", "O(b^d)", "O(b*d)",
                                hijo, total_generados, total_expandidos, global_max_pila, inicio_t, raiz
                            )
                        pila.append(hijo)
            else:
                hubo_poda = True

        total_generados += nodos_generados
        global_max_pila = max(global_max_pila, max_pila)

        if not hubo_poda:
            break

        limite += 1

    return _empaquetar_resultado(
        "DFS iterativa", "Pila LIFO + Limite", "O(b^d)", "O(b*d)",
        None, total_generados, total_expandidos, global_max_pila, inicio_t, raiz_principal
    )


# --- 3.4 Búsqueda Bidireccional ---
def _expandir_un_paso(frontera_propia, visitados_propios, visitados_opuestos):
    nodo = frontera_propia.popleft()
    generados = 0
    for accion, estado, costo_paso in funcion_sucesora(nodo.estado):
        if estado not in visitados_propios:
            hijo = Nodo(estado, padre=nodo, accion=accion,
                        costo=nodo.costo + costo_paso, nivel=nodo.nivel + 1)
            nodo.agregar_hijo(hijo)
            visitados_propios[estado] = hijo
            frontera_propia.append(hijo)
            generados += 1
            if estado in visitados_opuestos:
                return hijo, visitados_opuestos[estado], generados
    return None, None, generados


def bidireccional(estado_inicial):
    inicio_t = time.perf_counter()

    if estado_inicial == OBJETIVO:
        raiz = Nodo(estado_inicial)
        return _empaquetar_resultado(
            "Bidireccional", "2 Colas + 2 Dicts", "O(b^(d/2))", "O(b^(d/2))",
            raiz, 1, 0, 1, inicio_t, (raiz, raiz)
        )

    raiz_ini = Nodo(estado_inicial)
    raiz_obj = Nodo(OBJETIVO)

    frontera_ini = deque([raiz_ini])
    frontera_obj = deque([raiz_obj])
    visitados_ini = {estado_inicial: raiz_ini}
    visitados_obj = {OBJETIVO: raiz_obj}

    nodos_generados = 2
    nodos_expandidos = 0
    max_estructura = 2

    while frontera_ini and frontera_obj:
        max_estructura = max(max_estructura, len(frontera_ini) + len(frontera_obj))

        # Se expande el lado con menor frontera
        if len(frontera_ini) <= len(frontera_obj):
            nodo_ini, nodo_obj, generados = _expandir_un_paso(
                frontera_ini, visitados_ini, visitados_obj)
        else:
            nodo_obj, nodo_ini, generados = _expandir_un_paso(
                frontera_obj, visitados_obj, visitados_ini)

        nodos_generados += generados
        nodos_expandidos += 1

        if nodo_ini is not None and nodo_obj is not None:
            # Reconstrucción completa del camino y acciones
            mitad_ini = nodo_ini.camino()
            mitad_obj = nodo_obj.camino()
            camino_completo = mitad_ini + list(reversed(mitad_obj[:-1]))

            accs_ini = nodo_ini.acciones()
            accs_obj_invertidas = [ACCION_OPUESTA[a] for a in reversed(nodo_obj.acciones())]
            acciones_completas = accs_ini + accs_obj_invertidas

            costo_total = nodo_ini.costo + nodo_obj.costo
            tiempo = time.perf_counter() - inicio_t
            return {
                "algoritmo": "Bidireccional",
                "estructura": "2 Colas + 2 Dicts",
                "comp_tiempo_t": "O(b^(d/2))",
                "comp_espacio_t": "O(b^(d/2))",
                "encontrado": True,
                "camino": camino_completo,
                "acciones": acciones_completas,
                "costo": costo_total,
                "nivel": len(camino_completo) - 1,
                "nodos_generados": nodos_generados,
                "nodos_expandidos": nodos_expandidos,
                "max_estructura": max_estructura,
                "tiempo": tiempo,
                "raiz": (raiz_ini, raiz_obj),
                "encuentro": nodo_ini.estado
            }

    return _empaquetar_resultado(
        "Bidireccional", "2 Colas + 2 Dicts", "O(b^(d/2))", "O(b^(d/2))",
        None, nodos_generados, nodos_expandidos, max_estructura, inicio_t, (raiz_ini, raiz_obj)
    )


# ==============================================================================
# 4. VISUALIZACIÓN DE CUADRÍCULA Y ÁRBOLES
# ==============================================================================

def imprimir_cuadricula(estado_inicial, camino=None):
    camino_set = set(camino) if camino else set()
    lineas = []
    
    # Encabezado de columnas
    header = "     " + " ".join(f"{c:2d}" for c in range(ANCHO))
    lineas.append(header)
    lineas.append("    +" + "--" * ANCHO + "-+")
    
    for fila in range(LARGO):
        celdas = []
        for col in range(ANCHO):
            estado = (fila, col)
            if estado == estado_inicial and estado == OBJETIVO:
                c = "IO"
            elif estado == OBJETIVO:
                c = " O"
            elif estado == estado_inicial:
                c = " I"
            elif estado in camino_set:
                c = " *"
            else:
                c = " ."
            celdas.append(c)
        lineas.append(f"{fila:2d}  |" + "".join(celdas) + " |")
    
    lineas.append("    +" + "--" * ANCHO + "-+")
    return "\n".join(lineas)


def imprimir_arbol(nodo, prefijo="", es_ultimo=True, contador_nodos=None,
                   limite_nodos=300, max_profundidad=None, camino_solucion=None):
    """
    Imprime el árbol de búsqueda de forma visual y jerárquica.
    - Resalta con [★ SOLUCIÓN] los nodos que forman parte de la respuesta.
    - Permite limitar profundidad o total de nodos para evitar saturación de pantalla.
    """
    if contador_nodos is None:
        contador_nodos = [0]

    if nodo is None:
        return

    if max_profundidad is not None and nodo.nivel > max_profundidad:
        return

    if contador_nodos[0] >= limite_nodos:
        if contador_nodos[0] == limite_nodos:
            print(prefijo + "└── ... [Límite de visualización alcanzado]")
            contador_nodos[0] += 1
        return

    contador_nodos[0] += 1

    marcador = "└── " if es_ultimo else "├── "
    accion_str = f"[{nodo.accion}] " if nodo.accion else "[Inicio] "
    
    es_solucion = False
    if camino_solucion and nodo.estado in camino_solucion:
        es_solucion = True

    sol_tag = " [*] [EN CAMINO SOLUCION]" if es_solucion else ""
    info_nodo = f"{accion_str}Estado: {nodo.estado} (nivel={nodo.nivel}, costo={nodo.costo}){sol_tag}"

    if prefijo == "":
        print(f"{info_nodo}")
    else:
        print(f"{prefijo}{marcador}{info_nodo}")

    prefijo_hijos = prefijo + ("    " if es_ultimo else "│   ")

    for i, hijo in enumerate(nodo.hijos):
        es_ultimo_hijo = (i == len(nodo.hijos) - 1)
        imprimir_arbol(
            hijo, prefijo_hijos, es_ultimo_hijo,
            contador_nodos, limite_nodos, max_profundidad, camino_solucion
        )


def imprimir_solo_camino_arbol(nodo_raiz, camino_solucion):
    """Imprime exclusivamente la rama del arbol que conduce a la meta."""
    if not camino_solucion:
        print("No hay camino solucion para mostrar.")
        return

    print("Rama del arbol correspondiente a la solucion:")
    nodo_actual = nodo_raiz
    nivel = 0
    
    for idx, estado in enumerate(camino_solucion):
        indent = "  " * nivel + ("└── " if nivel > 0 else "")
        accion = f"[{nodo_actual.accion}] " if nodo_actual.accion else "[Inicio] "
        meta_tag = " (META OBJETIVO ALCANZADO)" if estado == OBJETIVO else ""
        print(f"{indent}{accion}Estado: {estado} (paso {idx}){meta_tag}")
        
        if idx + 1 < len(camino_solucion):
            siguiente_estado = camino_solucion[idx + 1]
            hijo_encontrado = None
            for h in nodo_actual.hijos:
                if h.estado == siguiente_estado:
                    hijo_encontrado = h
                    break
            if hijo_encontrado:
                nodo_actual = hijo_encontrado
                nivel += 1
            else:
                nivel += 1


# ==============================================================================
# 5. TABLAS COMPARATIVAS Y SOLUCIONES
# ==============================================================================

def ejecutar_comparacion(semilla=None):
    """Ejecuta los 4 algoritmos sobre el mismo punto de inicio."""
    estado_inicial = generar_estado_inicial(semilla)

    resultados = [
        bfs(estado_inicial),
        dfs(estado_inicial),
        dfs_iterativa(estado_inicial),
        bidireccional(estado_inicial),
    ]
    return estado_inicial, resultados


def imprimir_tabla_completa(resultados):
    print("=" * 115)
    print("TABLA 1: METRICAS EXPERIMENTALES Y ESTRUCTURA DE DATOS UTILIZADA")
    print("=" * 115)
    encabezado = (f"{'Algoritmo':<15}{'Estructura de Datos':<22}{'Solucion':<10}{'Costo':<7}{'Nivel':<7}"
                  f"{'Generados':<11}{'Expandidos':<12}{'Max.Memoria':<14}{'Tiempo (s)':<10}")
    print(encabezado)
    print("-" * 115)
    for r in resultados:
        sol = "Si" if r["encontrado"] else "No"
        costo = str(r["costo"]) if r["encontrado"] else "-"
        nivel = str(r["nivel"]) if r["encontrado"] else "-"
        print(f"{r['algoritmo']:<15}{r['estructura']:<22}{sol:<10}{costo:<7}{nivel:<7}"
              f"{r['nodos_generados']:<11}{r['nodos_expandidos']:<12}"
              f"{r['max_estructura']:<14}{r['tiempo']:.6f}")
    print("-" * 115)

    print("\n" + "=" * 115)
    print("TABLA 2: ANALISIS DE COMPLEJIDAD TEORICA vs. PRACTICA")
    print("  * b = factor de ramificacion (max. 4: Arriba, Abajo, Izq, Der)")
    print("  * d = profundidad de la solucion optima")
    print("  * m = profundidad maxima del espacio de estados")
    print("=" * 115)
    encabezado_teorico = (f"{'Algoritmo':<16}{'Comp. Tiempo Teorica':<24}{'Comp. Espacio Teorica':<24}"
                          f"{'Completo':<12}{'Optimo':<10}{'Comentario':<25}")
    print(encabezado_teorico)
    print("-" * 115)
    print(f"{'BFS':<16}{'O(b^d)':<24}{'O(b^d)':<24}{'Si':<12}{'Si (costo=1)':<10}{'Garantiza menor camino':<25}")
    print(f"{'DFS':<16}{'O(b^m)':<24}{'O(b*m)':<24}{'Si (visitados)':<12}{'No':<10}{'Bajo uso de memoria':<25}")
    print(f"{'DFS Iterativa':<16}{'O(b^d)':<24}{'O(b*d)':<24}{'Si':<12}{'Si (costo=1)':<10}{'Memoria DFS + optimo':<25}")
    print(f"{'Bidireccional':<16}{'O(b^(d/2))':<24}{'O(b^(d/2))':<24}{'Si':<12}{'Si (costo=1)':<10}{'Muy rapida (busca en 2 lados)':<25}")
    print("=" * 115)


def mostrar_todas_las_soluciones(estado_inicial, resultados):
    print("\n" + "=" * 80)
    print("DETALLE DE TODAS LAS POSIBLES SOLUCIONES ENCONTRADAS")
    print("=" * 80)
    for r in resultados:
        print(f"\n[>] Algoritmo: {r['algoritmo']}")
        if not r["encontrado"]:
            print("  [X] No encontro solucion.")
            continue
        print(f"  [OK] Solucion encontrada | Costo total: {r['costo']} | Pasos (Nivel): {r['nivel']}")
        print(f"  Secuencia de acciones ({len(r['acciones'])} pasos):")
        
        accs = r["acciones"]
        if accs:
            partes = []
            for i in range(0, len(accs), 8):
                partes.append(" -> ".join(accs[i:i+8]))
            print("    " + "\n    -> ".join(partes))
        else:
            print("    [Inicio y Objetivo coinciden]")

        print(f"  Coordenadas del camino ({len(r['camino'])} estados):")
        cam = r["camino"]
        partes_c = []
        for i in range(0, len(cam), 6):
            partes_c.append(" -> ".join(str(c) for c in cam[i:i+6]))
        print("    " + "\n    -> ".join(partes_c))


def mejor_solucion(resultados):
    encontradas = [r for r in resultados if r["encontrado"]]
    if not encontradas:
        return None
    return min(encontradas, key=lambda r: (r["costo"], r["tiempo"]))


# ==============================================================================
# 6. PROGRAMA PRINCIPAL CON MENÚ INTERACTIVO
# ==============================================================================

def menu_visualizar_arbol(resultados):
    nombres_opcion = {
        "1": "BFS",
        "2": "DFS",
        "3": "DFS iterativa",
        "4": "Bidireccional",
    }
    
    while True:
        print("\n--- Visualización de Árboles de Búsqueda ---")
        print("  1 - BFS")
        print("  2 - DFS")
        print("  3 - DFS iterativa")
        print("  4 - Bidireccional")
        print("  0 - Volver al menú principal")
        opcion = input("Elige el algoritmo a inspeccionar: ").strip()

        if opcion == "0":
            break

        if opcion not in nombres_opcion:
            print("Opción inválida.")
            continue

        nombre_elegido = nombres_opcion[opcion]
        resultado_elegido = next((r for r in resultados if r["algoritmo"] == nombre_elegido), None)

        if resultado_elegido is None or resultado_elegido["raiz"] is None:
            print(f"No hay árbol disponible para {nombre_elegido}.")
            continue

        print(f"\n¿Como deseas ver el arbol de {nombre_elegido}?")
        print("  1 - Solo la rama del camino solucion (limpia y directa)")
        print("  2 - Arbol completo explorado (con nodos solucion resaltados [*])")
        print("  3 - Arbol acotado por niveles (profundidad max: 4)")
        modo = input("Opcion de visualizacion: ").strip()

        camino_sol = resultado_elegido["camino"] if resultado_elegido["encontrado"] else []

        if nombre_elegido == "Bidireccional":
            raiz_ini, raiz_obj = resultado_elegido["raiz"]
            if modo == "1":
                print("\n>> Camino solucion (Encuentro en", resultado_elegido.get("encuentro", "N/A"), "):")
                print(" -> ".join(str(c) for c in camino_sol))
            elif modo == "3":
                print("\n>> Arbol desde el Inicio (niveles 0-4):")
                imprimir_arbol(raiz_ini, max_profundidad=4, camino_solucion=set(camino_sol))
                print("\n>> Arbol desde el Objetivo (niveles 0-4):")
                imprimir_arbol(raiz_obj, max_profundidad=4, camino_solucion=set(camino_sol))
            else:
                print("\n>> Arbol completo desde el Inicio:")
                imprimir_arbol(raiz_ini, limite_nodos=150, camino_solucion=set(camino_sol))
                print("\n>> Arbol completo desde el Objetivo:")
                imprimir_arbol(raiz_obj, limite_nodos=150, camino_solucion=set(camino_sol))
        else:
            raiz = resultado_elegido["raiz"]
            if modo == "1":
                imprimir_solo_camino_arbol(raiz, camino_sol)
            elif modo == "3":
                imprimir_arbol(raiz, max_profundidad=4, camino_solucion=set(camino_sol))
            else:
                imprimir_arbol(raiz, limite_nodos=250, camino_solucion=set(camino_sol))


def menu_mapas(estado_inicial, resultados):
    nombres_opcion = {
        "1": "BFS",
        "2": "DFS",
        "3": "DFS iterativa",
        "4": "Bidireccional",
    }
    while True:
        print("\n--- Mapas de Soluciones en la Cuadricula ---")
        print("  1 - Ver mapa de BFS")
        print("  2 - Ver mapa de DFS")
        print("  3 - Ver mapa de DFS iterativa")
        print("  4 - Ver mapa de Bidireccional")
        print("  5 - Ver mapa de la MEJOR solucion")
        print("  0 - Volver")
        opc = input("Selecciona una opcion: ").strip()

        if opc == "0":
            break
        elif opc == "5":
            mejor = mejor_solucion(resultados)
            print(f"\n[MAPA: MEJOR SOLUCION -> {mejor['algoritmo']}]")
            print("  I = Inicio | O = Objetivo | * = Camino recorrido | . = Libre\n")
            print(imprimir_cuadricula(estado_inicial, mejor["camino"]))
        elif opc in nombres_opcion:
            nombre = nombres_opcion[opc]
            res = next((r for r in resultados if r["algoritmo"] == nombre), None)
            if res and res["encontrado"]:
                print(f"\n[MAPA: {nombre}] (Costo: {res['costo']}, Pasos: {res['nivel']})")
                print("  I = Inicio | O = Objetivo | * = Camino recorrido | . = Libre\n")
                print(imprimir_cuadricula(estado_inicial, res["camino"]))
            else:
                print(f"{nombre} no encontro solucion o no esta disponible.")
        else:
            print("Opcion no valida.")


def main():
    print("=" * 60)
    print(" SISTEMA DE BUSQUEDAS NO INFORMADAS - AULA DE CLASES")
    print("=" * 60)
    print(f"Dimensiones del Aula: {LARGO} filas x {ANCHO} columnas")
    print(f"Punto Objetivo (Fijo): {OBJETIVO}")
    
    # Inicio aleatorio automatico en cada corrida
    semilla = None
    modo_inicio = input("\n¿Deseas usar un inicio 100% aleatorio? (S/n): ").strip().lower()
    if modo_inicio == "n":
        try:
            semilla = int(input("Ingresa un numero entero para la semilla: ").strip())
        except ValueError:
            print("Semilla no valida, se usara inicio aleatorio.")
            semilla = None

    estado_inicial, resultados = ejecutar_comparacion(semilla=semilla)

    print(f"\n>>> Punto Inicial generado: {estado_inicial}")
    print(f">>> Punto Objetivo fijo:     {OBJETIVO}\n")

    imprimir_tabla_completa(resultados)
    
    mejor = mejor_solucion(resultados)
    if mejor:
        print(f"\n[MEJOR SOLUCION ENCONTRADA]: {mejor['algoritmo']}")
        print(f"   - Costo: {mejor['costo']} pasos")
        print(f"   - Nodos expandidos: {mejor['nodos_expandidos']}")
        print(f"   - Tiempo real: {mejor['tiempo']:.6f} segundos")

    while True:
        print("\n" + "=" * 45)
        print("           MENU PRINCIPAL")
        print("=" * 45)
        print("  1 - Ver tabla de metricas y complejidades")
        print("  2 - Ver detalle de todas las soluciones (caminos y acciones)")
        print("  3 - Ver mapas en cuadricula de las soluciones")
        print("  4 - Visualizar e inspeccionar arboles de busqueda")
        print("  5 - Generar NUEVO punto de inicio aleatorio y reejecutar")
        print("  0 - Salir")
        opcion = input("Selecciona una opcion: ").strip()

        if opcion == "1":
            imprimir_tabla_completa(resultados)
        elif opcion == "2":
            mostrar_todas_las_soluciones(estado_inicial, resultados)
        elif opcion == "3":
            menu_mapas(estado_inicial, resultados)
        elif opcion == "4":
            menu_visualizar_arbol(resultados)
        elif opcion == "5":
            estado_inicial, resultados = ejecutar_comparacion(semilla=None)
            print(f"\n>>> Nuevo Punto Inicial aleatorio: {estado_inicial}")
            print(f">>> Punto Objetivo fijo:          {OBJETIVO}\n")
            imprimir_tabla_completa(resultados)
            mejor = mejor_solucion(resultados)
            if mejor:
                print(f"\n[MEJOR SOLUCION ENCONTRADA]: {mejor['algoritmo']} (Costo={mejor['costo']}, Tiempo={mejor['tiempo']:.6f}s)")
        elif opcion == "0":
            print("\n¡Programa finalizado con exito!")
            break
        else:
            print("Opcion no valida. Intenta de nuevo.")


if __name__ == "__main__":
    main()