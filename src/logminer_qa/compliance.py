"""
Banking compliance and fraud-specific analysis utilities.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Iterable, List, Sequence


ACCOUNT_PATTERN = re.compile(r"\b\d{12,18}\b")
VELOCITY_WINDOW = timedelta(minutes=10)


@dataclass(slots=True)
class ComplianceFinding:
    rule: str
    severity: str
    description: str
    evidence: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, object]:
        return {
            "rule": self.rule,
            "severity": self.severity,
            "description": self.description,
            "evidence": self.evidence,
        }


@dataclass(slots=True)
class FraudFinding:
    category: str
    severity: str
    description: str
    accounts: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, object]:
        return {
            "category": self.category,
            "severity": self.severity,
            "description": self.description,
            "accounts": self.accounts,
            "metrics": self.metrics,
        }


def _extract_timestamp(record: Dict[str, object]) -> datetime | None:
    timestamp = record.get("timestamp")
    if not isinstance(timestamp, str):
        return None
    try:
        if timestamp.endswith("Z"):
            timestamp = timestamp[:-1]
        return datetime.fromisoformat(timestamp)
    except ValueError:
        return None


class BankingComplianceEngine:
    """
    Performs lightweight compliance validations on sanitized banking logs.
    """

    def evaluate(self, records: Sequence[Dict[str, object]]) -> List[ComplianceFinding]:
        findings: List[ComplianceFinding] = []
        audit_failures: List[str] = []
        pci_issues: List[str] = []
        gdpr_gaps: List[str] = []

        for record in records:
            analysis = record.get("analysis", {}) if isinstance(record, dict) else {}
            label = analysis.get("event_label")
            hashed_fields = record.get("hashed_fields") if isinstance(record, dict) else {}
            timestamp = record.get("timestamp") if isinstance(record, dict) else None
            message = ""
            if isinstance(record, dict):
                message = str(record.get("message", ""))
            if isinstance(record, dict):
                for value in record.values():
                    if isinstance(value, str):
                        message += f" {value}"

            if label == "transaction_event":
                if not timestamp or not hashed_fields:
                    audit_failures.append(
                        f"Transaction record missing timestamp or hashed_fields: {record.get('journey_id') or record.get('session_id')}"
                    )

            if ACCOUNT_PATTERN.search(message):
                pci_issues.append("Potential unmasked account number detected in sanitized payload.")

            if label == "generic_event" and "data access" in message.lower() and not hashed_fields:
                gdpr_gaps.append("Customer data access event missing hashed identifier.")

        if audit_failures:
            findings.append(
                ComplianceFinding(
                    rule="AuditTrailCompleteness",
                    severity="high",
                    description="Some transactions lack timestamp or hashed identifiers.",
                    evidence=audit_failures,
                )
            )
        if pci_issues:
            findings.append(
                ComplianceFinding(
                    rule="PCIAccountMasking",
                    severity="critical",
                    description="Detected possible card/account numbers that were not tokenized.",
                    evidence=pci_issues,
                )
            )
        if gdpr_gaps:
            findings.append(
                ComplianceFinding(
                    rule="GDPRAccessLogging",
                    severity="medium",
                    description="Customer data access events require hashed customer identifiers.",
                    evidence=gdpr_gaps,
                )
            )

        return findings

    def generate_tests(self, findings: Sequence[ComplianceFinding]) -> List[str]:
        scenarios: List[str] = []
        for finding in findings:
            evidence = "\n    ".join(f"- {item}" for item in finding.evidence[:5])
            scenario = (
                f"Feature: Compliance rule {finding.rule}\n"
                f"  Scenario: Validate {finding.rule} remediation\n"
                f"  Given sanitized banking logs with potential non-compliance\n"
                f"  When the compliance engine inspects the records\n"
                f"  Then it flags {finding.severity} severity for {finding.rule}\n"
            )
            if evidence:
                scenario += f"  And supporting evidence includes:\n    {evidence}\n"
            scenarios.append(scenario.strip())
        return scenarios


class FraudDetectionEngine:
    """
    Heuristic fraud pattern detection for sanitized logs.
    """

    def evaluate(
        self, records: Sequence[Dict[str, object]], parsed_records: Sequence[Dict[str, object]]
    ) -> List[FraudFinding]:
        findings: List[FraudFinding] = []
        account_events: Dict[str, List[datetime]] = {}
        high_value_accounts: Dict[str, float] = {}
        login_failures: Dict[str, int] = {}

        for record, parsed in zip(records, parsed_records):
            if not isinstance(record, dict):
                continue
            hashed_fields = record.get("hashed_fields") or {}
            analysis = record.get("analysis", {})
            label = analysis.get("event_label")
            timestamp = _extract_timestamp(record)
            amount_values = self._parse_amounts(parsed)
            accounts = self._extract_accounts(parsed, hashed_fields)
            message = str(record.get("message", "")).lower()

            for account in accounts:
                if timestamp:
                    account_events.setdefault(account, []).append(timestamp)
                total_amount = sum(amount_values)
                if total_amount > 5000:
                    high_value_accounts[account] = max(high_value_accounts.get(account, 0.0), total_amount)

            if label == "login_event" and ("failed" in message or "denied" in message):
                for account in accounts or hashed_fields.values():
                    login_failures[account] = login_failures.get(account, 0) + 1

        velocity_accounts = [
            account for account, events in account_events.items() if self._exceeds_velocity(events)
        ]
        if velocity_accounts:
            findings.append(
                FraudFinding(
                    category="VelocityCheck",
                    severity="high",
                    description="Account shows unusually high transaction velocity within 10 minute window.",
                    accounts=velocity_accounts,
                    metrics={"account_count": float(len(velocity_accounts))},
                )
            )

        if high_value_accounts:
            findings.append(
                FraudFinding(
                    category="HighValueTransfers",
                    severity="medium",
                    description="Transactions exceeding $5000 detected.",
                    accounts=list(high_value_accounts.keys()),
                    metrics=high_value_accounts,
                )
            )

        suspect_accounts = [account for account, count in login_failures.items() if count >= 3]
        if suspect_accounts:
            findings.append(
                FraudFinding(
                    category="FailedLoginVelocity",
                    severity="medium",
                    description="Multiple failed logins detected for the same account.",
                    accounts=suspect_accounts,
                    metrics={account: float(login_failures[account]) for account in suspect_accounts},
                )
            )

        return findings

    def generate_tests(self, findings: Sequence[FraudFinding]) -> List[str]:
        scenarios: List[str] = []
        for finding in findings:
            accounts = ", ".join(finding.accounts[:5])
            scenario = (
                f"Feature: Fraud pattern {finding.category}\n"
                f"  Scenario: Detect {finding.category}\n"
                f"  Given sanitized banking activity logs\n"
                f"  When the fraud detection module analyses account behaviour\n"
                f"  Then it classifies the pattern as {finding.severity} severity\n"
            )
            if accounts:
                scenario += f"  And affected accounts include {accounts}\n"
            scenarios.append(scenario.strip())
        return scenarios

    @staticmethod
    def _parse_amounts(parsed: Dict[str, object]) -> List[float]:
        results: List[float] = []
        for value in parsed.get("monetary_values", []):
            try:
                results.append(float(value.replace(",", "")))
            except (ValueError, AttributeError):
                continue
        return results

    @staticmethod
    def _extract_accounts(parsed: Dict[str, object], hashed_fields: Dict[str, str]) -> List[str]:
        tokens = parsed.get("account_tokens", []) if isinstance(parsed, dict) else []
        if hashed_fields:
            tokens.extend(str(value) for value in hashed_fields.values())
        return list({token for token in tokens if token})

    @staticmethod
    def _exceeds_velocity(events: Iterable[datetime]) -> bool:
        ordered = sorted(timestamp for timestamp in events if timestamp)
        for idx in range(len(ordered) - 3):
            if ordered[idx + 3] - ordered[idx] <= VELOCITY_WINDOW:
                return True
        return False

