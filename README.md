# Distributed Printing System

Sistema de impressão distribuída com exclusão mútua usando gRPC, Algoritmo de Ricart-Agrawala e Relógios Lógicos de Lamport.

## 📋 Índice

- [Quick Start](#quick-start)
- [Arquitetura](#arquitetura)
- [Instalação](#instalação)
- [Execução](#execução)
- [Testes](#testes)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Documentação](#documentação)

## 🚀 Quick Start

### Pré-requisitos

- Python 3.12 ou superior
- pip (gerenciador de pacotes Python)

### Setup Rápido

```bash
# 1. Criar ambiente virtual
python3 -m venv venv

# 2. Ativar ambiente virtual
source venv/bin/activate  # macOS/Linux
# ou
venv\Scripts\activate     # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Gerar código gRPC (após criar proto/printing.proto)
python3 -m grpc_tools.protoc -I proto --python_out=. --grpc_python_out=. proto/printing.proto

# 5. Executar servidor de impressão (Terminal 1)
python3 printer/server.py --port 50051

# 6. Executar clientes (Terminais 2, 3, 4...)
python3 client/main.py --id 1 --server localhost:50051 --port 50052 --clients localhost:50053,localhost:50054
python3 client/main.py --id 2 --server localhost:50051 --port 50053 --clients localhost:50052,localhost:50054
python3 client/main.py --id 3 --server localhost:50051 --port 50054 --clients localhost:50052,localhost:50053
```

Para mais detalhes, consulte [SETUP.md](SETUP.md) e [docs/execution.md](docs/execution.md).

## 🏗️ Arquitetura

### Componentes Principais

1. **Servidor de Impressão (Burro)**
   - Porta padrão: 50051
   - Implementa `PrintingService`
   - Recebe requisições de impressão e imprime mensagens
   - Não participa do algoritmo de exclusão mútua

2. **Clientes Inteligentes**
   - Portas: 50052, 50053, 50054, ...
   - Implementam `MutualExclusionService` (como servidores)
   - Usam `PrintingService` do servidor burro (como clientes)
   - Implementam algoritmo de Ricart-Agrawala
   - Mantêm relógios lógicos de Lamport

### Algoritmos Utilizados

- **Ricart-Agrawala**: Algoritmo de exclusão mútua distribuída
- **Lamport**: Relógios lógicos para sincronização e ordenação de eventos

### Comunicação

- **gRPC**: Framework de comunicação RPC
- **Protocol Buffers**: Serialização de mensagens

## 📦 Instalação

Consulte [SETUP.md](SETUP.md) para instruções detalhadas de instalação e configuração do ambiente.

## ▶️ Execução

### Gerar Código gRPC

```bash
python3 -m grpc_tools.protoc -I proto --python_out=. --grpc_python_out=. proto/printing.proto
```

Ou use o script:

```bash
./scripts/generate_proto.sh
```

### Executar Servidor

**Opção 1: Script automatizado**
```bash
./scripts/run_server.sh --port 50051 --delay-min 2.0 --delay-max 3.0
```

**Opção 2: Manualmente**
```bash
PYTHONPATH=. python3 printer/server.py --port 50051 --delay-min 2.0 --delay-max 3.0
```

### Executar Clientes

**Opção 1: Script automatizado (recomendado para teste)**
```bash
# Executa servidor + 3 clientes automaticamente
./scripts/run_manual_test.sh
```

**Opção 2: Terminais separados**

**Terminal 1 - Servidor:**
```bash
./scripts/run_server.sh --port 50051
```

**Terminal 2 - Cliente 1:**
```bash
./scripts/run_client.sh --id 1 --server localhost:50051 --port 50052 --clients localhost:50053,localhost:50054
```

**Terminal 3 - Cliente 2:**
```bash
./scripts/run_client.sh --id 2 --server localhost:50051 --port 50053 --clients localhost:50052,localhost:50054
```

**Terminal 4 - Cliente 3:**
```bash
./scripts/run_client.sh --id 3 --server localhost:50051 --port 50054 --clients localhost:50052,localhost:50053
```

**Opção 3: Manualmente**
```bash
PYTHONPATH=. python3 client/main.py --id 1 --server localhost:50051 --port 50052 --clients localhost:50053,localhost:50054 --job-interval-min 5.0 --job-interval-max 10.0
```

Para mais detalhes, consulte [docs/execution.md](docs/execution.md).

## 🧪 Testes

### Executar Todos os Testes

```bash
pytest tests/
```

### Executar Testes Específicos

```bash
# Testes unitários
pytest tests/unit/

# Testes de integração
pytest tests/integration/

# Testes com verbose
pytest tests/ -v
```

### Verificar Cobertura

```bash
pytest --cov=. --cov-report=html tests/
```

## 📁 Estrutura do Projeto

```
tp1/
├── proto/              # Arquivos .proto para definição de serviços gRPC
├── printer/            # Implementação do servidor de impressão burro
│   └── server.py       # Servidor gRPC de impressão
├── client/             # Implementação dos clientes inteligentes
│   └── main.py         # Cliente principal com algoritmo Ricart-Agrawala
├── scripts/            # Scripts de execução e utilidades
│   ├── generate_proto.sh    # Gerar código gRPC
│   ├── run_server.sh        # Script para iniciar servidor
│   ├── run_client.sh        # Script para iniciar clientes
│   └── run_manual_test.sh   # Script para teste completo automatizado
├── tests/              # Testes automatizados
│   ├── unit/           # Testes unitários
│   └── integration/    # Testes de integração
├── docs/               # Documentação adicional
│   ├── execution.md         # Manual de execução detalhado
│   ├── testing.md          # Estratégia de testes
│   └── report_outline.md   # Esboço do relatório técnico
├── requirements.txt    # Dependências Python
├── pyproject.toml      # Configurações de formatação e linting
├── SETUP.md            # Instruções de setup
└── README.md           # Este arquivo
```

## 📚 Documentação

- [SETUP.md](SETUP.md) - Instruções de configuração do ambiente
- [docs/execution.md](docs/execution.md) - Manual de execução detalhado passo a passo
- [docs/testing.md](docs/testing.md) - Estratégia de testes e resultados
- [docs/report_outline.md](docs/report_outline.md) - Esboço do relatório técnico
- [instructions.md](instructions.md) - Especificação completa do trabalho prático

## 🤝 Contribuindo

Este é um trabalho acadêmico. Para questões ou dúvidas, consulte o professor ou a especificação em [instructions.md](instructions.md).

## 📝 Licença

Trabalho acadêmico - uso educacional.

