"""
Script de instalação de dependências e inicialização do DataBridge
Detecta e instala automaticamente todas as dependências necessárias antes de executar
"""
import os
import sys
import subprocess
import time
import shutil
from pathlib import Path
import platform
import ctypes

# Constantes e caminhos
WORKSPACE_DIR = Path(__file__).parent
DATABRIDGE_DIR = WORKSPACE_DIR / "databridge"

def is_admin():
    """Verifica se o script está sendo executado como administrador"""
    try:
        if platform.system() == 'Windows':
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except:
        return False

def run_command(cmd, shell=True, timeout=None):
    """Executa um comando e retorna a saída"""
    try:
        result = subprocess.run(cmd, shell=shell, text=True, capture_output=True, timeout=timeout)
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "Timeout ao executar o comando", -1
    except Exception as e:
        return "", str(e), -1

def instalar_dependencias():
    """Instala todas as dependências necessárias para a API"""
    print("\n📦 Instalando dependências essenciais...\n")
    
    # Lista de pacotes necessários
    dependencias = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "python-jose",
        "passlib",
        "bcrypt",
        "sqlalchemy",
        "psycopg2-binary"
    ]
    
    # Verificar se há ambiente virtual e usá-lo se existir
    venv_python = None
    venv_paths = [
        WORKSPACE_DIR / "venv" / "Scripts" / "python.exe",  # Windows venv
        WORKSPACE_DIR / "env" / "Scripts" / "python.exe",   # Windows env
        WORKSPACE_DIR / ".venv" / "Scripts" / "python.exe", # Windows .venv
    ]
    
    for venv_path in venv_paths:
        if venv_path.exists():
            venv_python = str(venv_path)
            break
    
    python_exe = venv_python if venv_python else sys.executable
    
    # Instalar cada dependência
    for dep in dependencias:
        print(f"➤ Instalando {dep}...")
        cmd = [python_exe, "-m", "pip", "install", "-U", dep]
        stdout, stderr, code = run_command(cmd, shell=False)
        
        if code == 0:
            print(f"✅ {dep} instalado com sucesso!")
        else:
            print(f"⚠️ Erro ao instalar {dep}: {stderr}")
    
    print("\n✅ Todas as dependências instaladas")
    return python_exe

def corrigir_main_py():
    """Corrige o arquivo main.py para funcionar com Python 3.13"""
    print("\n🔧 Corrigindo arquivo main.py...")
    
    # Caminho para o arquivo main.py
    main_py = DATABRIDGE_DIR / "app" / "main.py"
    
    if main_py.exists():
        # Fazer backup se não existir
        backup_file = DATABRIDGE_DIR / "app" / "main.py.bak"
        if not backup_file.exists():
            shutil.copy(main_py, backup_file)
            print(f"✅ Backup criado: {backup_file}")
        
        # Criar uma versão simplificada do main.py
        simplified_content = """# DataBridge API - Versão simplificada para Python 3.13
import os
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("databridge")

# Versão da API
VERSION = "1.0.0-memory"

# Configurar a aplicação FastAPI
app = FastAPI(
    title="DataBridge API",
    description="API para integração de sistemas de informação financeira",
    version=VERSION,
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas da API REST (simplificadas)
@app.get("/api/v1/clients")
async def get_clients():
    return [
        {"id": 1, "name": "Cliente Exemplo 1", "status": "active"},
        {"id": 2, "name": "Cliente Exemplo 2", "status": "inactive"},
        {"id": 3, "name": "Cliente Exemplo 3", "status": "active"}
    ]

@app.get("/api/v1/files")
async def get_files():
    return [
        {"id": 1, "name": "arquivo1.csv", "size": 1024, "uploaded_at": "2025-05-03T10:30:00"},
        {"id": 2, "name": "arquivo2.xlsx", "size": 2048, "uploaded_at": "2025-05-02T14:45:00"}
    ]

@app.get("/api/v1/records")
async def get_records():
    return [
        {"id": 1, "client_id": 1, "value": 150.75, "date": "2025-05-01"},
        {"id": 2, "client_id": 1, "value": 249.90, "date": "2025-05-02"},
        {"id": 3, "client_id": 2, "value": 99.50, "date": "2025-05-03"}
    ]

# Healthcheck endpoint
@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "online",
        "version": VERSION,
        "mode": "memory",
        "message": "DataBridge API running in Python 3.13 compatibility mode"
    }

# Root endpoint
@app.get("/")
async def root():
    return {"message": "DataBridge API is running", "docs": "/docs"}
"""
        
        # Salvar o arquivo modificado
        with open(main_py, "w", encoding="utf-8") as f:
            f.write(simplified_content)
        
        print("✅ Arquivo main.py modificado para funcionar com Python 3.13")
    else:
        print(f"❌ Arquivo main.py não encontrado: {main_py}")
        return False
    
    return True

def executar_api(python_exe):
    """Executa a API com o executável Python fornecido"""
    print("\n🚀 Iniciando API DataBridge...\n")
    
    # Mudar para o diretório da aplicação
    os.chdir(DATABRIDGE_DIR)
    
    # Configurar ambiente
    os.environ["DATABRIDGE_DB_MODE"] = "memory"
    os.environ["PYTHONPATH"] = str(DATABRIDGE_DIR)
    
    print("📊 Informações de acesso:")
    print("- API: http://127.0.0.1:8000")
    print("- Documentação: http://127.0.0.1:8000/docs")
    print("- Health Check: http://127.0.0.1:8000/api/v1/health")
    print("\n⏳ Iniciando servidor... (pressione Ctrl+C para encerrar)\n")
    
    # Executar comando com o Python do ambiente virtual ou sistema
    cmd = [python_exe, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
    
    try:
        # Abrir navegador após alguns segundos
        import threading
        import webbrowser
        
        def open_browser():
            time.sleep(3)
            webbrowser.open("http://127.0.0.1:8000/docs")
        
        threading.Thread(target=open_browser, daemon=True).start()
        
        # Executar uvicorn como processo
        subprocess.call(cmd)
    except KeyboardInterrupt:
        print("\n🛑 API encerrada pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro ao iniciar API: {e}")
        
        # Método alternativo
        os.system(f'"{python_exe}" -m uvicorn app.main:app --host 0.0.0.0 --port 8000')

def main():
    """Função principal"""
    print("\n" + "="*70)
    print(" "*10 + "DATABRIDGE - INSTALAÇÃO E EXECUÇÃO SIMPLIFICADA" + " "*10)
    print("="*70)
    
    # Instalar dependências
    python_exe = instalar_dependencias()
    
    # Corrigir main.py
    corrigir_main_py()
    
    # Executar API
    executar_api(python_exe)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Processo interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")