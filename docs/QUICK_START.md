# Quick Start Guide

Get LogMiner-QA running in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- pip package manager
- 2GB+ free disk space (for models and dependencies)
- Optional: spaCy for enhanced PII detection

## Step 1: Install Dependencies

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install core dependencies
pip install -r requirements.txt

# Optional: Enhanced PII detection
pip install spacy
python -m spacy download en_core_web_sm

# Optional: Keras 3 compatibility (if you see warnings)
pip install tf-keras
```

## Step 2: Set Security Secret

Generate a secure secret for hashing:

**Windows PowerShell:**
```powershell
$bytes = New-Object byte[] 32
$rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
try { $rng.GetBytes($bytes) } finally { $rng.Dispose() }
$env:LOGMINER_HASH_SECRET = ([System.BitConverter]::ToString($bytes)).Replace('-','')
```

**Linux/Mac:**
```bash
export LOGMINER_HASH_SECRET=$(openssl rand -hex 32)
```

**Windows CMD:**
```cmd
# Generate using Python
python -c "import secrets; print(secrets.token_hex(32))"
# Then set: set LOGMINER_HASH_SECRET=<generated_value>
```

## Step 3: Run Your First Analysis

### Option A: Use Sample Data

```bash
python -m logminer_qa.cli \
  --input data/sample_logs.jsonl \
  --output sanitized.jsonl \
  --report report.json \
  --tests generated_tests.feature
```

### Option B: Use Your Own CSV/JSONL

```bash
python -m logminer_qa.cli \
  --input your_logs.csv \
  --output sanitized.jsonl \
  --report analytics.json \
  --tests my_tests.feature
```

## Step 4: Review Results

Check the generated files:

1. **sanitized.jsonl**: PII-free logs with analysis metadata
   ```bash
   head -n 1 sanitized.jsonl | python -m json.tool
   ```

2. **report.json**: Analytics summary
   - Frequency counts (with differential privacy)
   - Event clusters
   - Anomaly scores
   - Compliance/fraud findings

3. **generated_tests.feature**: Gherkin test scenarios
   ```bash
   head -n 20 generated_tests.feature
   ```

## Common Commands

### Basic Analysis
```bash
python -m logminer_qa.cli --input logs.csv --output out.jsonl --report report.json
```

### With Test Generation
```bash
python -m logminer_qa.cli \
  --input logs.csv \
  --output out.jsonl \
  --report report.json \
  --tests tests.feature
```

### CI/CD Mode
```bash
python -m logminer_qa.cli \
  --input logs.csv \
  --ci-summary build/summary.json
```

### API Server Mode
```bash
# Terminal 1: Start server
uvicorn logminer_qa.server:create_app --factory --host 0.0.0.0 --port 8080

# Terminal 2: Send request
curl -X POST http://localhost:8080/analyze \
  -H "Content-Type: application/json" \
  -d '{"records": [{"event": "login", "user": "test@example.com"}]}'
```

## Next Steps

- Read [Early Adopter Guide](EARLY_ADOPTER_GUIDE.md) for detailed usage
- Check [Workflow Diagram](WORKFLOW.md) to understand the pipeline
- Review [Tech Stack](TECH_STACK.md) for technical details
- See [Deployment Guide](DEPLOYMENT.md) for production setup

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| Hash secret warning | Set `LOGMINER_HASH_SECRET` environment variable |
| Keras 3 warning | Run `pip install tf-keras` |
| Memory errors | Reduce dataset size or enable streaming (default) |
| Slow processing | Normal for large datasets. Embeddings take 15-45 min for 20K records. |

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/77QAlab/LogMiner-QA/issues)
- **Documentation**: Check `docs/` folder
- **Questions**: Open an issue with `question` label

Happy analyzing! 

