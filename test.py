#!/usr/bin/env python3
"""
Script de teste para verificar as importações básicas
"""

import sys
import os

print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Working directory: {os.getcwd()}")

# Lista de pacotes importantes para verificar
essential_packages = [
    "dotenv",
    "uvicorn",
    "fastapi",
    "pydantic",
    "httpx",
    "jose",
    "passlib",
    "openai"
]

print("\nVerificando importações essenciais:")

for package in essential_packages:
    print(f"\nTentando importar {package}...")
    try:
        if package == "dotenv":
            from dotenv import load_dotenv
            print(f"✓ {package} importado com sucesso!")
            
            # Testar carregamento de arquivo .env
            if os.path.exists(".env"):
                load_dotenv()
                print("✓ Arquivo .env carregado com sucesso!")
            else:
                print("✗ Arquivo .env não encontrado!")
        
        elif package == "uvicorn":
            import uvicorn
            print(f"✓ {package} importado com sucesso! (versão {uvicorn.__version__})")
        
        elif package == "fastapi":
            import fastapi
            print(f"✓ {package} importado com sucesso! (versão {fastapi.__version__})")
        
        elif package == "pydantic":
            import pydantic
            print(f"✓ {package} importado com sucesso! (versão {pydantic.__version__})")
        
        elif package == "httpx":
            import httpx
            print(f"✓ {package} importado com sucesso! (versão {httpx.__version__})")
        
        elif package == "jose":
            from jose import jwt
            print(f"✓ {package} importado com sucesso!")
        
        elif package == "passlib":
            from passlib.context import CryptContext
            print(f"✓ {package} importado com sucesso!")
        
        elif package == "openai":
            import openai
            print(f"✓ {package} importado com sucesso! (versão {openai.__version__})")
            
    except ImportError as e:
        print(f"✗ Erro ao importar {package}: {e}")
        print(f"  Sugestão: Execute 'pip install {package}' manualmente.")

print("\nVerificando comandos do sistema:")
try:
    import subprocess
    
    # Verificar se o comando uvicorn pode ser encontrado
    result = subprocess.run([sys.executable, "-m", "uvicorn", "--version"], 
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    if result.returncode == 0:
        print(f"✓ Comando 'uvicorn' está disponível: {result.stdout.strip()}")
    else:
        print(f"✗ Erro ao executar 'uvicorn': {result.stderr.strip()}")
        
except Exception as e:
    print(f"✗ Erro ao verificar comandos: {e}")

print("\nTeste concluído!") 