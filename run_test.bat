@echo off
echo Executando teste de dependências Python...

REM Verificar se o ambiente virtual existe
if exist venv\ (
    echo Ativando ambiente virtual...
    call venv\Scripts\activate
) else (
    echo Ambiente virtual não encontrado. Criando um novo...
    python -m venv venv
    call venv\Scripts\activate
    
    echo Instalando python-dotenv...
    pip install python-dotenv
)

REM Executar o script de teste
python test.py

REM Desativar ambiente virtual
call venv\Scripts\deactivate

echo.
echo Teste concluído. Pressione qualquer tecla para sair.
pause 