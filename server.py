import os
import json
import webbrowser
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

from modelo import ANCHO, LARGO, OBJETIVO, generar_estado_inicial
from algoritmos import ejecutar_comparacion, mejor_solucion

# Directorio de archivos estáticos
WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")


class SearchAPIHandler(BaseHTTPRequestHandler):
    """Manejador HTTP para servir la interfaz web y responder a la API REST."""

    def log_message(self, format, *args):
        # Silenciar logs innecesarios de peticiones para una consola limpia
        pass

    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200, "text/plain")

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # Endpoint API: Obtener estado inicial aleatorio
        if path == "/api/random":
            inicio = generar_estado_inicial()
            self._set_headers(200, "application/json")
            self.wfile.write(json.dumps({"inicio": list(inicio), "objetivo": list(OBJETIVO)}).encode("utf-8"))
            return

        # Servir archivos estáticos del frontend
        if path == "/" or path == "":
            file_path = os.path.join(WEB_DIR, "index.html")
            content_type = "text/html; charset=utf-8"
        elif path == "/style.css":
            file_path = os.path.join(WEB_DIR, "style.css")
            content_type = "text/css; charset=utf-8"
        elif path == "/app.js":
            file_path = os.path.join(WEB_DIR, "app.js")
            content_type = "application/javascript; charset=utf-8"
        else:
            safe_path = os.path.normpath(os.path.join(WEB_DIR, path.lstrip("/")))
            if safe_path.startswith(WEB_DIR) and os.path.isfile(safe_path):
                file_path = safe_path
                content_type = "text/plain"
            else:
                self._set_headers(404, "text/plain")
                self.wfile.write(b"404 No Encontrado")
                return

        if os.path.exists(file_path):
            self._set_headers(200, content_type)
            with open(file_path, "rb") as f:
                self.wfile.write(f.read())
        else:
            self._set_headers(404, "text/plain")
            self.wfile.write(b"404 No Encontrado")

    def do_POST(self):
        parsed = urlparse(self.path)
        
        # Endpoint API: Ejecutar algoritmos de búsqueda
        if parsed.path == "/api/run":
            content_len = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_len).decode("utf-8")
            
            try:
                data = json.loads(body)
                inicio = tuple(data.get("inicio", [3, 0]))
                objetivo = tuple(data.get("objetivo", OBJETIVO))
            except Exception:
                inicio = (3, 0)
                objetivo = OBJETIVO

            # Ejecutar comparativa con los 4 algoritmos (Tree Search puro)
            ini_res, resultados = ejecutar_comparacion(estado_inicial=inicio, objetivo=objetivo)
            mejor = mejor_solucion(resultados)

            # Limpiar clave 'raiz' con objetos Nodo para permitir serialización JSON limpia
            resultados_json = []
            for r in resultados:
                r_clean = dict(r)
                r_clean.pop("raiz", None)
                resultados_json.append(r_clean)

            mejor_json = dict(mejor) if mejor else None
            if mejor_json:
                mejor_json.pop("raiz", None)

            response_payload = {
                "inicio": list(ini_res),
                "objetivo": list(objetivo),
                "resultados": resultados_json,
                "mejor": mejor_json
            }

            self._set_headers(200, "application/json; charset=utf-8")
            self.wfile.write(json.dumps(response_payload, ensure_ascii=False).encode("utf-8"))
            return

        self._set_headers(404, "text/plain")
        self.wfile.write(b"404 Endpoint no encontrado")


def find_free_port(start_port=5000):
    """Encuentra un puerto disponible para levantar el servidor."""
    port = start_port
    while port < 6000:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
            port += 1
    return 8000


def start_server(port=None, auto_open=True):
    """Inicia el servidor local y abre la interfaz visual en el navegador."""
    if port is None:
        port = find_free_port(5000)

    server_address = ("127.0.0.1", port)
    httpd = HTTPServer(server_address, SearchAPIHandler)
    url = f"http://127.0.0.1:{port}"

    print("=" * 70)
    print(" 🚀 INTERFAZ GRÁFICA INTERACTIVA - BÚSQUEDAS NO INFORMADAS (IA)")
    print("=" * 70)
    print(f" Servidor iniciado con éxito en: {url}")
    print(" Presiona Ctrl + C en esta consola para detener el servidor.")
    print("=" * 70)

    if auto_open:
        webbrowser.open(url)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n Servidor detenido.")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    start_server()
