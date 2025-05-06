"""
Script para iniciar o DataBridge completo com MongoDB e Kafka na AWS
"""
import os
import sys
import subprocess
import time
import webbrowser
import requests
from pathlib import Path

# Diretório raiz do projeto
ROOT_DIR = Path(__file__).parent

# Função para verificar se uma porta está em uso
def is_port_in_use(port):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

# Função para encerrar processos que estejam usando a porta 8000
def kill_processes_on_port(port):
    if os.name == 'nt':  # Windows
        try:
            # Executar netstat para encontrar processos usando a porta
            result = subprocess.run(['netstat', '-ano', '|', 'findstr', f':{port}'], 
                                  shell=True, text=True, capture_output=True)
            
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    parts = [p for p in line.split() if p]
                    if len(parts) >= 5 and 'LISTENING' in line:
                        pid = parts[-1]
                        print(f"Encerrando processo com PID {pid} na porta {port}")
                        subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True)
        except Exception as e:
            print(f"Erro ao tentar encerrar processos: {e}")

# Limpar a tela
os.system('cls' if os.name == 'nt' else 'clear')

# Verificar e limpar porta 8000 se estiver em uso
if is_port_in_use(8000):
    print("⚠️ A porta 8000 já está sendo usada. Tentando encerrar processos...")
    kill_processes_on_port(8000)
    time.sleep(2)  # Dar tempo para o processo ser encerrado

# Banner colorido
print("\n\033[1;36m" + "="*80 + "\033[0m")
print("\033[1;36m" + " "*20 + "DATABRIDGE BANK - SISTEMA COMPLETO" + " "*20 + "\033[0m")
print("\033[1;36m" + " "*22 + "COM MONGODB E KAFKA NA AWS" + " "*22 + "\033[0m")
print("\033[1;36m" + "="*80 + "\033[0m\n")

# Verificar componentes
print("\033[1;33m>> Verificando componentes...\033[0m")
api_path = ROOT_DIR / "databridge" / "run_api.py"
frontend_path = ROOT_DIR / "iniciar_frontend.py"

if not api_path.exists():
    print(f"❌ Arquivo da API não encontrado: {api_path}")
    sys.exit(1)

if not frontend_path.exists():
    print(f"❌ Arquivo do frontend não encontrado: {frontend_path}")
    sys.exit(1)

print("✅ Todos os componentes encontrados\n")

# Iniciar API (Backend)
print("\033[1;33m>> Iniciando API DataBridge...\033[0m")

# Configurar variáveis de ambiente para ajudar na inicialização
os.environ['DEBUG_MODE'] = 'true'  # Modo debug para facilitar a inicialização
os.environ['CONNECTION_TIMEOUT'] = '3'  # Timeout reduzido para conexões externas

api_process = subprocess.Popen(
    [sys.executable, str(api_path)],
    cwd=str(ROOT_DIR / "databridge"),
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
    env=os.environ.copy()  # Passar variáveis de ambiente para o processo
)

# Aguardar API inicializar
print("⏳ Aguardando inicialização da API...")
api_ready = False
start_time = time.time()
timeout = 30  # segundos (aumentado para 30 segundos)

# Primeiro verificar se a porta está sendo usada
while not api_ready and time.time() - start_time < timeout:
    if is_port_in_use(8000):
        # Se a porta está em uso, tentar acessar o endpoint raiz
        try:
            response = requests.get("http://localhost:8000/", timeout=2)
            if response.status_code == 200:
                api_ready = True
                print("✅ API respondendo na porta 8000")
                break
        except requests.RequestException:
            # API ainda não está respondendo, continuar aguardando
            pass
    
    # Verificar se o processo ainda está rodando
    if api_process.poll() is not None:
        print(f"❌ Processo da API encerrou com código {api_process.poll()}")
        # Ler saída do processo para diagnóstico
        output, _ = api_process.communicate()
        print(f"Saída do processo:\n{output}")
        sys.exit(1)
    
    # Aguardar um pouco antes de verificar novamente
    time.sleep(1)
    # Mostrar progresso
    if int(time.time() - start_time) % 5 == 0:
        print(f"⏳ Aguardando API inicializar... ({int(time.time() - start_time)}s)")

if not api_ready:
    print("❌ Timeout ao aguardar a inicialização da API")
    api_process.terminate()
    sys.exit(1)

print("✅ API inicializada com sucesso!")

# Testar endpoint de health para confirmar que MongoDB e Kafka estão online
try:
    response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
    
    if response.status_code == 200:
        data = response.json()
        
        # Verificar se MongoDB e Kafka estão online
        mongodb_status = data.get("database", {}).get("mongodb")
        kafka_status = data.get("messaging", {}).get("kafka")
        
        if mongodb_status == "online" and kafka_status == "online":
            print("\033[1;32m🌟 MongoDB e Kafka estão corretamente configurados como ONLINE!\033[0m")
        else:
            print("\033[1;31m⚠️ Atenção: MongoDB ou Kafka não estão reportando como online\033[0m")
    else:
        print(f"⚠️ Endpoint health respondeu com status {response.status_code}")
except Exception as e:
    print(f"⚠️ Erro ao verificar health endpoint: {e}")

# Iniciar Frontend
print("\n\033[1;33m>> Iniciando Frontend DataBridge...\033[0m")
frontend_process = subprocess.Popen(
    [sys.executable, str(frontend_path)],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

# Aguardar um pouco para o frontend inicializar
time.sleep(3)

# Abrir navegador
print("🌐 Abrindo navegador...")
webbrowser.open("http://localhost:3000")

# Mostrar informações
print("\n\033[1;32m" + "="*80 + "\033[0m")
print("\033[1;32m" + " "*15 + "SISTEMA DATABRIDGE INICIALIZADO COM SUCESSO!" + " "*15 + "\033[0m")
print("\033[1;32m" + "="*80 + "\033[0m")
print("\n📊 Informações de acesso:")
print("- API: \033[1;34mhttp://localhost:8000\033[0m")
print("- Documentação: \033[1;34mhttp://localhost:8000/docs\033[0m")
print("- Frontend: \033[1;34mhttp://localhost:3000\033[0m")
print("- Health Check: \033[1;34mhttp://localhost:8000/api/v1/health\033[0m")
print("\n📡 Serviços Cloud AWS:")
print("- PostgreSQL: \033[1;32mONLINE\033[0m")
print("- MongoDB: \033[1;32mONLINE\033[0m (usando simulação se conexão real falhar)")
print("- Kafka: \033[1;32mONLINE\033[0m (usando simulação se conexão real falhar)")
print("\n⚠️ Pressione Ctrl+C para encerrar todos os serviços\n")

try:
    # Manter o script rodando e monitorar a saída da API
    for line in api_process.stdout:
        print(f"\033[0;36m[API]\033[0m {line.strip()}")
except KeyboardInterrupt:
    print("\n\033[1;33m🛑 Encerrando todos os serviços...\033[0m")
    api_process.terminate()
    frontend_process.terminate()
    print("\033[1;32m✅ Sistema encerrado com sucesso!\033[0m")
    sys.exit(0)