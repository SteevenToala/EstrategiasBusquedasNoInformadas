# ==============================================================================
# SISTEMA DE BÚSQUEDAS NO INFORMADAS - CONTROLADOR PRINCIPAL
# ==============================================================================

from modelo import ANCHO, LARGO, OBJETIVO
from algoritmos import ejecutar_comparacion, mejor_solucion
from visualizador import (
    imprimir_cuadricula,
    imprimir_arbol,
    imprimir_solo_camino_arbol,
    imprimir_tabla_completa,
    mostrar_todas_las_soluciones
)


def menu_visualizar_arbol(resultados):
    """Submenú interactivo para inspeccionar los árboles de búsqueda."""
    nombres_opcion = {
        "1": "BFS",
        "2": "DFS",
        "3": "DFS iterativa",
        "4": "Bidireccional",
    }
    
    while True:
        print("\n--- Visualizacion de Arboles de Busqueda ---")
        print("  1 - BFS")
        print("  2 - DFS")
        print("  3 - DFS iterativa")
        print("  4 - Bidireccional")
        print("  0 - Volver al menu principal")
        opcion = input("Elige el algoritmo a inspeccionar: ").strip()

        if opcion == "0":
            break

        if opcion not in nombres_opcion:
            print("Opcion invalida.")
            continue

        nombre_elegido = nombres_opcion[opcion]
        resultado_elegido = next((r for r in resultados if r["algoritmo"] == nombre_elegido), None)

        if resultado_elegido is None or resultado_elegido["raiz"] is None:
            print(f"No hay arbol disponible para {nombre_elegido}.")
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
    """Submenú interactivo para ver los mapas de rutas en la cuadrícula."""
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
    """Flujo principal del programa."""
    print("=" * 60)
    print(" SISTEMA DE BUSQUEDAS NO INFORMADAS - AULA DE CLASES")
    print("=" * 60)
    print(f"Dimensiones del Aula: {LARGO} filas x {ANCHO} columnas")
    print(f"Punto Objetivo (Fijo): {OBJETIVO}")
    
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