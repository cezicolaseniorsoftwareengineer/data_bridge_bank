"""
Script de reparo e inicialização para o DataBridge
Resolve problemas de PostgreSQL e incompatibilidade da API com Python 3.13
"""
import os
import sys
import subprocess
import time
import socket
import importlib
import shutil
from pathlib import Path
import platform
import ctypes

# Constantes e caminhos
WORKSPACE_DIR = Path(__file__).parent
DATABRIDGE_DIR = WORKSPACE_DIR / "databridge"
POSTGRESQL_SERVICE_NAME = "postgresql-x64-17"

def is_admin():
    """Verifica se o script está sendo executado como administrador"""
    try:
        if platform.system() == 'Windows':
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            # No Unix/Linux, verifica se é root (uid 0)
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

def verificar_postgresql():
    """Verifica o PostgreSQL e tenta corrigir problemas de inicialização"""
    print("\n🔍 Diagnosticando problemas com o PostgreSQL...")
    
    # Verificar status do serviço
    stdout, stderr, code = run_command(f"sc query {POSTGRESQL_SERVICE_NAME}")
    if "RUNNING" in stdout:
        print(f"✅ Serviço PostgreSQL está rodando!")
        return True
    
    # Verificar pasta de instalação do PostgreSQL
    print("➤ Procurando instalação do PostgreSQL...")
    pg_dirs = []
    
    # Procurar em locais comuns
    for drive in ['C:', 'D:']:
        paths = [
            f"{drive}\\Program Files\\PostgreSQL",
            f"{drive}\\PostgreSQL",
            f"{drive}\\Program Files (x86)\\PostgreSQL"
        ]
        for path in paths:
            if os.path.exists(path):
                for item in os.listdir(path):
                    if os.path.isdir(os.path.join(path, item)) and item.replace('.', '').isdigit():
                        pg_dirs.append(os.path.join(path, item))
    
    if not pg_dirs:
        print("❌ Não foi possível encontrar a instalação do PostgreSQL")
        print("➤ Configurando a API para funcionar sem PostgreSQL...")
        return False
    
    pg_dir = pg_dirs[0]  # Usar a primeira instalação encontrada
    print(f"✅ Instalação do PostgreSQL encontrada em: {pg_dir}")
    
    # Verificar logs do PostgreSQL para entender o problema
    print("\n➤ Verificando logs do PostgreSQL...")
    data_dir = os.path.join(pg_dir, "data")
    log_dir = os.path.join(data_dir, "log")
    
    if os.path.exists(log_dir):
        log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
        if log_files:
            # Pegar o log mais recente
            latest_log = max(log_files, key=lambda x: os.path.getmtime(os.path.join(log_dir, x)))
            log_path = os.path.join(log_dir, latest_log)
            
            try:
                with open(log_path, 'r', errors='ignore') as f:
                    last_lines = f.readlines()[-20:]  # Últimas 20 linhas
                    print(f"📃 Últimas linhas do log ({latest_log}):")
                    for line in last_lines:
                        if "FATAL" in line or "ERROR" in line:
                            print(f"❗ {line.strip()}")
                        else:
                            print(f"   {line.strip()}")
            except Exception as e:
                print(f"❌ Erro ao ler log: {e}")
    
    # Tentar corrigir problemas comuns do PostgreSQL
    print("\n➤ Tentando corrigir problemas comuns do PostgreSQL...")
    
    # 1. Verificar se diretório de dados existe e tem permissões
    if os.path.exists(data_dir):
        print(f"✓ Diretório de dados encontrado: {data_dir}")
        
        # Verificar permissões (apenas se for admin)
        if is_admin():
            print("✓ Executando como administrador, ajustando permissões...")
            try:
                # No Windows, ajustar permissões usando icacls
                stdout, stderr, code = run_command(f'icacls "{data_dir}" /grant:r "NT AUTHORITY\\NetworkService":(OI)(CI)F')
                if code == 0:
                    print("✓ Permissões ajustadas com sucesso")
                else:
                    print(f"⚠️ Não foi possível ajustar permissões: {stderr}")
            except Exception as e:
                print(f"⚠️ Erro ao ajustar permissões: {e}")
        else:
            print("⚠️ Execute este script como administrador para corrigir permissões")
    else:
        print(f"❌ Diretório de dados não encontrado em: {data_dir}")
        return False
    
    # 2. Verificar arquivos de lock
    print("\n➤ Verificando arquivos de lock...")
    lock_files = [
        os.path.join(data_dir, "postmaster.pid"),
        os.path.join(data_dir, ".s.PGSQL.5432.lock")
    ]
    
    for lock_file in lock_files:
        if os.path.exists(lock_file):
            print(f"⚠️ Encontrado arquivo de lock: {lock_file}")
            try:
                if is_admin():
                    os.remove(lock_file)
                    print(f"✓ Arquivo de lock removido: {lock_file}")
                else:
                    print("⚠️ Execute como administrador para remover arquivos de lock")
            except Exception as e:
                print(f"❌ Erro ao remover arquivo de lock: {e}")
    
    # 3. Iniciar o serviço novamente
    print("\n➤ Tentando iniciar o serviço PostgreSQL...")
    if is_admin():
        stdout, stderr, code = run_command(f"sc start {POSTGRESQL_SERVICE_NAME}")
        
        # Aguardar para ver se o serviço inicia
        time.sleep(5)
        
        stdout, stderr, code = run_command(f"sc query {POSTGRESQL_SERVICE_NAME}")
        if "RUNNING" in stdout:
            print("✅ Serviço PostgreSQL iniciado com sucesso!")
            return True
        else:
            print("❌ Não foi possível iniciar o serviço PostgreSQL")
            print(f"   Detalhes: {stdout}")
            
            # Se tudo falhar, configuramos para usar memória
            print("➤ Configurando a API para funcionar sem PostgreSQL...")
            return False
    else:
        print("⚠️ Execute este script como administrador para iniciar o serviço")
        return False

def corrigir_problema_strawberry():
    """Corrige a incompatibilidade entre Python 3.13 e Strawberry GraphQL"""
    print("\n🔧 Corrigindo problema de compatibilidade com Python 3.13...")
    
    # Verificar versão do Python
    python_version = platform.python_version()
    print(f"➤ Versão do Python: {python_version}")
    
    if python_version.startswith("3.13"):
        print("➤ Detectada versão Python 3.13, incompatível com Strawberry GraphQL 0.205.0")
        
        # Modificar o arquivo app/main.py para desativar GraphQL
        main_py = DATABRIDGE_DIR / "app" / "main.py"
        
        if main_py.exists():
            # Fazer backup do arquivo original
            backup_file = DATABRIDGE_DIR / "app" / "main.py.bak"
            if not backup_file.exists():
                shutil.copy(main_py, backup_file)
                print(f"✓ Backup criado: {backup_file}")
            
            # Ler o conteúdo original
            with open(main_py, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Modificar o arquivo para evitar a importação do Strawberry
            modified_content = """# API DataBridge - Versão simplificada
# Compatível com Python 3.13 (sem GraphQL)

import os
import logging
import time
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter

# Comentado para evitar erro de compatibilidade com Python 3.13
# import strawberry
# from strawberry.fastapi import GraphQLRouter
# from app.api.graphql.schema import schema as graphql_schema

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("databridge")

# Rotas REST
from app.api.rest.router import api_router

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

# Middleware para logging de requisições
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s")
    return response

# Rotas da API REST
app.include_router(api_router, prefix="/api/v1")

# GraphQL endpoint desativado para compatibilidade com Python 3.13
# graphql_app = GraphQLRouter(graphql_schema)
# app.include_router(graphql_app, prefix="/api/v1/graphql")

# Healthcheck endpoint
@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "online",
        "version": VERSION,
        "mode": "memory",
        "database": os.environ.get("DATABRIDGE_DB_MODE", "memory"),
        "message": "API running in compatibility mode (Python 3.13)"
    }

# Root endpoint com redirecionamento para a documentação
@app.get("/")
async def root():
    return {"message": "DataBridge API", "docs": "/api/v1/docs"}
"""
            
            # Salvar as mudanças
            with open(main_py, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            print("✅ Arquivo main.py modificado para funcionar com Python 3.13")
        else:
            print(f"❌ Arquivo main.py não encontrado em: {main_py}")
    else:
        print(f"✓ Versão do Python ({python_version}) não precisa de ajustes")

def configurar_modo_memoria():
    """Configura a API para usar armazenamento em memória"""
    print("\n🔧 Configurando API para modo de memória...")
    
    # Definir variáveis de ambiente
    os.environ["DATABRIDGE_DB_MODE"] = "memory"
    os.environ["DATABRIDGE_TESTING"] = "true"
    
    # Verificar e criar diretórios necessários
    uploads_dir = DATABRIDGE_DIR / "uploads"
    logs_dir = DATABRIDGE_DIR / "logs"
    
    uploads_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    print("✓ Diretórios de uploads e logs verificados")
    print("✓ Variáveis de ambiente configuradas para modo de memória")
    
    return True

def iniciar_api_simplificada():
    """Inicia a API com configurações simplificadas"""
    print("\n🚀 Iniciando API DataBridge em modo simplificado...")
    
    # Mudar para o diretório da API
    os.chdir(DATABRIDGE_DIR)
    
    # Configurar PYTHONPATH
    os.environ["PYTHONPATH"] = str(DATABRIDGE_DIR)
    
    # Informações de acesso
    print("\n📊 Informações de acesso:")
    print("- API: http://127.0.0.1:8000")
    print("- Documentação: http://127.0.0.1:8000/api/v1/docs")
    print("- Health Check: http://127.0.0.1:8000/api/v1/health")
    print("- Frontend: Abra no navegador: file://" + str(DATABRIDGE_DIR / "frontend" / "index.html"))
    
    print("\n⏳ Iniciando servidor API em modo simplificado...")
    print("-" * 60)
    
    # Iniciar uvicorn com configurações simplificadas
    try:
        # Abrir navegador com a documentação (em outra thread)
        import threading
        import webbrowser
        
        def open_browser():
            time.sleep(3)  # Dar tempo para a API iniciar
            webbrowser.open("http://127.0.0.1:8000/api/v1/docs")
        
        threading.Thread(target=open_browser, daemon=True).start()
        
        # Iniciar o servidor
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 API encerrada pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro ao iniciar a API: {e}")
        
        # Método alternativo
        print("\n➤ Tentando método alternativo...")
        os.system(f'"{sys.executable}" -m uvicorn app.main:app --host 0.0.0.0 --port 8000')

def main():
    """Função principal que executa todo o fluxo de correção e inicialização"""
    print("\n" + "="*70)
    print(" "*15 + "DATABRIDGE - SOLUÇÃO DE PROBLEMAS" + " "*15)
    print("="*70)
    
    # 1. Verificar se é administrador
    if not is_admin():
        print("\n⚠️ AVISO: Este script deve ser executado como administrador")
        print("   Algumas correções podem não funcionar corretamente.")
        
        # Perguntar se deseja continuar
        resposta = input("\nDeseja continuar mesmo assim? (S/N): ")
        if resposta.lower() != 's':
            print("Encerrando script. Execute novamente como administrador.")
            return
    
    # 2. Corrigir problema do Strawberry GraphQL
    corrigir_problema_strawberry()
    
    # 3. Verificar e corrigir PostgreSQL
    postgres_ok = verificar_postgresql()
    
    # 4. Configurar modo adequado (PostgreSQL ou Memória)
    if not postgres_ok:
        configurar_modo_memoria()
    
    # 5. Iniciar a API
    iniciar_api_simplificada()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Processo interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante a execução: {e}")