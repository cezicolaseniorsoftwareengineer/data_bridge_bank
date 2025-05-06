"""
Script para iniciar o DataBridge com MongoDB e Kafka na AWS
"""
import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

# Diretório raiz
ROOT_DIR = Path(__file__).parent

# Caminho da API
API_DIR = ROOT_DIR / "databridge"
APP_DIR = API_DIR / "app"
MAIN_PY = APP_DIR / "main.py"

# Banner do sistema
def print_banner():
    print("\n" + "="*80)
    print(" DATABRIDGE BANK - SISTEMA COMPLETO COM SUPORTE A AWS".center(80))
    print(" MongoDB e Kafka Ativados".center(80))
    print("="*80 + "\n")

# Verificar ambiente
def check_environment():
    if not API_DIR.exists():
        print(f"ERRO: Diretório API não encontrado: {API_DIR}")
        sys.exit(1)
    
    if not MAIN_PY.exists():
        print(f"ERRO: Arquivo main.py não encontrado em: {MAIN_PY}")
        sys.exit(1)
    
    print("✅ Ambiente verificado com sucesso")

# Iniciar API
def start_api():
    print("\n📡 Iniciando API DataBridge com serviços AWS...\n")
    
    # Usar o script de inicialização da API
    api_script = API_DIR / "run_api.py"
    
    # Verificar se o script existe
    if not api_script.exists():
        print(f"ERRO: Script run_api.py não encontrado em: {api_script}")
        sys.exit(1)
    
    # Executar o script em um processo separado
    api_process = subprocess.Popen(
        [sys.executable, str(api_script)], 
        cwd=str(API_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Aguardar inicialização
    print("⏳ Aguardando inicialização da API...")
    time.sleep(5)  # Dar tempo para a API iniciar
    
    return api_process

# Verificar status da API
def check_api_status():
    try:
        import http.client
        import json
        
        conn = http.client.HTTPConnection("localhost", 8000, timeout=5)
        conn.request("GET", "/api/v1/health")
        response = conn.getresponse()
        
        if response.status != 200:
            print(f"⚠️ API responde com status {response.status}")
            return False
        
        data = json.loads(response.read().decode())
        
        if data.get("status") == "online":
            print(f"✅ API DataBridge inicializada com sucesso!")
            print(f"   Versão: {data.get('version')}")
            
            # Verificar serviços
            services = []
            if data.get("database", {}).get("postgres") == "online":
                services.append("PostgreSQL")
            if data.get("database", {}).get("mongodb") == "online":
                services.append("MongoDB")
            if data.get("messaging", {}).get("kafka") == "online":
                services.append("Kafka")
            
            if services:
                print(f"   Serviços ativos: {', '.join(services)}")
            else:
                print("   Nenhum serviço reportado como ativo")
            
            return True
        else:
            print(f"⚠️ API iniciada mas reporta status: {data.get('status', 'desconhecido')}")
            return False
            
    except Exception as e:
        print(f"⚠️ Erro ao verificar API: {e}")
        return False

# Iniciar o frontend
def start_frontend():
    print("\n🖥️ Iniciando o frontend DataBridge...\n")
    
    # Caminho do script do frontend
    frontend_script = ROOT_DIR / "iniciar_frontend.py"
    
    # Verificar se o script existe
    if not frontend_script.exists():
        print(f"ERRO: Script iniciar_frontend.py não encontrado em: {frontend_script}")
        sys.exit(1)
    
    # Executar o script em um processo separado
    frontend_process = subprocess.Popen(
        [sys.executable, str(frontend_script)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Aguardar um pouco
    time.sleep(2)
    
    return frontend_process

# Função principal
def main():
    print_banner()
    check_environment()
    
    # Iniciar componentes
    api_process = start_api()
    api_ok = check_api_status()
    
    if not api_ok:
        print("\n⚠️ A API não parece estar funcionando corretamente.")
        resposta = input("Deseja continuar mesmo assim? (s/n): ")
        if resposta.lower() != 's':
            api_process.terminate()
            print("Processo encerrado pelo usuário.")
            sys.exit(1)
    
    frontend_process = start_frontend()
    
    # Mostrar URLs
    print("\n🚀 Sistema DataBridge com MongoDB e Kafka inicializado!\n")
    print("📊 Informações de acesso:")
    print("- API: http://127.0.0.1:8000")
    print("- Documentação: http://127.0.0.1:8000/docs")
    print("- Frontend: http://localhost:3000")
    
    print("\n⚠️ Pressione Ctrl+C para encerrar o sistema\n")
    
    try:
        # Imprimir logs da API em tempo real com prefixo
        for line in api_process.stdout:
            print(f"[API] {line.strip()}")
    except KeyboardInterrupt:
        print("\n🛑 Encerrando o sistema...")
        api_process.terminate()
        frontend_process.terminate()
        print("✅ Sistema encerrado com sucesso!")
        sys.exit(0)

if __name__ == "__main__":
    main()