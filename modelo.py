import random

# ==============================================================================
# MODELO DEL ENTORNO Y ESTRUCTURA DE NODOS
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


class Nodo:
    """Representa un nodo dentro del árbol de búsqueda."""
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
