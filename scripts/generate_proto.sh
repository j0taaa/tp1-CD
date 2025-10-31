#!/bin/bash

# Script para gerar código gRPC a partir do arquivo .proto
# Usage: ./scripts/generate_proto.sh

set -e

# Diretório do script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Entrar no diretório do projeto
cd "$PROJECT_ROOT"

# Verificar se o ambiente virtual está ativado
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Ambiente virtual não detectado. Ativando venv..."
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        echo "❌ Erro: Ambiente virtual não encontrado. Execute 'python3 -m venv venv' primeiro."
        exit 1
    fi
fi

# Verificar se o arquivo .proto existe
PROTO_FILE="proto/printing.proto"
if [ ! -f "$PROTO_FILE" ]; then
    echo "❌ Erro: Arquivo $PROTO_FILE não encontrado."
    exit 1
fi

echo "🔄 Gerando código gRPC a partir de $PROTO_FILE..."

# Gerar código Python a partir do .proto
python3 -m grpc_tools.protoc \
    -I proto \
    --python_out=. \
    --grpc_python_out=. \
    "$PROTO_FILE"

# Verificar se os arquivos foram gerados
if [ -f "printing_pb2.py" ] && [ -f "printing_pb2_grpc.py" ]; then
    echo "✅ Código gRPC gerado com sucesso!"
    echo "   - printing_pb2.py"
    echo "   - printing_pb2_grpc.py"
else
    echo "❌ Erro: Arquivos gerados não encontrados."
    exit 1
fi

