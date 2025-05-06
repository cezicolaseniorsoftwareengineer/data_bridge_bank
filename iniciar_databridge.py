"""
Script para iniciar a API DataBridge em modo simplificado
Resolve problemas de conexão e dependências automaticamente
"""
import os
import sys
import subprocess
import time
import importlib
from pathlib import Path

DATABRIDGE_DIR = Path(__file__).parent / "databridge"
os.chdir(DATABRIDGE_DIR)

def instalar_dependencias_basicas():
    """Instala as dependências essenciais para o funcionamento da API"""
    print("🔍 Verificando e instalando dependências básicas...")
    
    dependencias = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "python-jose",
        "PyJWT",
        "bcrypt",
        "strawberry-graphql==0.205.0",  # Versão específica para evitar conflitos
        "passlib"
    ]
    
    for dep in dependencias:
        try:
            if "==" in dep:
                modulo = dep.split("==")[0]
            else:
                modulo = dep
            importlib.import_module(modulo)
            print(f"✓ {modulo} já instalado")
        except ImportError:
            print(f"➤ Instalando {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])

def configurar_modo_memoria():
    """Configura a API para usar armazenamento em memória para testes"""
    print("\n🔧 Configurando API para modo de memória (sem necessidade de banco de dados)...")
    
    # Verificar e criar diretório de uploads
    uploads_dir = DATABRIDGE_DIR / "uploads"
    if not uploads_dir.exists():
        uploads_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ Diretório de uploads criado: {uploads_dir}")
    else:
        print(f"✓ Diretório de uploads já existe: {uploads_dir}")
    
    # Verificar e criar diretório de logs
    logs_dir = DATABRIDGE_DIR / "logs"
    if not logs_dir.exists():
        logs_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ Diretório de logs criado: {logs_dir}")
    else:
        print(f"✓ Diretório de logs já existe: {logs_dir}")
    
    # Definir variáveis de ambiente para modo de memória
    os.environ["DATABRIDGE_DB_MODE"] = "memory"
    os.environ["DATABRIDGE_TESTING"] = "true"
    print("✓ Variáveis de ambiente configuradas para modo de memória")

def iniciar_api():
    """Inicia a API DataBridge"""
    print("\n🚀 Iniciando API DataBridge...")
    print("URL da API: http://127.0.0.1:8000")
    print("Documentação: http://127.0.0.1:8000/api/v1/docs")
    print("Health Check: http://127.0.0.1:8000/api/v1/health")
    print("\nPressione Ctrl+C para encerrar\n")
    
    # Usar try-except para capturar erros e fornecer mensagens úteis
    try:
        # Iniciar uvicorn diretamente com parâmetros ajustados
        subprocess.check_call([
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
            "--log-level", "info"
        ])
    except KeyboardInterrupt:
        print("\n🛑 API encerrada pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro ao iniciar a API: {str(e)}")
        print("\nTentando método alternativo...")
        
        try:
            # Método alternativo de execução
            os.environ["PYTHONPATH"] = str(DATABRIDGE_DIR)
            python_exe = sys.executable
            os.system(f'"{python_exe}" -m uvicorn app.main:app --host 0.0.0.0 --port 8080')
            print("\n🚀 API iniciada na porta alternativa 8080")
        except Exception as e2:
            print(f"\n❌ Erro ao iniciar a API (segundo método): {str(e2)}")
            print("\nVerificando possíveis soluções:")
            
            # Verificar se a porta está em uso
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('127.0.0.1', 8000))
                if result == 0:
                    print("⚠️ A porta 8000 já está em uso. Tente fechar outros aplicativos que possam estar usando esta porta.")
                sock.close()
            except:
                pass
            
            print("\nSugestões de solução:")
            print("1. Verifique se não há outra instância da API rodando")
            print("2. Reinicie seu computador para liberar recursos")
            print("3. Tente executar a API com uma porta diferente:")
            print("   python run_api_port_8080.py")

def atualizar_frontend_config():
    """Atualiza o arquivo de configuração do frontend para apontar para a API"""
    frontend_config = DATABRIDGE_DIR / "frontend" / "api-config.js"
    
    if frontend_config.exists():
        print("\n📝 Atualizando configuração do frontend...")
        try:
            # Ler o conteúdo atual
            with open(frontend_config, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Garantir que a API está configurada corretamente
            if "baseUrl: 'http://127.0.0.1:8000/api/v1'" not in content:
                content = content.replace(
                    "baseUrl: 'http://127.0.0.1:8080/api/v1'", 
                    "baseUrl: 'http://127.0.0.1:8000/api/v1'"
                )
                
                # Salvar as alterações
                with open(frontend_config, "w", encoding="utf-8") as f:
                    f.write(content)
                
                print("✓ Configuração do frontend atualizada para usar a porta 8000")
            else:
                print("✓ Configuração do frontend já está correta")
        except Exception as e:
            print(f"⚠️ Não foi possível atualizar a configuração do frontend: {str(e)}")
    else:
        print("\n⚠️ Arquivo de configuração do frontend não encontrado")

def verificar_ambiente():
    """Verifica o ambiente Python e sistema operacional"""
    print("\n🔍 Verificando ambiente de execução...")
    print(f"Python: {sys.version}")
    print(f"Sistema Operacional: {os.name} - {sys.platform}")
    print(f"Diretório do projeto: {DATABRIDGE_DIR}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print(" "*15 + "DATABRIDGE API - INICIALIZADOR" + " "*15)
    print("="*60)
    
    verificar_ambiente()
    instalar_dependencias_basicas()
    configurar_modo_memoria()
    atualizar_frontend_config()
    
    print("\n✅ Tudo pronto! Iniciando API...\n")
    print("-"*60)
    iniciar_api()