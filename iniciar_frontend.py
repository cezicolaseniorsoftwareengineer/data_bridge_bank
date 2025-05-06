"""
Script para iniciar o servidor frontend da aplicação DataBridge
"""
import os
import http.server
import socketserver
import webbrowser
from pathlib import Path

# Encontrar o diretório frontend
script_dir = Path(__file__).parent
frontend_dir = script_dir / "databridge" / "frontend"

# Porta para o servidor web
PORT = 3000

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Definir o diretório raiz para servir os arquivos
        super().__init__(*args, directory=str(frontend_dir), **kwargs)
    
    def end_headers(self):
        # Adicionar cabeçalhos CORS para permitir requisições da API
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

print(f"Iniciando servidor frontend DataBridge na porta {PORT}...")
print(f"Servindo arquivos do diretório: {frontend_dir}")

# Verificar se o diretório existe
if not frontend_dir.exists():
    print(f"ERRO: Diretório frontend não encontrado: {frontend_dir}")
    print("Verifique o caminho e tente novamente.")
    exit(1)

# Verificar se o index.html existe
index_path = frontend_dir / "index.html"
if not index_path.exists():
    print(f"ERRO: Arquivo index.html não encontrado em: {index_path}")
    print("Verifique o caminho e tente novamente.")
    exit(1)

# Iniciar servidor HTTP
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Server iniciado em http://localhost:{PORT}")
    print(f"Abra o navegador em: http://localhost:{PORT}")
    print("Para parar o servidor, pressione Ctrl+C")
    
    # Abrir o navegador automaticamente
    webbrowser.open(f"http://localhost:{PORT}")
    
    # Manter servidor rodando
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado. Obrigado por usar o DataBridge!")