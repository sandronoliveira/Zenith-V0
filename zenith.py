#!/usr/bin/env python3
"""
Zenith V1 - Sistema Empresarial com IA
Script principal para iniciar todos os componentes do sistema
"""

import os
import sys
import argparse
import subprocess
import time
import signal
import atexit
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
def setup_environment():
    """Configurar ambiente de execução e variáveis de ambiente."""
    # Obter diretório raiz
    root_dir = Path(__file__).parent.absolute()
    os.chdir(root_dir)
    
    # Procurar por arquivo .env em ordem de preferência
    env_files = [
        os.path.join(root_dir, ".env"),
        os.path.join(root_dir, ".env.local"),
        os.path.join(root_dir, f".env.{os.environ.get('ENV', 'development')}"),
        os.path.join(root_dir, ".env.example")
    ]
    
    # Carregar o primeiro arquivo que existir
    for env_file in env_files:
        if os.path.exists(env_file):
            print(f"Carregando variáveis de ambiente de: {env_file}")
            load_dotenv(env_file)
            break
    else:
        print("Aviso: Nenhum arquivo .env encontrado. Usando variáveis de ambiente do sistema.")
    
    # Verificar variáveis críticas
    critical_vars = ["JWT_SECRET", "OPENAI_API_KEY"]
    missing_vars = [var for var in critical_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"AVISO: As seguintes variáveis de ambiente críticas não estão definidas: {', '.join(missing_vars)}")
        print("Algumas funcionalidades podem não funcionar corretamente.")

# Processos ativos
active_processes = []

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Zenith V1 - Sistema Empresarial com IA')
    parser.add_argument('--all', action='store_true', help='Iniciar todos os serviços')
    parser.add_argument('--auth', action='store_true', help='Iniciar serviço de autenticação')
    parser.add_argument('--orchestrator', action='store_true', help='Iniciar orquestrador principal')
    parser.add_argument('--llm', action='store_true', help='Iniciar roteador de LLM')
    parser.add_argument('--rag', action='store_true', help='Iniciar sistema RAG')
    parser.add_argument('--connectors', action='store_true', help='Iniciar API de conectores')
    parser.add_argument('--port-base', type=int, default=int(os.environ.get('PORT_BASE', 8000)), 
                        help='Porta base para os serviços')
    parser.add_argument('--dev', action='store_true', help='Modo de desenvolvimento')
    parser.add_argument('--env-file', type=str, help='Arquivo de variáveis de ambiente personalizado')
    
    return parser.parse_args()

def start_service(module_path, service_name, port):
    """Iniciar um serviço usando uvicorn."""
    print(f"Iniciando {service_name} na porta {port}...")
    
    # Definir variáveis de ambiente
    env = os.environ.copy()
    env['PORT'] = str(port)
    
    # Construir comando
    cmd = [
        sys.executable, '-m', 'uvicorn', 
        f"{module_path}:app", 
        '--host', '0.0.0.0', 
        '--port', str(port),
        '--reload' if args.dev else ''
    ]
    
    # Filtrar argumentos vazios
    cmd = [arg for arg in cmd if arg]
    
    # Iniciar o processo
    process = subprocess.Popen(cmd, env=env)
    active_processes.append((process, service_name))
    return process

def cleanup():
    """Limpar todos os processos na saída."""
    print("\nEncerrando todos os serviços...")
    for process, name in active_processes:
        print(f"Encerrando {name}...")
        try:
            process.terminate()
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print(f"Forçando encerramento de {name}...")
            process.kill()

def signal_handler(sig, frame):
    """Gerenciar sinais para encerramento limpo."""
    cleanup()
    sys.exit(0)

def main():
    """Função principal."""
    # Configurar ambiente
    if args.env_file and os.path.exists(args.env_file):
        print(f"Carregando variáveis de ambiente de: {args.env_file}")
        load_dotenv(args.env_file)
    else:
        setup_environment()
    
    # Configurar portas
    port_base = args.port_base
    services = {}
    
    # Se nenhum serviço específico for selecionado, ativar todos
    if not any([args.auth, args.orchestrator, args.llm, args.rag, args.connectors]):
        args.all = True
    
    # Iniciar serviços conforme solicitado
    if args.all or args.auth:
        services['auth'] = start_service('services.auth.server', 'Serviço de Autenticação', port_base)
        port_base += 1
    
    if args.all or args.orchestrator:
        services['orchestrator'] = start_service('services.orchestrator.server', 'Orquestrador Principal', port_base)
        port_base += 1
    
    if args.all or args.llm:
        services['llm'] = start_service('ai.llm_router.router', 'Roteador de LLM', port_base)
        port_base += 1
    
    if args.all or args.rag:
        services['rag'] = start_service('ai.rag.server', 'Sistema RAG', port_base)
        port_base += 1
    
    if args.all or args.connectors:
        services['connectors'] = start_service('connectors.api.connector_api', 'API de Conectores', port_base)
        port_base += 1
    
    print("\nTodos os serviços iniciados. Pressione Ctrl+C para encerrar.")
    
    # Manter o script em execução
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nEncerrando o sistema Zenith...")

if __name__ == "__main__":
    # Registrar handlers para encerramento limpo
    atexit.register(cleanup)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Parse argumentos
    args = parse_arguments()
    
    # Iniciar aplicação
    main() 