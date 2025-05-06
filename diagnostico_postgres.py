"""
Script para diagnosticar problemas com o serviço PostgreSQL no Windows
"""
import subprocess
import os
import time
import sys
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_command(cmd):
    """Executa um comando e retorna o resultado"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), -1

def check_postgres_service():
    """Verifica o status do serviço PostgreSQL"""
    print("Verificando serviço PostgreSQL...")
    stdout, stderr, code = run_command("sc query postgresql")
    
    if code != 0:
        stdout, stderr, code = run_command("sc query \"postgresql*\"")
        if code != 0:
            print("Serviço PostgreSQL não encontrado! Tentando verificar todos os serviços relacionados...")
            stdout, stderr, code = run_command("sc query state= all | findstr /i \"postgres\"")
            if stdout:
                print("Serviços potenciais encontrados:")
                print(stdout)
            else:
                print("Nenhum serviço relacionado ao PostgreSQL encontrado.")
                return None
        
    if "RUNNING" in stdout:
        print("✅ Serviço PostgreSQL está em execução!")
        return True
    elif "STOPPED" in stdout:
        print("❌ Serviço PostgreSQL está parado.")
        return False
    else:
        print("Estado desconhecido do serviço PostgreSQL:")
        print(stdout)
        return None

def check_port_5432():
    """Verifica se a porta 5432 está sendo usada"""
    print("\nVerificando se a porta 5432 está em uso...")
    stdout, stderr, code = run_command("netstat -ano | findstr :5432")
    
    if stdout:
        print("Porta 5432 está em uso:")
        print(stdout)
        return True
    else:
        print("Porta 5432 não está sendo usada por nenhum processo.")
        return False

def check_postgres_logs():
    """Tenta localizar e verificar os últimos logs do PostgreSQL"""
    print("\nProcurando por logs do PostgreSQL...")
    potential_paths = [
        r"C:\Program Files\PostgreSQL\*\data\log",
        r"%PROGRAMDATA%\PostgreSQL\*\data\log"
    ]
    
    log_found = False
    for path in potential_paths:
        expanded_path = os.path.expandvars(path)
        stdout, stderr, code = run_command(f"dir {expanded_path} /s /b")
        if stdout:
            log_files = stdout.strip().split("\n")
            print(f"Logs encontrados em: {os.path.dirname(log_files[0])}")
            
            # Pegar o arquivo de log mais recente
            for log_file in log_files:
                if log_file.endswith(".log"):
                    print(f"\nMostrando as últimas 20 linhas do arquivo: {os.path.basename(log_file)}")
                    stdout, stderr, code = run_command(f"type {log_file} | tail -20")
                    if stdout:
                        print("-" * 80)
                        print(stdout)
                        print("-" * 80)
                    else:
                        stdout, stderr, code = run_command(f"type {log_file}")
                        lines = stdout.strip().split("\n")
                        if lines:
                            print("-" * 80)
                            for line in lines[-20:]:
                                print(line)
                            print("-" * 80)
                    log_found = True
                    break
            
            if log_found:
                break
    
    if not log_found:
        print("Não foi possível encontrar arquivos de log do PostgreSQL.")

def attempt_to_start_service():
    """Tenta iniciar o serviço PostgreSQL"""
    print("\nTentando iniciar o serviço PostgreSQL...")
    if not is_admin():
        print("⚠️ Este script não está sendo executado como administrador.")
        print("⚠️ Algumas operações podem falhar devido a permissões insuficientes.")
    
    # Tenta encontrar o nome exato do serviço primeiro
    stdout, stderr, code = run_command("sc query state= all | findstr /i \"postgres\"")
    service_name = None
    
    if stdout:
        lines = stdout.strip().split("\n")
        for line in lines:
            if "SERVICE_NAME" in line:
                service_name = line.split(":")[1].strip()
                break
    
    if not service_name:
        service_name = "postgresql"  # Nome padrão
    
    print(f"Tentando iniciar o serviço: {service_name}")
    stdout, stderr, code = run_command(f"sc start {service_name}")
    
    if "START_PENDING" in stdout or "RUNNING" in stdout:
        print("✅ Serviço iniciado com sucesso!")
        return True
    else:
        print("❌ Falha ao iniciar o serviço:")
        print(stdout)
        if stderr:
            print("Erro:", stderr)
        return False

def fix_common_issues():
    """Tenta corrigir problemas comuns"""
    print("\nVerificando problemas comuns...")
    
    # Verifica se o diretório de dados existe e tem permissões adequadas
    stdout, stderr, code = run_command("sc qc postgresql")
    service_path = None
    
    if "BINARY_PATH_NAME" in stdout:
        for line in stdout.strip().split("\n"):
            if "BINARY_PATH_NAME" in line:
                parts = line.split(":", 1)
                if len(parts) > 1:
                    service_path = parts[1].strip().strip('"')
                    break
    
    if service_path:
        binary_dir = os.path.dirname(service_path)
        data_dir = None
        
        # Tenta encontrar o diretório de dados
        if os.path.exists(binary_dir):
            print(f"Diretório binário do PostgreSQL: {binary_dir}")
            
            # Verifica se há um diretório data na mesma hierarquia
            potential_data_dir = os.path.join(os.path.dirname(binary_dir), "data")
            if os.path.exists(potential_data_dir):
                data_dir = potential_data_dir
                print(f"Diretório de dados encontrado: {data_dir}")
                
                # Verifica permissões
                print("Verificando permissões no diretório de dados...")
                stdout, stderr, code = run_command(f"icacls \"{data_dir}\"")
                if stdout:
                    print(stdout)
            else:
                print("Diretório de dados não encontrado em local padrão.")
        else:
            print(f"Diretório binário não encontrado: {binary_dir}")
    else:
        print("Não foi possível determinar o caminho do serviço PostgreSQL.")

def main():
    print("===== Diagnóstico do PostgreSQL no Windows =====")
    
    # Verificar status atual
    status = check_postgres_service()
    
    # Verificar porta
    port_in_use = check_port_5432()
    
    if status is False:  # Serviço está parado
        print("\n⚠️ O serviço PostgreSQL está parado.")
        # Verificar logs antes de tentar iniciar
        check_postgres_logs()
        
        # Verificar problemas comuns
        fix_common_issues()
        
        # Tentar iniciar o serviço
        print("\nTentando iniciar o serviço PostgreSQL...")
        started = attempt_to_start_service()
        
        if started:
            print("Aguardando 5 segundos para o serviço inicializar...")
            time.sleep(5)
            
            # Verificar novamente o status
            new_status = check_postgres_service()
            if new_status:
                print("\n✅ O serviço PostgreSQL foi iniciado com sucesso!")
            else:
                print("\n❌ O serviço PostgreSQL não conseguiu permanecer em execução.")
                print("Isso indica um problema grave no serviço. Verificando os logs novamente...")
                check_postgres_logs()
        
    elif status is True:  # Serviço está em execução
        print("\n✅ O serviço PostgreSQL já está em execução.")
        if not port_in_use:
            print("⚠️ Alerta: Embora o serviço esteja em execução, a porta 5432 não está sendo usada.")
            print("Isso pode indicar que o PostgreSQL está configurado para usar uma porta diferente,")
            print("ou que o processo não conseguiu vincular-se à porta 5432.")
    else:
        print("\n❓ Não foi possível determinar o status do serviço PostgreSQL.")
        check_postgres_logs()
    
    print("\n===== Verificação Concluída =====")
    print("Se o problema persistir, considere reinstalar o PostgreSQL ou")
    print("verificar se há conflitos com outros bancos de dados.")

if __name__ == "__main__":
    main()