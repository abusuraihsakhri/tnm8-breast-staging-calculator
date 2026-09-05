# TNM8 Breast Staging Calculator

> **Domain:** Medical Oncology & Cancer Staging Systems
> **Reference Guidelines & Standards:** `AJCC Cancer Staging Manual & NCCN Clinical Practice Guidelines`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## Overview

AJCC 8th Ed. Breast Cancer Stage Calculator with single and batch evaluation capabilities.

- Calculates composite scores with clinical classification (Low/Moderate/High)
- Single-case evaluation via CLI
- Batch processing for CSV datasets
- Enterprise agent framework with PHI protection and audit trail
- FastAPI REST server for integration

Author: Dr. Abu Suraih Sakhri
License: MIT

---

## Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/tnm8-breast-staging-calculator.git
cd tnm8-breast-staging-calculator

# Install dependencies
pip install -r requirements.txt
```

---

## Usage

### 1. Single Case Evaluation
```bash
python tnm8_breast.py single --v1 14.5 --v2 4.2 --v3 1.8
```

### 2. Batch Processing
```bash
python tnm8_breast.py batch -i sample.csv -o results.csv
```

### 3. Enterprise Agent CLI
```bash
# Run single task evaluation
python cli.py audit --task-id TASK-001 --primary 28.5 --secondary 14.2

# Batch process via agent framework
python cli.py batch -i sample.csv -o results.csv

# Verify HMAC audit trail integrity
python cli.py verify-audit

# Query the supervisory chat
python cli.py chat "Explain staging criteria"
```

### 4. REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

API Endpoints:
- `GET /health` - Health check
- `GET /metrics` - Prometheus operational metrics
- `POST /api/audit` - Submit task for evaluation
- `POST /api/chat` - Supervisory chat query
- `GET /api/audit/logs` - Retrieve and verify audit trail

### 5. High-Throughput Simulation
```bash
python simulator.py 1000
```

---

## Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `Patient_ID` | Patient identifier | Required |
| `v1` | Primary measurement value | Required |
| `v2` | Secondary measurement value | Optional |
| `v3` | Tertiary measurement value | Optional |

---

## Security Features

- **Zero-PHI Outbound Interceptor:** Blocks SSNs, MRNs, phone numbers, emails, and patient identifiers from outbound data
- **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs with integrity verification
- **Path Traversal Protection:** Validates all file paths before I/O operations
- **Input Sanitization:** Strips control characters and validates all inputs

### Environment Variables

| Variable | Description | Default |
|:---------|:------------|:--------|
| `AUDIT_SECRET_KEY` | Secret key for HMAC audit signing | Ephemeral random key (warns if unset) |
| `MODEL_PROVIDER` | LLM provider for agent framework | `mock` |

---

## Testing

```bash
# Run all tests
pytest -v

# Run with coverage
pytest -v --cov=. --cov-report=html
```

Test suite includes:
- Core algorithm tests (single + batch)
- Enrichment engine tests
- PHI guard enforcement tests
- Worker agent evaluation tests
- Supervisor consensus + audit tests
- **Security tests (path traversal, input sanitization, tamper detection)**

---

## Container Deployment

```bash
docker build -t tnm8-breast-staging-calculator .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=your-secret-key tnm8-breast-staging-calculator
```

Or with Docker Compose:

```bash
docker-compose up -d
```

---

## Project Structure

```
tnm8-breast-staging-calculator/
├── tnm8_breast.py          # Core domain algorithm + CLI
├── cli.py                   # Enterprise agent CLI
├── simulator.py             # High-throughput simulation
├── enrichment.py            # Enrichment feature engines
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container build spec
├── docker-compose.yml      # Container orchestration
├── agents/                 # Enterprise agent framework
│   ├── __init__.py
│   ├── api.py              # FastAPI REST server
│   ├── base.py             # Security, PHI guard, audit trail
│   ├── models.py           # Pydantic data models
│   ├── supervisor.py       # Multi-agent orchestrator
│   ├── workers.py          # Specialized evaluation workers
│   ├── llm_factory.py      # LLM provider factory
│   ├── metrics.py          # Prometheus metrics
│   ├── learning.py         # Bayesian calibration engine
│   └── streamer.py         # WebSocket telemetry
├── tests/                  # Test suite
│   ├── test_tnm8_breast_staging_calculator.py
│   ├── test_enrichment.py
│   └── test_security.py    # Security-focused tests
├── web/                    # Operations console UI
├── sample.csv              # Example input data
└── benchmark_dataset.json  # Benchmark test cases
```
