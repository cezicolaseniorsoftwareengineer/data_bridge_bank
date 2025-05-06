import http.server
import socketserver
import os

# Definir a porta - vamos usar 8001 para evitar conflito com a porta 8000
PORT = 8001

# Imprimir instrução clara
print(f"\n{'='*60}")
print(f"SERVIDOR DE TESTE RODANDO NA PORTA {PORT}")
print(f"Abra seu navegador e acesse: http://localhost:{PORT}")
print(f"{'='*60}\n")

# Iniciar o servidor simples
with socketserver.TCPServer(("", PORT), http.server.SimpleHTTPRequestHandler) as httpd:
    print(f"Servidor rodando na porta {PORT}...")
    print("Pressione Ctrl+C para encerrar")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado pelo usuário.")
        httpd.server_close()