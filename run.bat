@echo off
echo Iniciando Zenith V1 - Sistema Empresarial com IA...

REM Habilitar saída detalhada para depuração
echo Executando em modo de diagnóstico...

REM Verificar se Python está instalado
echo Verificando instalação do Python...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python não encontrado. Por favor, instale Python 3.8 ou superior.
    pause
    exit /b 1
)
echo Python encontrado!

REM Verificar se as dependências estão instaladas
if not exist venv\ (
    echo Configurando ambiente virtual...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo Erro ao criar ambiente virtual.
        pause
        exit /b 1
    )
    
    call venv\Scripts\activate
    if %errorlevel% neq 0 (
        echo Erro ao ativar ambiente virtual.
        pause
        exit /b 1
    )
    
    echo Instalando dependências...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Erro ao instalar dependências.
        pause
        exit /b 1
    )
) else (
    echo Ativando ambiente virtual...
    call venv\Scripts\activate
    if %errorlevel% neq 0 (
        echo Erro ao ativar ambiente virtual.
        pause
        exit /b 1
    )
)

REM Instalar explicitamente os pacotes essenciais
echo Verificando instalação de pacotes essenciais...

echo Instalando python-dotenv...
pip install python-dotenv
if %errorlevel% neq 0 (
    echo Erro ao instalar python-dotenv.
    pause
    exit /b 1
)

echo Instalando uvicorn...
pip install uvicorn
if %errorlevel% neq 0 (
    echo Erro ao instalar uvicorn.
    pause
    exit /b 1
)

echo Instalando fastapi...
pip install fastapi
if %errorlevel% neq 0 (
    echo Erro ao instalar fastapi.
    pause
    exit /b 1
)

echo Executando o script de teste para verificar as dependências...
python test.py
if %errorlevel% neq 0 (
    echo Erro ao executar o teste de dependências.
    pause
    exit /b 1
)

REM Verificar se o arquivo .env existe, caso contrário criar a partir do .env.example
if not exist .env (
    if exist .env.example (
        echo Criando arquivo .env a partir do .env.example...
        copy .env.example .env
        echo AVISO: Criado arquivo .env a partir do modelo. Por favor, edite-o com suas configurações.
    ) else (
        echo AVISO: Arquivo .env.example não encontrado. Criando um .env básico...
        (
            echo # Configurações Básicas de Desenvolvimento
            echo DEBUG=True
            echo ENV=development
            echo LOG_LEVEL=DEBUG
            echo.
            echo # Serviços e Portas
            echo PORT_BASE=8000
            echo.
            echo # Segurança
            echo JWT_SECRET=zenith_development_secret_change_in_production
            echo JWT_ALGORITHM=HS256
            echo JWT_EXPIRATION_MINUTES=60
            echo.
            echo # OpenAI - IMPORTANTE: Insira sua chave abaixo
            echo OPENAI_API_KEY=insira_sua_chave_aqui
            echo.
            echo # Redis (in-memory para desenvolvimento)
            echo REDIS_HOST=localhost
            echo REDIS_PORT=6379
            echo.
            echo # Neo4j (conexão padrão para desenvolvimento)
            echo NEO4J_URI=bolt://localhost:7687
            echo NEO4J_USER=neo4j
            echo NEO4J_PASSWORD=password
        ) > .env
    )
)

REM Definir variáveis de ambiente se não existirem
if "%OPENAI_API_KEY%"=="" (
    echo AVISO: Variável OPENAI_API_KEY não definida. Algumas funcionalidades de IA podem não funcionar.
    echo Por favor, edite o arquivo .env e adicione sua chave da OpenAI.
)

echo.
echo Iniciando os serviços Zenith...
echo.

REM Executar o sistema com saída para log e garantindo que os módulos sejam encontrados
echo Executando o sistema (registrando saída em zenith_log.txt)...
python -m zenith --all %* > zenith_log.txt 2>&1
if %errorlevel% neq 0 (
    echo.
    echo Erro ao executar o sistema Zenith. Verifique o arquivo zenith_log.txt para detalhes.
    type zenith_log.txt
    pause
    exit /b 1
)

REM Desativar ambiente virtual ao sair
call venv\Scripts\deactivate

echo.
echo Serviços encerrados.

REM Manter a janela aberta para leitura em caso de erro
pause 