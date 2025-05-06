"""
Script simplificado para iniciar o DataBridge localmente com simulação de serviços AWS
"""
import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

# Diretório raiz do projeto
ROOT_DIR = Path(__file__).parent

# Função para verificar se uma porta está em uso
def is_port_in_use(port):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

# Limpar a tela
os.system('cls' if os.name == 'nt' else 'clear')

# Banner colorido
print("\n\033[1;36m" + "="*80 + "\033[0m")
print("\033[1;36m" + " "*20 + "DATABRIDGE BANK - INICIALIZAÇÃO SIMPLIFICADA" + " "*20 + "\033[0m")
print("\033[1;36m" + " "*22 + "MODO DE SIMULAÇÃO DE SERVIÇOS AWS" + " "*22 + "\033[0m")
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
print("\033[1;33m>> Iniciando API DataBridge em modo simulação...\033[0m")

# Configurar variáveis de ambiente para modo MOCK
os.environ['DEBUG_MODE'] = 'true'  # Modo debug para facilitar a inicialização
os.environ['CONNECTION_TIMEOUT'] = '2'  # Timeout reduzido para conexões externas
os.environ['MONGODB_ENABLED'] = 'false'  # Desativar MongoDB real
os.environ['KAFKA_ENABLED'] = 'false'  # Desativar Kafka real

api_process = subprocess.Popen(
    [sys.executable, str(api_path)],
    cwd=str(ROOT_DIR / "databridge"),
    env=os.environ.copy()  # Passar variáveis de ambiente para o processo
)

# Aguardar API inicializar
print("⏳ Aguardando inicialização da API (verificando porta 8000)...")
api_ready = False
start_time = time.time()
timeout = 30  # segundos

# Verificar se a porta está sendo usada
while not api_ready and time.time() - start_time < timeout:
    if is_port_in_use(8000):
        api_ready = True
        print("✅ API respondendo na porta 8000")
        break
    
    # Verificar se o processo ainda está rodando
    if api_process.poll() is not None:
        print(f"❌ Processo da API encerrou com código {api_process.poll()}")
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

# Iniciar Frontend
print("\n\033[1;33m>> Iniciando Frontend DataBridge...\033[0m")
frontend_process = subprocess.Popen(
    [sys.executable, str(frontend_path)],
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
print("\n📡 Serviços simulados:")
print("- PostgreSQL: \033[1;32mSIMULADO\033[0m")
print("- MongoDB: \033[1;32mSIMULADO\033[0m")
print("- Kafka: \033[1;32mSIMULADO\033[0m")
print("\n⚠️ Pressione Ctrl+C para encerrar todos os serviços\n")

try:
    # Manter o script rodando até que o usuário interrompa com Ctrl+C
    while True:
        # Verificar se os processos ainda estão em execução
        if api_process.poll() is not None:
            print(f"Processo da API encerrou com código {api_process.poll()}")
            break
        
        if frontend_process.poll() is not None:
            print(f"Processo do Frontend encerrou com código {frontend_process.poll()}")
            break
        
        time.sleep(1)
except KeyboardInterrupt:
    print("\n\033[1;33m🛑 Encerrando todos os serviços...\033[0m")
    api_process.terminate()
    frontend_process.terminate()
    print("\033[1;32m✅ Sistema encerrado com sucesso!\033[0m")
    sys.exit(0)