# Relatório Técnico - Esboço

## 1. Introdução

### 1.1 Objetivo
Implementar um sistema distribuído de impressão com exclusão mútua usando gRPC, algoritmo de Ricart-Agrawala e relógios lógicos de Lamport.

### 1.2 Contexto
Sistema onde múltiplos processos clientes disputam acesso exclusivo a um servidor de impressão "burro", coordenando-se através de algoritmo distribuído de exclusão mútua.

## 2. Arquitetura e Funcionamento do Código

### 2.1 Visão Geral da Arquitetura
- Servidor de Impressão ("Burro")
- Clientes Inteligentes
- Protocolo gRPC
- Relógios Lógicos de Lamport
- Algoritmo de Ricart-Agrawala

### 2.2 Servidor de Impressão
**Localização:** `printer/server.py`
- Recebe requisições via gRPC
- Imprime mensagens formatadas
- Simula delay de impressão
- Retorna confirmação

### 2.3 Clientes Inteligentes
**Localização:** `client/main.py`
- Implementam algoritmo de Ricart-Agrawala
- Mantêm relógio lógico de Lamport
- Geram jobs automaticamente
- Coordenam acesso com outros clientes

### 2.4 Utilitários Compartilhados
**Localização:** `common/`
- Lamport Clock
- Logger
- Message Builder

## 3. Análise do Algoritmo de Ricart-Agrawala

### 3.1 Descrição do Algoritmo
**Referência:** Ricart & Agrawala (1981)

### 3.2 Implementação
- Requisição de acesso
- Decisão de concessão/adiamento
- Liberação de acesso

### 3.3 Garantias
- Exclusão mútua ✓
- Ordenação justa ✓
- Vivacidade ✓
- Sincronização de relógios ✓

## 4. Resultados dos Testes Realizados

### 4.1 Testes Unitários
- 34 testes - 100% passando
- Cobertura completa dos componentes

### 4.2 Testes de Integração
- 8 testes - 100% passando
- Validação do algoritmo completo

### 4.3 Testes Manuais
- Cenários de execução validados
- Exclusão mútua verificada

### 4.4 Verificação de Monotonicidade
- Todos os testes de monotonicidade passando

## 5. Dificuldades Encontradas e Soluções Adotadas

### 5.1 Implementação de Respostas Deferidas
**Dificuldade:** gRPC não suporta respostas não solicitadas
**Solução:** Notificação via AccessRelease

### 5.2 Coordenação de Threads
**Dificuldade:** Race conditions e deadlocks
**Solução:** Locks e conditions apropriados

### 5.3 Ordenação de Eventos
**Dificuldade:** Garantir ordenação com delays de rede
**Solução:** Implementação rigorosa das regras de Lamport

### 5.4 Testes de Integração
**Dificuldade:** Configuração de múltiplos serviços
**Solução:** Fixtures pytest e portas fixas

### 5.5 Geração Automática de Jobs
**Dificuldade:** Balancear automático vs manual
**Solução:** Threads separadas e configuração via CLI

## 6. Conclusão

### 6.1 Objetivos Alcançados
✅ Sistema distribuído funcional
✅ Algoritmo Ricart-Agrawala implementado
✅ Relógios Lamport funcionando
✅ Testes abrangentes
✅ Documentação completa

### 6.2 Aprendizados Principais
- Algoritmos distribuídos requerem atenção a detalhes
- Thread safety é crítica
- Testes unitários e de integração são complementares

### 6.3 Referências
- Ricart & Agrawala (1981)
- Lamport (2019)
- Documentação gRPC

