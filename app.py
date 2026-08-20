# ==============================================================================
# SISTEMA DE BÚSQUEDAS NO INFORMADAS - LANZADOR PRINCIPAL
# ==============================================================================

import sys
from gui import main as lanzar_gui
from consola import main as lanzar_consola

def main():
    """Lanza la aplicación de escritorio nativa por defecto, o la consola si se pasa --cli."""
    if len(sys.argv) > 1 and sys.argv[1] in ("--cli", "-c", "--consola"):
        lanzar_consola()
    else:
        lanzar_gui()

if __name__ == "__main__":
    main()