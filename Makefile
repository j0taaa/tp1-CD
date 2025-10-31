# Makefile para o projeto Distributed Printing System

.PHONY: proto test clean format lint help

# Gerar código gRPC a partir do arquivo .proto
proto:
	@echo "Gerando código gRPC..."
	python3 -m grpc_tools.protoc -I proto --python_out=. --grpc_python_out=. proto/printing.proto
	@echo "✅ Código gRPC gerado com sucesso!"

# Executar testes
test:
	pytest tests/ -v

# Executar testes com cobertura
test-cov:
	pytest tests/ --cov=. --cov-report=html

# Formatar código
format:
	black .
	isort .

# Verificar código com linter
lint:
	ruff check .

# Limpar arquivos gerados e cache
clean:
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -r {} + 2>/dev/null || true
	rm -f printing_pb2.py printing_pb2_grpc.py

# Ajuda
help:
	@echo "Comandos disponíveis:"
	@echo "  make proto      - Gerar código gRPC"
	@echo "  make test       - Executar testes"
	@echo "  make test-cov   - Executar testes com cobertura"
	@echo "  make format     - Formatar código"
	@echo "  make lint       - Verificar código com linter"
	@echo "  make clean      - Limpar arquivos gerados"
	@echo "  make help       - Mostrar esta ajuda"

