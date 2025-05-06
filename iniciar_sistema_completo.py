"""
Script simplificado para iniciar o sistema DataBridge completo (API + Frontend)
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
print("\033[1;36m" + " "*20 + "DATABRIDGE BANK - SISTEMA COMPLETO SIMPLIFICADO" + " "*20 + "\033[0m")
print("\033[1;36m" + "="*80 + "\033[0m\n")

# Verificar componentes
print("\033[1;33m>> Verificando componentes...\033[0m")
api_path = ROOT_DIR / "databridge" / "run_api_simples.py"
frontend_path = ROOT_DIR / "iniciar_frontend.py"

if not api_path.exists():
    print(f"❌ Arquivo da API simplificada não encontrado: {api_path}")
    sys.exit(1)

if not frontend_path.exists():
    print(f"❌ Arquivo do frontend não encontrado: {frontend_path}")
    sys.exit(1)

print("✅ Todos os componentes encontrados\n")

# Verificar se as portas estão disponíveis
print("\033[1;33m>> Verificando portas...\033[0m")
ports_to_check = [8000, 3000]
for port in ports_to_check:
    if is_port_in_use(port):
        print(f"❌ Porta {port} já está em uso. Encerre o processo que está usando essa porta.")
        sys.exit(1)
    print(f"✅ Porta {port} está disponível")

# Iniciar API (Backend)
print("\n\033[1;33m>> Iniciando API DataBridge simplificada...\033[0m")

# Iniciar o processo da API
api_process = subprocess.Popen(
    [sys.executable, str(api_path)],
    cwd=str(ROOT_DIR / "databridge")
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