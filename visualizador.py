from modelo import ANCHO, LARGO, OBJETIVO

# ==============================================================================
# COMPONENTE DE VISUALIZACIÓN Y FORMATEO DE RESULTADOS
# ==============================================================================

def imprimir_cuadricula(estado_inicial, camino=None):
    """Genera y retorna la representación visual del aula en texto."""
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
    - Resalta con [*] [EN CAMINO SOLUCION] los nodos que forman parte de la respuesta.
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
            print(prefijo + "└── ... [Limite de visualizacion alcanzado]")
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
    """Imprime exclusivamente la rama del árbol que conduce a la meta."""
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


def imprimir_tabla_completa(resultados):
    """Imprime las tablas comparativas teóricas y empíricas."""
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
    """Muestra la lista de acciones y coordenadas encontradas por cada algoritmo."""
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
