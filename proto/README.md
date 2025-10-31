# Protocol Buffer Definition

Este diretório contém a definição do protocolo gRPC para o sistema de impressão distribuída.

## Arquivo

- `printing.proto`: Definição completa dos serviços e mensagens gRPC

## Serviços Definidos

### PrintingService
Serviço implementado pelo servidor de impressão "burro". Contém:
- `SendToPrinter`: Envia requisição de impressão do cliente para o servidor

### MutualExclusionService
Serviço implementado pelos clientes para comunicação entre pares. Contém:
- `RequestAccess`: Solicita acesso ao recurso compartilhado
- `ReleaseAccess`: Libera o acesso ao recurso compartilhado

## Mensagens

### PrintRequest / PrintResponse
Mensagens para comunicação cliente -> servidor de impressão.

### AccessRequest / AccessResponse / AccessRelease
Mensagens para comunicação cliente <-> cliente (exclusão mútua).

### Empty
Mensagem vazia usada como retorno para `ReleaseAccess`.

## Geração de Código

Para gerar o código Python a partir do arquivo .proto:

```bash
# Usando o script
./scripts/generate_proto.sh

# Ou usando make
make proto

# Ou manualmente
python3 -m grpc_tools.protoc -I proto --python_out=. --grpc_python_out=. proto/printing.proto
```

## Notas sobre a Implementação

A definição do protocolo segue exatamente a sugestão fornecida nas instruções, com uma pequena modificação:

- **Empty message**: Adicionada a mensagem `Empty` para o retorno de `ReleaseAccess`, já que no proto3 não é possível ter um retorno `void` diretamente. Esta é uma prática comum em gRPC quando um método não precisa retornar dados.

Isso permite que o método `ReleaseAccess` tenha uma assinatura consistente com o resto da API gRPC, mesmo que não retorne dados úteis.

