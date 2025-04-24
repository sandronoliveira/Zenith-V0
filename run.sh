#!/bin/bash

echo "Iniciando Zenith V1 - Sistema Empresarial com IA..."

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "Python não encontrado. Por favor, instale Python 3.8 ou superior."
    exit 1
fi

# Verificar se as dependências estão instaladas
if [ ! -d "venv" ]; then
    echo "Configurando ambiente virtual..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Verificar se o arquivo .env existe, caso contrário criar a partir do .env.example
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "Criando arquivo .env a partir do .env.example..."
        cp .env.example .env
        echo "AVISO: Criado arquivo .env a partir do modelo. Por favor, edite-o com suas configurações."
    else
        echo "AVISO: Arquivo .env.example não encontrado. Criando um .env básico..."
        echo "JWT_SECRET=insira_um_segredo_aqui" > .env
        echo "OPENAI_API_KEY=insira_sua_chave_aqui" >> .env
    fi
fi

# Definir variáveis de ambiente se não existirem
if [ -z "$OPENAI_API_KEY" ]; then
    echo "AVISO: Variável OPENAI_API_KEY não definida. Algumas funcionalidades de IA podem não funcionar."
    echo "Por favor, edite o arquivo .env e adicione sua chave da OpenAI."
fi

echo
echo "Iniciando os serviços Zenith..."
echo

# Executar o sistema
python zenith.py --all "$@"

# Desativar ambiente virtual ao sair
deactivate

echo
echo "Serviços encerrados." 