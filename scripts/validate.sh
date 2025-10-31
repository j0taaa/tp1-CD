#!/bin/bash

# Script de validação - verifica se tudo está funcionando após checkout limpo
# Usage: ./scripts/validate.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}=========================================="
echo "Validação do Projeto"
echo "==========================================${NC}"
echo ""

# Check Python version
echo -n "Verificando Python... "
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
if [[ $(echo "$PYTHON_VERSION 3.12" | awk '{print ($1 >= $2)}') == 1 ]]; then
    echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION"
else
    echo -e "${RED}✗${NC} Python $PYTHON_VERSION (requer 3.12+)"
    exit 1
fi

# Check virtual environment
echo -n "Verificando ambiente virtual... "
if [ -d "venv" ]; then
    echo -e "${GREEN}✓${NC}"
    source venv/bin/activate
else
    echo -e "${RED}✗${NC} Ambiente virtual não encontrado"
    echo "Execute: python3 -m venv venv"
    exit 1
fi

# Check dependencies
echo -n "Verificando dependências... "
if python3 -c "import grpc, printing_pb2" 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC} Dependências não instaladas"
    echo "Execute: pip install -r requirements.txt"
    exit 1
fi

# Check generated gRPC files
echo -n "Verificando arquivos gRPC gerados... "
if [ -f "printing_pb2.py" ] && [ -f "printing_pb2_grpc.py" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC} Arquivos gRPC não encontrados"
    echo "Execute: ./scripts/generate_proto.sh"
    exit 1
fi

# Check scripts
echo -n "Verificando scripts... "
if [ -x "scripts/run_server.sh" ] && [ -x "scripts/run_client.sh" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠${NC} Scripts não executáveis (corrigindo...)"
    chmod +x scripts/*.sh
    echo -e "${GREEN}✓${NC} Corrigido"
fi

# Run tests
echo ""
echo -n "Executando testes... "
if pytest tests/ -v --tb=line > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Todos os testes passaram"
else
    echo -e "${RED}✗${NC} Alguns testes falharam"
    echo "Execute: pytest tests/ -v para ver detalhes"
    exit 1
fi

# Check imports
echo -n "Verificando imports... "
if python3 -c "
import sys
sys.path.insert(0, '.')
from common import LamportClock, Logger
from printer.server import PrintingServiceServicer
from client.main import ClientNode
" 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC} Erro nos imports"
    exit 1
fi

echo ""
echo -e "${GREEN}=========================================="
echo "✓ Validação Completa - Tudo OK!"
echo "==========================================${NC}"
echo ""
echo "Próximos passos:"
echo "  1. Leia docs/execution.md para instruções detalhadas"
echo "  2. Execute: ./scripts/run_manual_test.sh para teste completo"
echo "  3. Consulte README.md para visão geral"

