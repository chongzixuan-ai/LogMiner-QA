#!/usr/bin/env python3
"""
Installation Test Script for LogMiner-QA

This script verifies that the installation is working correctly.
Run this before distributing to early adopters.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all core modules can be imported."""
    print("Testing imports...")
    try:
        import logminer_qa
        print("  ✓ logminer_qa package")
        
        from logminer_qa.config import Settings, SanitizerConfig
        print("  ✓ config module")
        
        from logminer_qa.sanitizer import SanitizationLayer
        print("  ✓ sanitizer module")
        
        from logminer_qa.parsing import LogParser
        print("  ✓ parsing module")
        
        from logminer_qa.clustering import EventClusterer
        print("  ✓ clustering module")
        
        from logminer_qa.embeddings import EmbeddingService
        print("  ✓ embeddings module")
        
        from logminer_qa.anomaly import AnomalyDetector
        print("  ✓ anomaly module")
        
        from logminer_qa.journey import JourneyAnalyzer
        print("  ✓ journey module")
        
        from logminer_qa.compliance import BankingComplianceEngine
        print("  ✓ compliance module")
        
        from logminer_qa.pipeline import LogMinerPipeline
        print("  ✓ pipeline module")
        
        from logminer_qa.cli import load_records, main as cli_main
        print("  ✓ CLI module")
        
        return True
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality without requiring ML models."""
    print("\nTesting basic functionality...")
    try:
        from logminer_qa.config import Settings, SanitizerConfig
        from logminer_qa.sanitizer import SanitizationLayer
        from logminer_qa.parsing import LogParser
        
        # Create settings
        settings = Settings()
        print(f"  ✓ Settings created: chunk_size={settings.chunk_size}")
        
        # Create sanitizer
        config = SanitizerConfig(enable_ner=False)  # Skip spaCy for quick test
        sanitizer = SanitizationLayer(config)
        print("  ✓ Sanitizer created")
        
        # Test sanitization
        test_record = {
            "message": "User john.doe@example.com transferred $1000",
            "user": "john.doe@example.com"
        }
        result = sanitizer.sanitize_record(test_record)
        print(f"  ✓ Sanitization works: {len(result.redaction_map)} redactions")
        
        # Create parser
        parser = LogParser()
        print("  ✓ Parser created")
        
        # Test parsing
        parsed = parser.parse_record(result.sanitized)
        print(f"  ✓ Parsing works: found {len(parsed.account_tokens)} account tokens")
        
        return True
    except Exception as e:
        print(f"  ✗ Functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dependencies():
    """Check that critical dependencies are available."""
    print("\nTesting dependencies...")
    dependencies = {
        "numpy": "NumPy",
        "sklearn": "scikit-learn",
        "requests": "Requests",
        "tqdm": "tqdm",
    }
    
    all_ok = True
    for module, name in dependencies.items():
        try:
            __import__(module)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✗ {name} not installed")
            all_ok = False
    
    # Optional dependencies (test with error handling)
    optional = {
        "spacy": "spaCy (optional, for NER)",
        "sentence_transformers": "Sentence Transformers (optional, for embeddings)",
        "tensorflow": "TensorFlow (optional, for LSTM)",
        "fastapi": "FastAPI (optional, for API server)",
    }
    
    print("\n  Optional dependencies:")
    for module, name in optional.items():
        try:
            __import__(module)
            print(f"    ✓ {name}")
        except (ImportError, ValueError) as e:
            # ValueError can occur with tf-keras compatibility issues
            if "tf-keras" in str(e) or "Keras 3" in str(e):
                print(f"    ⊘ {name} (tf-keras needed: pip install tf-keras)")
            else:
                print(f"    ⊘ {name} (not installed, will use fallbacks)")
    
    return all_ok

def test_file_structure():
    """Verify essential files exist."""
    print("\nTesting file structure...")
    essential_files = [
        "README.md",
        "LICENSE",
        "requirements.txt",
        "src/logminer_qa/__init__.py",
        "src/logminer_qa/config.py",
        "src/logminer_qa/pipeline.py",
        "docs/QUICK_START.md",
    ]
    
    all_ok = True
    for file_path in essential_files:
        if Path(file_path).exists():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} missing")
            all_ok = False
    
    return all_ok

def main():
    """Run all tests."""
    print("=" * 60)
    print("LogMiner-QA Installation Test")
    print("=" * 60)
    
    results = []
    
    results.append(("File Structure", test_file_structure()))
    results.append(("Dependencies", test_dependencies()))
    results.append(("Imports", test_imports()))
    results.append(("Basic Functionality", test_basic_functionality()))
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name:.<40} {status}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n✅ All tests passed! Installation is ready.")
        return 0
    else:
        print("\n❌ Some tests failed. Please fix issues before distribution.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

