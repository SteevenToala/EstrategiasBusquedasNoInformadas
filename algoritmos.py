import time
from collections import deque
from modelo import (
    OBJETIVO,
    ACCION_OPUESTA,
    generar_estado_inicial,
    funcion_sucesora,
    test_objetivo,
    Nodo
)

# ==============================================================================
# ALGORITMOS DE BÚSQUEDA NO INFORMADA
# ==============================================================================

def _empaquetar_resultado(nombre, estructura, comp_tiempo_t, comp_espacio_t,
                           nodo, nodos_generados, nodos_expandidos,
                           max_estructura, inicio_t, raiz=None):
    """Empaqueta métricas y caminos obtenidos tras la ejecución del algoritmo."""
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


def bfs(estado_inicial):
    """Búsqueda en Anchura (Breadth-First Search) - Usa Cola FIFO."""
    inicio_t = time.perf_counter()
    raiz = Nodo(estado_inicial)

    if test_objetivo(estado_inicial):
        return _empaquetar_resultado(
            "BFS", "Cola FIFO (deque)", "O(b^d)", "O(b^d)",
            raiz, 1, 0, 1, inicio_t, raiz
        )

    frontera = deque([raiz])          # COLA FIFO
    visitados = {estado_inicial}      # Control de estados visitados
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


def dfs(estado_inicial):
    """Búsqueda en Profundidad (Depth-First Search) - Usa Pila LIFO."""
    inicio_t = time.perf_counter()
    raiz = Nodo(estado_inicial)

    if test_objetivo(estado_inicial):
        return _empaquetar_resultado(
            "DFS", "Pila LIFO (list)", "O(b^m)", "O(b*m)",
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
                        "DFS", "Pila LIFO (list)", "O(b^m)", "O(b*m)",
                        hijo, nodos_generados, nodos_expandidos, max_pila, inicio_t, raiz
                    )
                pila.append(hijo)

    return _empaquetar_resultado(
        "DFS", "Pila LIFO (list)", "O(b^m)", "O(b*m)",
        None, nodos_generados, nodos_expandidos, max_pila, inicio_t, raiz
    )


def dfs_iterativa(estado_inicial):
    """Búsqueda en Profundidad Iterativa (IDDFS) - Pila con Límite Progresivo."""
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


def _expandir_un_paso_bidireccional(frontera_propia, visitados_propios, visitados_opuestos):
    """Paso unitario de expansión para búsqueda bidireccional."""
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
    """Búsqueda Bidireccional - 2 Colas FIFO simultáneas (Inicio <-> Meta)."""
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
            nodo_ini, nodo_obj, generados = _expandir_un_paso_bidireccional(
                frontera_ini, visitados_ini, visitados_obj)
        else:
            nodo_obj, nodo_ini, generados = _expandir_un_paso_bidireccional(
                frontera_obj, visitados_obj, visitados_ini)

        nodos_generados += generados
        nodos_expandidos += 1

        if nodo_ini is not None and nodo_obj is not None:
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


def mejor_solucion(resultados):
    """Determina la mejor solución encontrada según costo y tiempo."""
    encontradas = [r for r in resultados if r["encontrado"]]
    if not encontradas:
        return None
    return min(encontradas, key=lambda r: (r["costo"], r["tiempo"]))
