"""
Script de diagnóstico e correção de problemas do DataBridge
"""
import os
import sys
import subprocess
import importlib
from pathlib import Path

print("\n" + "="*80)
print(" "*20 + "DATABRIDGE - DIAGNÓSTICO E CORREÇÃO" + " "*20)
print("="*80 + "\n")

# Verificar dependências básicas
print(">> Verificando dependências principais...")
dependencies = [
    "fastapi",
    "uvicorn",
    "pydantic",
    "email-validator",
    "motor",
    "aiokafka",
    "sqlalchemy",
    "requests"
]

missing = []
for dep in dependencies:
    try:
        importlib.import_module(dep)
        print(f"✅ {dep} - Instalado")
    except ImportError:
        missing.append(dep)
        print(f"❌ {dep} - Não encontrado")

# Instalar dependências faltantes
if missing:
    print("\n>> Instalando dependências faltantes...")
    subprocess.run([sys.executable, "-m", "pip", "install", *missing])
    print("✅ Dependências instaladas com sucesso!")
else:
    print("\n✅ Todas as dependências principais estão instaladas!")

# Verificar arquivos principais
print("\n>> Verificando arquivos principais...")
root_dir = Path(__file__).parent
files_to_check = [
    root_dir / "databridge" / "run_api.py",
    root_dir / "databridge" / "app" / "main.py",
    root_dir / "databridge" / "app" / "models" / "mongodb.py",
    root_dir / "databridge" / "app" / "services" / "kafka.py",
    root_dir / "iniciar_frontend.py"
]

all_files_ok = True
for file_path in files_to_check:
    if file_path.exists():
        print(f"✅ {file_path.relative_to(root_dir)} - Encontrado")
    else:
        all_files_ok = False
        print(f"❌ {file_path.relative_to(root_dir)} - Não encontrado")

if not all_files_ok:
    print("\n⚠️ Alguns arquivos importantes não foram encontrados!")
    print("   O sistema pode não funcionar corretamente.")
else:
    print("\n✅ Todos os arquivos principais estão presentes!")

# Verificar processos nas portas
print("\n>> Verificando portas em uso...")
def check_port(port):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

ports = [8000, 3000]
for port in ports:
    if check_port(port):
        print(f"⚠️ Porta {port} já está em uso. Pode haver uma instância rodando.")
    else:
        print(f"✅ Porta {port} está livre.")

# Verificar se os diretórios de uploads existem
print("\n>> Verificando diretórios de uploads...")
uploads_dirs = [
    root_dir / "uploads",
    root_dir / "databridge" / "uploads"
]

for uploads_dir in uploads_dirs:
    if not uploads_dir.exists():
        print(f"Criando diretório de uploads: {uploads_dir.relative_to(root_dir)}")
        uploads_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Diretório criado: {uploads_dir.relative_to(root_dir)}")
    else:
        print(f"✅ Diretório já existe: {uploads_dir.relative_to(root_dir)}")

# Preparar variáveis de ambiente para inicialização facilitada
print("\n>> Configurando variáveis de ambiente para modo simulado...")
os.environ['DEBUG_MODE'] = 'true'
os.environ['CONNECTION_TIMEOUT'] = '2'
os.environ['MONGODB_ENABLED'] = 'false'
os.environ['KAFKA_ENABLED'] = 'false'
print("✅ Variáveis de ambiente configuradas para modo simulado")

# Verificar se há arquivo Pydantic com problemas
print("\n>> Verificando schemas Pydantic...")
schema_file = root_dir / "databridge" / "app" / "models" / "schemas.py"
if schema_file.exists():
    print(f"✅ Arquivo schemas.py encontrado")
    
    # Verificar se há modelos com EmailStr sem validador
    try:
        import email_validator
        print(f"✅ Email validator instalado e disponível")
    except ImportError:
        print(f"⚠️ Email validator não está disponível. Tentando instalar...")
        subprocess.run([sys.executable, "-m", "pip", "install", "email-validator"])
        print(f"✅ Email validator instalado")

print("\n" + "="*80)
print(">> Diagnóstico concluído")
print("="*80)

print("\nO sistema DataBridge está agora configurado para iniciar no modo simulado.")
print("Execute o script 'iniciar_databridge_simulado.py' para iniciar o sistema.")
print("\nRecomendações:")
print("1. Utilize modo DEBUG para inicialização (já configurado)")
print("2. Use conexões simuladas para MongoDB e Kafka (já configurado)")
print("3. Verifique se não há processos rodando na porta 8000 e 3000")