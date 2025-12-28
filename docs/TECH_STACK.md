# LogMiner-QA Technology Stack

Complete reference of all technologies, libraries, frameworks, and tools used in the LogMiner-QA project.

---

## Table of Contents

1. [Core Language & Runtime](#core-language--runtime)
2. [Core Dependencies](#core-dependencies)
3. [Machine Learning & AI](#machine-learning--ai)
4. [NLP & Text Processing](#nlp--text-processing)
5. [Data Processing & Analysis](#data-processing--analysis)
6. [Web & API Framework](#web--api-framework)
7. [Security & Cryptography](#security--cryptography)
8. [Python Standard Library](#python-standard-library)
9. [Development & Deployment Tools](#development--deployment-tools)
10. [External Services & Connectors](#external-services--connectors)
11. [Recommended Tools](#recommended-tools)

---

## Core Language & Runtime

### Python
- **Version**: Python 3.11+ (compatible with 3.8+)
- **Why**: Primary programming language for the entire project
- **Usage**: All application code, scripts, and tooling

---

## Core Dependencies

These are the primary external libraries specified in `requirements.txt`:

### 1. requests (>=2.32.0)
- **Purpose**: HTTP client library
- **Usage**: 
  - Elasticsearch connector (`src/logminer_qa/connectors/elk.py`)
  - Datadog API connector (`src/logminer_qa/connectors/datadog.py`)
- **License**: Apache 2.0

### 2. scikit-learn (>=1.5.0)
- **Purpose**: Machine learning library
- **Usage**:
  - `MiniBatchKMeans` for event clustering (`src/logminer_qa/clustering.py`)
  - `TfidfVectorizer` for text vectorization (`src/logminer_qa/clustering.py`)
  - `LabelEncoder` for journey sequence encoding (`src/logminer_qa/journey.py`)
  - `IsolationForest` for anomaly detection (`src/logminer_qa/anomaly.py`)
- **License**: BSD 3-Clause

### 3. sentence-transformers (>=3.0.0)
- **Purpose**: Transformer-based sentence embeddings
- **Usage**: 
  - Text embedding generation (`src/logminer_qa/embeddings.py`)
  - Default model: `sentence-transformers/all-MiniLM-L6-v2`
  - Generates 384-dimensional embedding vectors
- **Dependencies**: PyTorch, transformers, sentencepiece
- **License**: Apache 2.0

### 4. tensorflow-cpu (>=2.17.0)
- **Purpose**: Deep learning framework (CPU-only build)
- **Usage**:
  - LSTM model for journey sequence analysis (`src/logminer_qa/journey.py`)
  - Keras API for neural network construction
- **Note**: Uses `tf-keras` compatibility shim for Keras 3 support
- **License**: Apache 2.0

### 5. fastapi (>=0.115.0)
- **Purpose**: Modern, fast web framework for building APIs
- **Usage**:
  - REST API server (`src/logminer_qa/server.py`)
  - Request/response models with Pydantic
  - `/analyze` endpoint for log processing
- **License**: MIT

### 6. uvicorn (>=0.30.0)
- **Purpose**: ASGI server for FastAPI
- **Usage**: Production server for API deployment
- **License**: BSD

### 7. tqdm (>=4.66.0)
- **Purpose**: Progress bars for long-running operations
- **Usage**: 
  - Embedding progress tracking (`src/logminer_qa/embeddings.py`)
  - Visual feedback during processing large datasets
- **License**: MIT/Mozilla Public License 2.0

---

## Machine Learning & AI

### TensorFlow/Keras
- **Components**:
  - `keras.Input` - Input layer definition
  - `keras.layers.Embedding` - Word/event embeddings
  - `keras.layers.LSTM` - Long Short-Term Memory cells
  - `keras.layers.Dropout` - Regularization
  - `keras.layers.Dense` - Fully connected layers
  - `keras.Model` - Model compilation and training
  - `keras.optimizers.Adam` - Optimizer
  - `keras.utils.pad_sequences` - Sequence padding
  - `keras.utils.to_categorical` - One-hot encoding
- **Model**: LSTM for user journey sequence prediction
- **Architecture**: Embedding → LSTM → Dropout → Dense → Softmax

### scikit-learn ML Components
- **Clustering**: `MiniBatchKMeans` (memory-efficient K-means)
- **Feature Extraction**: `TfidfVectorizer` (Term Frequency-Inverse Document Frequency)
- **Anomaly Detection**: `IsolationForest` (unsupervised anomaly detection)
- **Preprocessing**: `LabelEncoder` (categorical encoding)

### Sentence Transformers
- **Model**: `all-MiniLM-L6-v2`
- **Output Dimension**: 384
- **Use Case**: Semantic similarity and clustering of log messages
- **Features**: 
  - Batch processing (configurable batch size)
  - Normalized embeddings
  - GPU/CPU support

---

## NLP & Text Processing

### spaCy (Optional, Recommended)
- **Purpose**: Named Entity Recognition (NER) for PII detection
- **Model**: `en_core_web_sm` (English small model)
- **Usage**: 
  - PII entity extraction (`src/logminer_qa/parsing.py`)
  - Entity types: PERSON, ORG, GPE, LOC, DATE, etc.
  - Gracefully degrades if not installed
- **Installation**: 
  ```bash
  pip install spacy
  python -m spacy download en_core_web_sm
  ```
- **License**: MIT

### Regular Expressions (re)
- **Purpose**: Pattern-based PII detection
- **Usage**: 
  - Email addresses, phone numbers, IBANs, account numbers
  - API endpoint extraction
  - Status code detection
  - Error token identification
- **Location**: `src/logminer_qa/sanitizer.py`, `src/logminer_qa/parsing.py`

---

## Data Processing & Analysis

### NumPy
- **Purpose**: Numerical computing (dependency of scikit-learn, TensorFlow)
- **Usage**:
  - Array operations for embeddings
  - Numerical type conversions for JSON serialization
  - Statistical calculations
- **Version**: Included via scikit-learn/TensorFlow dependencies

### Pydantic
- **Purpose**: Data validation (dependency of FastAPI)
- **Usage**:
  - API request/response models (`src/logminer_qa/server.py`)
  - Type validation and serialization
- **Version**: Included via FastAPI dependencies

---

## Web & API Framework

### FastAPI
- **Features Used**:
  - `FastAPI` application class
  - `@app.post()` decorators for endpoints
  - `HTTPException` for error handling
  - Automatic OpenAPI/Swagger documentation
- **Endpoint**: `/analyze` - Main log analysis endpoint

### Uvicorn
- **Purpose**: ASGI server implementation
- **Usage**: Production deployment of FastAPI application
- **Configuration**: Supports factory pattern (`--factory` flag)

---

## Security & Cryptography

### Python Standard Library - hashlib
- **Purpose**: Cryptographic hashing
- **Algorithms Used**:
  - `SHA-256` - Primary hashing algorithm (configurable)
  - `blake2b` - Token encoding (12-byte digest)
- **Usage**:
  - `src/logminer_qa/sanitizer.py` - PII value hashing
  - `src/logminer_qa/token_store.py` - Token generation
- **Secret Management**: `LOGMINER_HASH_SECRET` environment variable

### Threading (threading)
- **Purpose**: Thread-safe token store operations
- **Usage**: `threading.Lock` for concurrent access protection
- **Location**: `src/logminer_qa/token_store.py`

---

## Python Standard Library

### Core Modules
- **`dataclasses`** - Configuration classes, data structures
- **`typing`** - Type hints and annotations
- **`pathlib`** - File path operations
- **`json`** - JSON serialization/deserialization
- **`csv`** - CSV file parsing
- **`logging`** - Application logging
- **`argparse`** - CLI argument parsing
- **`collections`** - Counter, defaultdict for aggregations
- **`itertools`** - chain, batch utilities
- **`re`** - Regular expressions
- **`math`** - Mathematical functions (Laplace noise)
- **`random`** - Random number generation
- **`statistics`** - Statistical functions (mean, etc.)
- **`threading`** - Thread synchronization
- **`hashlib`** - Cryptographic hashing
- **`abc`** - Abstract base classes (connector pattern)
- **`datetime`** - Date/time handling
- **`os`** - Environment variable access

---

## Development & Deployment Tools

### Virtual Environment
- **Tool**: Python `venv` module
- **Usage**: `python -m venv .venv`
- **Purpose**: Dependency isolation

### Package Management
- **Tool**: `pip`
- **File**: `requirements.txt`
- **Installation**: `pip install -r requirements.txt`

### Code Quality (Recommended)
- **Type Checking**: Python type hints throughout
- **Linting**: Compatible with pylint, flake8, mypy
- **Formatting**: Compatible with black, autopep8

### Deployment Options
- **Container**: Docker (recommended)
- **Orchestration**: Kubernetes, Docker Compose
- **Service Mesh**: Compatible with Istio, Linkerd
- **Secrets**: Vault, Kubernetes Secrets, Azure Key Vault

---

## External Services & Connectors

### Log Ingestion Sources

#### Elasticsearch/ELK Stack
- **Connector**: `ElasticsearchConnector`
- **Library**: `requests`
- **Location**: `src/logminer_qa/connectors/elk.py`
- **Features**: Query-based log retrieval, batch processing

#### Datadog
- **Connector**: `DatadogConnector`
- **Library**: `requests`
- **Location**: `src/logminer_qa/connectors/datadog.py`
- **Features**: API key authentication, query-based retrieval

#### Local Files
- **Formats**: 
  - JSONL (newline-delimited JSON)
  - CSV (with DictReader)
  - JSON (full file)
  - Plain text (fallback)
- **Location**: `src/logminer_qa/cli.py`, `src/logminer_qa/connectors/local.py`

---

## Recommended Tools

### Optional but Recommended

#### spaCy
- **Installation**: `pip install spacy && python -m spacy download en_core_web_sm`
- **Benefit**: Enhanced PII detection via Named Entity Recognition
- **Fallback**: System works without it (regex-only mode)

#### tf-keras
- **Installation**: `pip install tf-keras`
- **Benefit**: Compatibility shim for Keras 3 with sentence-transformers
- **When Needed**: If you encounter Keras 3 compatibility warnings

#### GPU Support (Optional)
- **TensorFlow GPU**: Replace `tensorflow-cpu` with `tensorflow` for GPU acceleration
- **PyTorch**: Automatically used by sentence-transformers if available
- **Benefit**: Faster embedding and LSTM training (10-100x speedup)

### Development Tools

#### Testing
- **pytest** - Unit and integration testing
- **pytest-cov** - Code coverage
- **pytest-mock** - Mocking support

#### Documentation
- **Sphinx** - API documentation generation
- **MkDocs** - User documentation
- **Markdown** - Documentation format

#### CI/CD
- **GitHub Actions** - Automation (example compatible)
- **Jenkins** - Build automation
- **GitLab CI** - Pipeline automation

---

## Technology Stack Summary

### By Category

| Category | Technologies |
|----------|-------------|
| **Language** | Python 3.11+ |
| **ML Framework** | TensorFlow/Keras, scikit-learn |
| **NLP** | spaCy (optional), sentence-transformers, regex |
| **API** | FastAPI, Uvicorn |
| **HTTP Client** | requests |
| **Data Processing** | NumPy, Pydantic |
| **Security** | hashlib (SHA-256, BLAKE2b), threading |
| **Progress Tracking** | tqdm |
| **Storage** | JSON files, CSV files, in-memory structures |

### By Use Case

| Use Case | Technology |
|----------|-----------|
| **Log Ingestion** | requests, csv, json, pathlib |
| **PII Detection** | regex, spaCy, hashlib |
| **Text Embeddings** | sentence-transformers, PyTorch |
| **Clustering** | scikit-learn (TF-IDF + KMeans) |
| **Anomaly Detection** | scikit-learn (IsolationForest) |
| **Sequence Modeling** | TensorFlow/Keras (LSTM) |
| **API Server** | FastAPI, Uvicorn |
| **Data Validation** | Pydantic, custom validators |
| **Progress Tracking** | tqdm |

---

## Version Compatibility Matrix

| Package | Minimum Version | Tested Version | Notes |
|---------|----------------|----------------|-------|
| Python | 3.8 | 3.11+ | Type hints require 3.8+ |
| requests | 2.32.0 | Latest | HTTP client |
| scikit-learn | 1.5.0 | Latest | ML algorithms |
| sentence-transformers | 3.0.0 | Latest | Embeddings |
| tensorflow-cpu | 2.17.0 | Latest | LSTM models |
| fastapi | 0.115.0 | Latest | API framework |
| uvicorn | 0.30.0 | Latest | ASGI server |
| tqdm | 4.66.0 | Latest | Progress bars |
| spaCy | 3.8.0+ | Latest | Optional NLP |

---

## Dependency Tree

```
LogMiner-QA
├── requests (HTTP client)
│   └── certifi, urllib3, idna, charset-normalizer
├── scikit-learn (ML algorithms)
│   ├── numpy
│   ├── scipy
│   └── joblib
├── sentence-transformers (Embeddings)
│   ├── torch (PyTorch)
│   ├── transformers (Hugging Face)
│   ├── numpy
│   └── sentencepiece
├── tensorflow-cpu (Deep Learning)
│   ├── numpy
│   ├── keras (included)
│   └── tensorflow-estimator
├── fastapi (API framework)
│   ├── pydantic
│   ├── starlette
│   └── typing-extensions
├── uvicorn (ASGI server)
│   ├── h11, httptools
│   └── uvloop (optional, Unix only)
└── tqdm (Progress bars)
    └── colorama (Windows)
```

---

## Installation Notes

### Minimum Installation
```bash
pip install -r requirements.txt
```

### Recommended Installation (with NLP)
```bash
pip install -r requirements.txt
pip install spacy
python -m spacy download en_core_web_sm
pip install tf-keras  # For Keras 3 compatibility
```

### GPU-Accelerated Installation
```bash
# Replace tensorflow-cpu with tensorflow
pip install tensorflow>=2.17.0
pip install -r requirements.txt
# ... rest of installation
```

---

## License Summary

| Package | License |
|---------|---------|
| requests | Apache 2.0 |
| scikit-learn | BSD 3-Clause |
| sentence-transformers | Apache 2.0 |
| tensorflow-cpu | Apache 2.0 |
| fastapi | MIT |
| uvicorn | BSD |
| tqdm | MIT/Mozilla Public License 2.0 |
| spaCy | MIT |
| Python Standard Library | Python Software Foundation License |

---

## Performance Considerations

### Memory Usage
- **TensorFlow/Keras**: ~200-500MB (model loading)
- **sentence-transformers**: ~200MB (model weights)
- **NumPy/scikit-learn**: ~100-300MB (depends on dataset size)
- **Total**: ~500MB-1GB baseline, + ~50MB per 10K records

### Processing Speed
- **CPU Mode**: ~5-12 minutes for 20K records
- **GPU Mode**: ~1-3 minutes for 20K records (with GPU)
- **Embeddings**: Bottleneck (15-45 min CPU, 2-5 min GPU)
- **Clustering**: ~2-5 minutes for 20K records

### Scalability
- **Current**: Tested up to 500K+ records
- **Limits**: Memory-bound (optimized with streaming)
- **Recommendation**: Use chunked processing for 100K+ records

---

## Security Considerations

### Cryptography
- Uses Python's built-in `hashlib` (industry standard)
- SHA-256 and BLAKE2b are cryptographically secure
- Secret key must be managed securely (`LOGMINER_HASH_SECRET`)

### Dependencies
- All dependencies are from PyPI (trusted source)
- Regular security updates recommended
- No known critical vulnerabilities in current versions

### Network
- `requests` library (well-maintained, widely used)
- All connections are outbound (no inbound listening except API)
- TLS/SSL support via `requests` for secure connections

---

## References & Documentation

- [Python Official Docs](https://docs.python.org/3/)
- [scikit-learn Documentation](https://scikit-learn.org/stable/)
- [TensorFlow Documentation](https://www.tensorflow.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [sentence-transformers Documentation](https://www.sbert.net/)
- [spaCy Documentation](https://spacy.io/)

---

**Last Updated**: 2025-11-18  
**Maintained By**: LogMiner-QA Team

