# Deployment & Differential Privacy Guide

This guide describes how to deploy LogMiner-QA inside a bank-controlled environment while preserving customer privacy.

## 1. Architecture Overview

1. **Sanitizer Container** ingests raw logs from ELK/Splunk/Kafka with only local network access.
2. **Analysis Engine Container** consumes sanitized events from the sanitizer over an internal message bus (NATS, RabbitMQ, or shared volume).
3. **Dashboard/API Container** (optional) hosts Streamlit/React and FastAPI endpoints. It only sees sanitized data and noisy aggregates.

Deploy all containers in the same Kubernetes namespace with explicit network policies:

- Allow ingress to the Sanitizer only from log sources.
- Only permit Sanitizer → Analysis egress.
- Block outbound traffic from all pods except to internal observability (Prometheus, Grafana).

## 2. Configuration Secrets

- Store LOGMINER_HASH_SECRET and any tokenizer salts in Vault/Key Vault. Inject via sealed secrets or CSI drivers.
- Mount the referential token store (/var/lib/logminer/tokens.json) on an encrypted PVC with restricted access.
- Keep model artefacts within the cluster (/models) and load them via init containers if necessary.

## 3. Container Build

Example Dockerfile snippet:

`dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ src/
ENV LOGMINER_HASH_SECRET=change-me
ENTRYPOINT ["python", "-m", "logminer_qa.cli"]
`

For air-gapped environments, build images on an internal registry, then deploy via Helm or Argo CD with the following values:

- sanitizer.resources tuned for NLP workloads (CPU 2 vCPU, RAM 4 GB).
- nalysis.resources sized for ML pipelines (CPU 4 vCPU, RAM 8 GB).
- 
odeSelector / 	olerations to isolate workloads on secure nodes.

## 4. Differential Privacy Controls

- Configure epsilon and delta in PrivacyConfig; defaults are ε=1.0, δ=1e-5.
- Track privacy budget consumption per dashboard query. Deny requests when the cumulative budget exceeds thresholds.
- Offer DP toggle per report for auditors; run DP-enabled reports by default.

## 5. CI/CD Integration

1. In Jenkins/GitHub Actions, run python -m logminer_qa.cli within the secure environment where logs reside.
2. Archive sanitized outputs and test cases only inside the bank’s artifact store.
3. Publish Gherkin tests to the existing QA suite (e.g., Cucumber, Pytest-BDD).

## 6. Observability & Auditing

- Expose Prometheus metrics (sanitized record count, DP epsilon usage, sanitizer latency).
- Ship logs to the bank’s SIEM with sanitization metadata only; never emit raw tokens.
- Set up audit jobs to compare raw ingestion vs sanitized outputs using synthetic data to ensure redaction fidelity.

## 7. Disaster Recovery

- Backup token stores and model artefacts using encrypted snapshots.
- Provide scripted redeployment via Helm to restore clusters within RTO objectives.
- Ensure DP noise is seeded via secure RNG (e.g., /dev/urandom guarded by kernel policies).

Following this guide keeps LogMiner-QA compliant with banking security requirements while delivering test insights derived from production behaviour.
