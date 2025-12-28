import random
import datetime
import json
from typing import List, Dict

class BankingLogGenerator:
    """Generate realistic banking teller transaction logs for LSTM training"""
    
    def __init__(self):
        self.transaction_types = [
            "DEPOSIT", "WITHDRAWAL", "BALANCE_INQUIRY", "TRANSFER",
            "LOAN_PAYMENT", "CHECK_CASHING", "ACCOUNT_OPENING",
            "ACCOUNT_CLOSURE", "CARD_ISSUE", "STATEMENT_REQUEST"
        ]
        
        self.event_sequences = {
            "DEPOSIT": [
                "SESSION_START", "TELLER_LOGIN", "CUSTOMER_VERIFY", "ACCOUNT_LOOKUP",
                "DEPOSIT_INIT", "CASH_COUNT", "AMOUNT_VERIFY", "DENOMINATION_CHECK",
                "TRANSACTION_VALIDATE", "BALANCE_UPDATE", "RECEIPT_PRINT", "SESSION_END"
            ],
            "WITHDRAWAL": [
                "SESSION_START", "TELLER_LOGIN", "CUSTOMER_VERIFY", "ID_CHECK",
                "ACCOUNT_LOOKUP", "BALANCE_CHECK", "WITHDRAWAL_INIT", "AMOUNT_VERIFY",
                "FUNDS_AVAILABILITY", "CASH_DISPENSE", "VAULT_ACCESS", "DENOMINATION_SELECT",
                "BALANCE_UPDATE", "RECEIPT_PRINT", "SESSION_END"
            ],
            "BALANCE_INQUIRY": [
                "SESSION_START", "TELLER_LOGIN", "CUSTOMER_VERIFY", "ACCOUNT_LOOKUP",
                "BALANCE_RETRIEVE", "HOLD_CHECK", "AVAILABLE_BALANCE_CALC", 
                "STATEMENT_GENERATE", "SESSION_END"
            ],
            "TRANSFER": [
                "SESSION_START", "TELLER_LOGIN", "CUSTOMER_VERIFY", "ACCOUNT_LOOKUP",
                "SOURCE_ACCOUNT_VERIFY", "DEST_ACCOUNT_LOOKUP", "DEST_ACCOUNT_VERIFY",
                "TRANSFER_INIT", "AMOUNT_VERIFY", "BALANCE_CHECK", "TRANSFER_VALIDATE",
                "SOURCE_DEBIT", "DEST_CREDIT", "TRANSFER_CONFIRM", "RECEIPT_PRINT", "SESSION_END"
            ],
            "LOAN_PAYMENT": [
                "SESSION_START", "TELLER_LOGIN", "CUSTOMER_VERIFY", "ACCOUNT_LOOKUP",
                "LOAN_ACCOUNT_LOOKUP", "PAYMENT_AMOUNT_CHECK", "PRINCIPAL_CALC",
                "INTEREST_CALC", "PAYMENT_APPLY", "LOAN_BALANCE_UPDATE", "PAYMENT_CONFIRM",
                "RECEIPT_PRINT", "SESSION_END"
            ],
            "CHECK_CASHING": [
                "SESSION_START", "TELLER_LOGIN", "CUSTOMER_VERIFY", "ID_CHECK",
                "CHECK_INSPECT", "CHECK_ENDORSEMENT_VERIFY", "ACCOUNT_LOOKUP",
                "FUNDS_VERIFY", "HOLD_CHECK", "CHECK_AMOUNT_VERIFY", "CASH_DISPENSE",
                "VAULT_ACCESS", "CHECK_SCAN", "CHECK_STORE", "RECEIPT_PRINT", "SESSION_END"
            ],
            "ACCOUNT_OPENING": [
                "SESSION_START", "TELLER_LOGIN", "CUSTOMER_VERIFY", "ID_VERIFY",
                "SSN_VERIFY", "ADDRESS_VERIFY", "KYC_CHECK", "CREDIT_CHECK",
                "ACCOUNT_TYPE_SELECT", "INITIAL_DEPOSIT_CHECK", "ACCOUNT_CREATE",
                "ACCOUNT_NUMBER_GENERATE", "CARD_ORDER", "DOCUMENTS_PRINT",
                "SIGNATURE_CAPTURE", "ACCOUNT_ACTIVATE", "SESSION_END"
            ],
            "ACCOUNT_CLOSURE": [
                "SESSION_START", "TELLER_LOGIN", "CUSTOMER_VERIFY", "ID_CHECK",
                "ACCOUNT_LOOKUP", "BALANCE_CHECK", "PENDING_TRANSACTION_CHECK",
                "HOLD_CHECK", "CLOSURE_REASON_CAPTURE", "FINAL_BALANCE_CALC",
                "CASH_DISPENSE", "ACCOUNT_DEACTIVATE", "CLOSURE_CONFIRM",
                "DOCUMENTS_PRINT", "SESSION_END"
            ],
            "CARD_ISSUE": [
                "SESSION_START", "TELLER_LOGIN", "CUSTOMER_VERIFY", "ACCOUNT_LOOKUP",
                "CARD_TYPE_SELECT", "CARD_REQUEST_INIT", "FEE_CHECK", "FEE_COLLECT",
                "CARD_INVENTORY_CHECK", "CARD_ACTIVATE", "PIN_SET", "CARD_HANDOVER",
                "RECEIPT_PRINT", "SESSION_END"
            ],
            "STATEMENT_REQUEST": [
                "SESSION_START", "TELLER_LOGIN", "CUSTOMER_VERIFY", "ACCOUNT_LOOKUP",
                "DATE_RANGE_SELECT", "STATEMENT_GENERATE", "TRANSACTION_RETRIEVE",
                "STATEMENT_FORMAT", "STATEMENT_PRINT", "FEE_CHECK", "SESSION_END"
            ]
        }
        
        # Anomalous sequences for testing
        self.anomalies = {
            "MISSING_AUTH": ["SESSION_START", "ACCOUNT_LOOKUP", "CASH_DISPENSE"],
            "VAULT_WITHOUT_VERIFY": ["SESSION_START", "TELLER_LOGIN", "VAULT_ACCESS"],
            "DOUBLE_DEBIT": ["SESSION_START", "TELLER_LOGIN", "CUSTOMER_VERIFY", 
                            "ACCOUNT_LOOKUP", "BALANCE_CHECK", "SOURCE_DEBIT", "SOURCE_DEBIT"],
            "SKIP_VERIFICATION": ["SESSION_START", "TELLER_LOGIN", "WITHDRAWAL_INIT", 
                                 "CASH_DISPENSE", "SESSION_END"],
            "UNAUTHORIZED_ACCESS": ["SESSION_START", "ACCOUNT_LOOKUP", "BALANCE_UPDATE", 
                                   "SESSION_END"]
        }
        
        self.tellers = [f"TELLER_{i:03d}" for i in range(1, 26)]
        self.branches = [f"BR_{i:04d}" for i in range(100, 120)]
        
    def generate_timestamp(self, base_time: datetime.datetime) -> str:
        """Generate realistic timestamp with microseconds"""
        return base_time.strftime("%Y-%m-%d %H:%M:%S.%f")
    
    def generate_transaction_log(self, trans_type: str, trans_id: str, 
                                 base_time: datetime.datetime, 
                                 is_anomaly: bool = False) -> List[Dict]:
        """Generate complete transaction log with all events"""
        logs = []
        
        if is_anomaly and random.random() < 0.3:
            # Inject anomalous sequence
            anomaly_type = random.choice(list(self.anomalies.keys()))
            events = self.anomalies[anomaly_type]
            severity = "CRITICAL"
        else:
            events = self.event_sequences[trans_type].copy()
            severity = "INFO"
            
            # Occasionally add variations to normal flows
            if random.random() < 0.15:
                if "BALANCE_CHECK" in events:
                    idx = events.index("BALANCE_CHECK")
                    events.insert(idx + 1, "OVERDRAFT_CHECK")
            
            if random.random() < 0.1 and "AMOUNT_VERIFY" in events:
                idx = events.index("AMOUNT_VERIFY")
                events.insert(idx + 1, "AMOUNT_RECOUNT")
        
        teller = random.choice(self.tellers)
        branch = random.choice(self.branches)
        customer_id = f"CUST_{random.randint(100000, 999999)}"
        account_num = f"{random.randint(1000000000, 9999999999)}"
        
        current_time = base_time
        
        for event in events:
            # Add realistic time delays between events
            delay = random.uniform(0.5, 3.5)
            current_time += datetime.timedelta(seconds=delay)
            
            log_entry = {
                "timestamp": self.generate_timestamp(current_time),
                "transaction_id": trans_id,
                "transaction_type": trans_type,
                "event": event,
                "teller_id": teller,
                "branch_id": branch,
                "customer_id": customer_id,
                "account_number": account_num,
                "severity": severity if event in ["SESSION_START", "TELLER_LOGIN", 
                                                   "CUSTOMER_VERIFY"] else "INFO",
                "status": "SUCCESS" if random.random() > 0.02 else "WARNING",
                "amount": f"{random.uniform(10.00, 50000.00):.2f}" if "AMOUNT" in event or 
                         "DEPOSIT" in event or "WITHDRAWAL" in event else None,
                "balance_before": f"{random.uniform(100.00, 100000.00):.2f}" if 
                                 "BALANCE" in event else None,
                "balance_after": None,
                "metadata": {
                    "terminal_id": f"TERM_{random.randint(1, 50):03d}",
                    "session_id": f"SES_{random.randint(100000, 999999)}",
                    "ip_address": f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
                }
            }
            
            # Calculate balance_after for balance updates
            if log_entry["balance_before"] and "UPDATE" in event:
                if log_entry["amount"]:
                    before = float(log_entry["balance_before"])
                    amount = float(log_entry["amount"])
                    if "DEBIT" in event or "WITHDRAWAL" in event:
                        log_entry["balance_after"] = f"{before - amount:.2f}"
                    else:
                        log_entry["balance_after"] = f"{before + amount:.2f}"
            
            logs.append(log_entry)
        
        return logs
    
    def generate_dataset(self, num_transactions: int = 1000, 
                        anomaly_rate: float = 0.05) -> List[Dict]:
        """Generate complete dataset of banking logs"""
        all_logs = []
        base_date = datetime.datetime(2024, 1, 1, 9, 0, 0)
        
        for i in range(num_transactions):
            # Vary time throughout business days
            day_offset = i // 50  # ~50 transactions per day
            time_offset = (i % 50) * random.uniform(5, 15)  # Minutes between transactions
            
            trans_time = base_date + datetime.timedelta(days=day_offset, minutes=time_offset)
            
            # Skip weekends
            if trans_time.weekday() >= 5:
                trans_time += datetime.timedelta(days=2)
            
            trans_type = random.choice(self.transaction_types)
            trans_id = f"TXN_{trans_time.strftime('%Y%m%d')}_{i:06d}"
            
            is_anomaly = random.random() < anomaly_rate
            
            transaction_logs = self.generate_transaction_log(
                trans_type, trans_id, trans_time, is_anomaly
            )
            
            all_logs.extend(transaction_logs)
        
        return all_logs
    
    def export_logs(self, logs: List[Dict], filename: str = "banking_teller_logs.json"):
        """Export logs to JSON file"""
        with open(filename, 'w') as f:
            json.dump(logs, f, indent=2)
        print(f"Generated {len(logs)} log entries across multiple transactions")
        print(f"Exported to {filename}")
    
    def export_csv(self, logs: List[Dict], filename: str = "banking_teller_logs.csv"):
        """Export logs to CSV format"""
        import csv
        
        if not logs:
            return
        
        # First pass: collect all possible fieldnames including flattened metadata
        all_fieldnames = set()
        flattened_logs = []
        for log in logs:
            log_copy = log.copy()
            if 'metadata' in log_copy:
                for k, v in log_copy['metadata'].items():
                    log_copy[f'metadata_{k}'] = v
                    all_fieldnames.add(f'metadata_{k}')
                del log_copy['metadata']
            all_fieldnames.update(log_copy.keys())
            flattened_logs.append(log_copy)
        
        # Sort fieldnames for consistent column order (metadata fields at end)
        fieldnames = sorted([f for f in all_fieldnames if not f.startswith('metadata_')])
        fieldnames.extend(sorted([f for f in all_fieldnames if f.startswith('metadata_')]))
        
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(flattened_logs)
        
        print(f"Exported to {filename}")


# Generate the dataset
if __name__ == "__main__":
    generator = BankingLogGenerator()
    
    # Generate 1500 transactions with 5% anomaly rate
    logs = generator.generate_dataset(num_transactions=1500, anomaly_rate=0.05)
    
    # Export in both formats
    generator.export_logs(logs, "banking_teller_logs.json")
    generator.export_csv(logs, "banking_teller_logs.csv")
    
    # Print statistics
    transactions = set(log['transaction_id'] for log in logs)
    event_types = set(log['event'] for log in logs)
    
    print(f"\nDataset Statistics:")
    print(f"Total log entries: {len(logs)}")
    print(f"Unique transactions: {len(transactions)}")
    print(f"Unique event types: {len(event_types)}")
    print(f"Transaction types: {len(generator.transaction_types)}")
    print(f"Average events per transaction: {len(logs) / len(transactions):.2f}")
    
    print(f"\nEvent types included:")
    for event in sorted(event_types):
        print(f"  - {event}")