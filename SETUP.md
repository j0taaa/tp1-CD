# Distributed Printing System - Setup Instructions

## Language & Runtime

This project uses **Python 3.13.2** (or compatible Python 3.12+).

## Environment Setup

### 1. Create Virtual Environment

```bash
python3 -m venv venv
```

### 2. Activate Virtual Environment

**On macOS/Linux:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Dependencies

The project requires the following packages:

- **grpcio**: gRPC framework for Python
- **grpcio-tools**: Protocol buffer compiler plugins for gRPC
- **protobuf**: Protocol buffer library
- **pytest**: Testing framework
- **pytest-asyncio**: Async testing support for pytest
- **black**: Code formatter
- **isort**: Import sorter
- **ruff**: Fast Python linter

## Code Formatting & Linting

### Format code with Black:
```bash
black .
```

### Sort imports with isort:
```bash
isort .
```

### Check code with Ruff:
```bash
ruff check .
```

## Verification

After setup, verify installation:
```bash
python3 --version
pip list | grep grpcio
```

You should see Python 3.13.2 (or compatible) and grpcio packages listed.

