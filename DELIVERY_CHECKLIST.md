# Checklist de Entrega

## ✅ Entregáveis Obrigatórios

### Código Fonte Completo
- [x] Scripts de execução para iniciar servidor e clientes
  - [x] `scripts/run_server.sh` - Inicia servidor de impressão
  - [x] `scripts/run_client.sh` - Inicia cliente individual
  - [x] `scripts/run_manual_test.sh` - Teste completo automatizado
  - [x] `scripts/generate_proto.sh` - Gera código gRPC
  - [x] `scripts/validate.sh` - Validação do projeto
- [x] Manual de execução detalhado (`docs/execution.md`)
  - [x] Comandos exatos para execução
  - [x] Parâmetros de configuração
  - [x] Soluções para problemas comuns
  - [x] Exemplos de saída esperada

### Relatório Técnico (Esboço)
- [x] Esboço completo em `docs/report_outline.md`
  - [x] Explicação da arquitetura e funcionamento do código
  - [x] Análise do algoritmo de Ricart-Agrawala implementado
  - [x] Resultados dos testes realizados
  - [x] Dificuldades encontradas e soluções adotadas

## ✅ Requisitos Técnicos Implementados

### Servidor de Impressão "Burro"
- [x] Executado em porta separada (50051)
- [x] Aguarda passivamente por conexões
- [x] Imprime mensagens no formato: `[TS: {timestamp}] CLIENTE {id}: {mensagem}`
- [x] Simula delay de 2-3 segundos
- [x] Retorna confirmação de impressão
- [x] NÃO participa do algoritmo de exclusão mútua
- [x] NÃO conhece outros clientes

### Clientes Inteligentes
- [x] Implementam algoritmo completo de Ricart-Agrawala
- [x] Mantêm relógios lógicos de Lamport atualizados
- [x] Geram requisições automáticas de impressão
- [x] Exibem status local em tempo real
- [x] Executam em terminais separados (portas 50052, 50053, 50054, …)
- [x] Implementam MutualExclusionService (como servidores)
- [x] Usam PrintingService do servidor burro (como clientes)
- [x] Usam MutualExclusionService de outros clientes (como clientes)

## ✅ Testes e Validação

- [x] 42 testes automatizados (34 unitários + 8 integração)
- [x] 100% dos testes passando
- [x] Testes de monotonicidade de timestamps
- [x] Testes de exclusão mútua
- [x] Testes de algoritmo Ricart-Agrawala
- [x] Validação completa (`scripts/validate.sh`)

## ✅ Documentação

- [x] README.md atualizado com instruções finais
- [x] SETUP.md com instruções de configuração
- [x] docs/execution.md com manual detalhado
- [x] docs/testing.md com estratégia de testes
- [x] docs/report_outline.md com esboço do relatório
- [x] Comentários no código explicando o algoritmo

## ✅ Scripts e Ferramentas

- [x] Makefile com comandos úteis
- [x] Scripts bash executáveis
- [x] Configuração de formatação (black, isort, ruff)
- [x] Configuração de testes (pytest)

## ✅ Verificação Final

Execute para validar:
```bash
./scripts/validate.sh
```

Deve retornar:
- ✓ Python 3.12+
- ✓ Ambiente virtual configurado
- ✓ Dependências instaladas
- ✓ Arquivos gRPC gerados
- ✓ Scripts executáveis
- ✓ Todos os testes passando
- ✓ Imports funcionando

## 📝 Próximos Passos

1. Revisar código e documentação
2. Preencher relatório técnico completo baseado no esboço
3. Executar testes manuais finais
4. Verificar conformidade com especificação
5. Preparar para entrega até **23:59 de 31/10/2025**

