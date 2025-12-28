# Changelog

All notable changes to LogMiner-QA will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of LogMiner-QA
- PII detection and sanitization with regex patterns and optional spaCy NER
- Secret-based hashing for referential integrity
- Differential privacy layer with Laplace mechanism
- Log parsing with regex and NLP entity extraction
- Event clustering using TF-IDF and MiniBatch KMeans
- Transformer-based embeddings (sentence-transformers)
- Anomaly detection with Isolation Forest
- LSTM-based journey sequence modeling
- Compliance engine (PCI DSS, GDPR, audit trail checks)
- Fraud detection engine (velocity, high-value, login failures)
- Test generation with Gherkin format
- CLI interface with streaming support
- FastAPI server for programmatic access
- CI/CD summary generation
- Connectors for Elasticsearch, Datadog, and local files (JSONL, CSV, JSON)
- Input validation and security checks
- Batch token persistence for performance
- Progress tracking for large datasets
- Comprehensive documentation (README, WORKFLOW, TECH_STACK, DEPLOYMENT)

### Performance
- Streaming/chunked processing for memory efficiency
- Batch token store writes (100 tokens per write)
- Progress bars for embedding operations
- Optimized clustering for large datasets

### Security
- Input validation with size and nesting depth limits
- Secure secret management via environment variables
- On-premise deployment design
- Privacy-preserving analytics with differential privacy

## [0.1.0] - 2025-11-18

### Initial Release
- First public release for early adopters
- Core functionality complete and tested
- Documentation suite included
- Ready for community feedback

