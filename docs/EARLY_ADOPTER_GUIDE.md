# Early Adopter Guide

Welcome, early adopter! Thank you for trying LogMiner-QA. This guide will help you get started quickly and provide feedback.

## What is LogMiner-QA?

LogMiner-QA is a privacy-first tool that:
- **Sanitizes** production logs by detecting and removing PII
- **Analyzes** logs using ML/NLP to extract insights
- **Generates** automated test cases from real user journeys
- **Runs entirely on-premise** - your data never leaves your infrastructure

## Quick Start (5 Minutes)

### 1. Installation

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Optional: Install spaCy for enhanced PII detection
pip install spacy
python -m spacy download en_core_web_sm

# Optional: Install tf-keras for Keras 3 compatibility
pip install tf-keras
```

### 2. Set Up Security Secret

```bash
# Generate a secure secret (PowerShell)
$bytes = New-Object byte[] 32
$rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
try { $rng.GetBytes($bytes) } finally { $rng.Dispose() }
$env:LOGMINER_HASH_SECRET = ([System.BitConverter]::ToString($bytes)).Replace('-','')

# Or on Linux/Mac:
export LOGMINER_HASH_SECRET=$(openssl rand -hex 32)
```

### 3. Run Your First Analysis

```bash
# Basic usage with sample data
python -m logminer_qa.cli \
  --input data/sample_logs.jsonl \
  --output sanitized.jsonl \
  --report report.json \
  --tests generated_tests.feature
```

### 4. Check the Results

- **sanitized.jsonl**: PII-free logs with analysis metadata
- **report.json**: Analytics summary (clustering, anomalies, compliance findings)
- **generated_tests.feature**: Gherkin test scenarios

## Common Use Cases

### Use Case 1: Analyze CSV Logs

```bash
python -m logminer_qa.cli \
  --input your_logs.csv \
  --output sanitized.jsonl \
  --report analytics.json \
  --tests test_cases.feature
```

### Use Case 2: Connect to Elasticsearch

1. Create `connectors.json`:
```json
{
  "elk": {
    "endpoint": "https://your-elasticsearch:9200",
    "index": "logs-*",
    "query": {"query": {"match": {"level": "ERROR"}}}
  }
}
```

2. Run with connector:
```bash
python -m logminer_qa.cli \
  --connectors-config connectors.json \
  --output sanitized.jsonl \
  --report report.json
```

### Use Case 3: API Server Mode

```bash
# Start API server
uvicorn logminer_qa.server:create_app --factory --host 0.0.0.0 --port 8080

# In another terminal, send logs
curl -X POST http://localhost:8080/analyze \
  -H "Content-Type: application/json" \
  -d '{"records": [{"event": "login", "user": "test@example.com"}]}'
```

### Use Case 4: CI/CD Integration

```bash
python -m logminer_qa.cli \
  --input logs/production.jsonl \
  --ci-summary build/logminer-summary.json

# Check summary and fail build if needed
python check_thresholds.py build/logminer-summary.json
```

## What We're Looking For

### Feedback Priorities

1. **Usability**
   - Is the CLI intuitive?
   - Are error messages helpful?
   - Is documentation clear?

2. **Performance**
   - How long does processing take?
   - Memory usage acceptable?
   - Any bottlenecks you notice?

3. **Features**
   - What's missing?
   - What would make this more useful?
   - Any edge cases not handled?

4. **Security**
   - Concerns about data handling?
   - Suggestions for improvements?
   - Compliance requirements?

5. **Integration**
   - What tools do you want to integrate with?
   - CI/CD platform preferences?
   - Log sources you need?

### How to Provide Feedback

1. **GitHub Issues**: Report bugs or request features
   - Use labels: `bug`, `enhancement`, `question`
   - Include reproduction steps

2. **Email/Direct Contact**: For sensitive feedback or enterprise inquiries

3. **Discussions**: Share use cases and experiences (GitHub Discussions)

4. **Surveys**: We'll send periodic surveys to early adopters

## Known Limitations

### Current Constraints

- **Large Datasets**: Processing >100K records may take 30+ minutes (CPU mode)
- **Memory**: Requires 500MB-2GB RAM depending on dataset size
- **GPU Support**: Not yet optimized for GPU (CPU mode works well)
- **Journey LSTM**: Requires 50+ unique journey sequences to train
- **Connectors**: Limited to Elasticsearch, Datadog, local files (more coming)

### Workarounds

- Use chunked processing for large files (automatic)
- Install spaCy for better PII detection
- Use smaller samples for initial testing
- Run API server for incremental processing

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'spacy'`
- **Solution**: Install spaCy (optional, but recommended)
- **Impact**: Reduced PII detection accuracy

**Issue**: `Hashing secret environment variable 'LOGMINER_HASH_SECRET' not set`
- **Solution**: Set environment variable (see step 2 above)
- **Impact**: Uses default (less secure, warns)

**Issue**: `sentence-transformers unavailable: Keras 3`
- **Solution**: `pip install tf-keras`
- **Impact**: Embeddings/anomaly detection won't work

**Issue**: Processing is slow
- **Solution**: Normal for large datasets. Use progress logs to monitor.
- **Tip**: Embeddings are the bottleneck (can take 15-45 min for 20K records)

**Issue**: Memory errors
- **Solution**: Enable streaming (default). Reduce chunk_size in config if needed.
- **Tip**: Process in smaller batches

## Next Steps

1. **Try the examples** in `docs/EXAMPLES.md` (coming soon)
2. **Read the workflow** in `docs/WORKFLOW.md` to understand the pipeline
3. **Review tech stack** in `docs/TECH_STACK.md` for technical details
4. **Check deployment** guide in `docs/DEPLOYMENT.md` for production setup
5. **Share your experience** via GitHub Issues or direct contact

## Support

- **Documentation**: Check `docs/` folder
- **Issues**: GitHub Issues (preferred for bugs/features)
- **Questions**: GitHub Discussions or open an issue with `question` label
- **Security**: Report security issues privately (don't use public issues)

## Thank You!

Your feedback and adoption help make LogMiner-QA better. We're committed to:
- Responding to issues within 48 hours
- Prioritizing early adopter feature requests
- Regular updates based on your feedback
- Building a supportive community

Welcome to the LogMiner-QA community! 🚀

