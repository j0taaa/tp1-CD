# Manual de Execução Detalhado

Este documento fornece instruções passo a passo para executar o Sistema de Impressão Distribuída.

## Pré-requisitos

- Python 3.12 ou superior
- pip (gerenciador de pacotes Python)
- Terminal/shell (bash, zsh, etc.)

## Passo 1: Configuração Inicial

### 1.1 Clone ou extraia o projeto

```bash
cd /caminho/para/projeto
```

### 1.2 Criar ambiente virtual

```bash
python3 -m venv venv
```

### 1.3 Ativar ambiente virtual

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 1.4 Instalar dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 1.5 Gerar código gRPC

```bash
# Opção 1: Usando o script
./scripts/generate_proto.sh

# Opção 2: Usando make
make proto

# Opção 3: Manualmente
python3 -m grpc_tools.protoc -I proto --python_out=. --grpc_python_out=. proto/printing.proto
```

**Verificação:** Você deve ver os arquivos `printing_pb2.py` e `printing_pb2_grpc.py` criados.

## Passo 2: Executar o Sistema

### Opção A: Execução Automatizada (Recomendado)

**Usar o script de teste manual:**

```bash
./scripts/run_manual_test.sh
```

Este script:
- Inicia automaticamente o servidor de impressão na porta 50051
- Inicia 3 clientes nas portas 50052, 50053, 50054
- Configura todos os parâmetros automaticamente
- Registra logs em `test_logs/`
- Permite parar com Ctrl+C

**Saída esperada:**
- Servidor iniciado e aguardando conexões
- Três clientes conectados e gerando jobs automaticamente
- Mensagens de impressão aparecendo no formato: `[TS: {timestamp}] CLIENTE {id}: {mensagem}`

### Opção B: Execução Manual (Terminais Separados)

#### Terminal 1: Servidor de Impressão

```bash
# Ativar ambiente virtual (se ainda não ativado)
source venv/bin/activate

# Executar servidor
./scripts/run_server.sh --port 50051 --delay-min 2.0 --delay-max 3.0
```

**Ou manualmente:**
```bash
PYTHONPATH=/caminho/para/projeto python3 printer/server.py --port 50051 --delay-min 2.0 --delay-max 3.0
```

**Saída esperada:**
```
[TS: {timestamp}] SERVIDOR: INFO: Servidor de impressão iniciado na porta 50051
[TS: {timestamp}] SERVIDOR: INFO: Delay de impressão: 2.0-3.0 segundos
```

#### Terminal 2: Cliente 1

```bash
source venv/bin/activate
./scripts/run_client.sh --id 1 --server localhost:50051 --port 50052 --clients localhost:50053,localhost:50054 --job-interval-min 5.0 --job-interval-max 10.0
```

**Ou manualmente:**
```bash
PYTHONPATH=/caminho/para/projeto python3 client/main.py --id 1 --server localhost:50051 --port 50052 --clients localhost:50053,localhost:50054 --job-interval-min 5.0 --job-interval-max 10.0
```

#### Terminal 3: Cliente 2

```bash
source venv/bin/activate
./scripts/run_client.sh --id 2 --server localhost:50051 --port 50053 --clients localhost:50052,localhost:50054 --job-interval-min 5.0 --job-interval-max 10.0
```

#### Terminal 4: Cliente 3

```bash
source venv/bin/activate
./scripts/run_client.sh --id 3 --server localhost:50051 --port 50054 --clients localhost:50052,localhost:50053 --job-interval-min 5.0 --job-interval-max 10.0
```

## Passo 3: Observar o Comportamento

### 3.1 Verificar Exclusão Mútua

Quando múltiplos clientes estão rodando:

1. **Observar logs do servidor:** Deve imprimir mensagens de apenas um cliente por vez
2. **Observar logs dos clientes:** Status reports mostrando estado de acesso
3. **Verificar ordenação:** Clientes com timestamps menores obtêm acesso primeiro

### 3.2 Exemplo de Saída Esperada

**Servidor:**
```
[TS: 5] CLIENTE 1: Documento #1 do cliente 1
[TS: 15] CLIENTE 2: Documento #1 do cliente 2
[TS: 25] CLIENTE 3: Documento #1 do cliente 3
```

**Cliente 1:**
```
[TS: 1] CLIENTE 1: INFO: Solicitando acesso para impressão (requisição #1, TS: 1)
[TS: 1] CLIENTE 1: INFO: Aguardando respostas (0/2)
[TS: 2] CLIENTE 1: INFO: Resposta recebida de localhost:50053 (granted: True)
[TS: 3] CLIENTE 1: INFO: Resposta recebida de localhost:50054 (granted: True)
[TS: 3] CLIENTE 1: INFO: Acesso concedido! Todas as respostas recebidas.
```

## Passo 4: Parar o Sistema

**Se usando script automatizado:** Pressione `Ctrl+C`

**Se usando terminais separados:** Pressione `Ctrl+C` em cada terminal

## Passo 5: Executar Testes

```bash
# Todos os testes
pytest tests/ -v

# Apenas unitários
pytest tests/unit/ -v

# Apenas integração
pytest tests/integration/ -v
```

## Parâmetros de Configuração

Veja [docs/execution.md](docs/execution.md) para lista completa de parâmetros.

## Problemas Comuns

Veja [docs/execution.md](docs/execution.md) para soluções de problemas comuns.

