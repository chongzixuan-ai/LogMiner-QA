# Contributing to LogMiner-QA

Thank you for your interest in contributing to LogMiner-QA! This document provides guidelines and instructions for contributing.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected behavior** vs **actual behavior**
- **Environment details**: Python version, OS, dependencies
- **Error messages** or logs (sanitized, no sensitive data!)
- **Minimal reproducible example** if possible

### Suggesting Enhancements

Enhancement suggestions are welcome! Please include:

- **Clear use case** description
- **Proposed solution** or approach
- **Alternative solutions** considered
- **Potential impact** on existing users

### Pull Requests

1. **Fork the repository** and create a feature branch
2. **Follow code style**: Use type hints, maintain docstrings
3. **Add tests** if applicable (we're building test coverage)
4. **Update documentation** for new features
5. **Ensure all checks pass** before submitting
6. **Write clear commit messages**

#### PR Checklist

- [ ] Code follows existing style patterns
- [ ] Type hints added for new functions
- [ ] Docstrings added/updated
- [ ] No sensitive data in commits (logs, secrets, etc.)
- [ ] README/docs updated if needed
- [ ] Changelog updated

### Code Style

- **Python 3.8+** compatibility
- **Type hints** for all function signatures
- **Docstrings** for public functions/classes
- **Black formatting** preferred (compatible with PEP 8)
- **Dataclasses** for configuration objects

### Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/logminer-qa.git
cd logminer-qa

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (when added)
# pip install -r requirements-dev.txt
```

### Testing

```bash
# Run tests (when test suite is added)
pytest

# Run with coverage
pytest --cov=src/logminer_qa
```

### Security Considerations

- **Never commit** secrets, API keys, or sensitive data
- **Sanitize** any log files before committing
- **Use environment variables** for configuration
- **Review** your code for potential security issues

### Areas Needing Contribution

We welcome contributions in these areas:

- **Test coverage**: Unit tests, integration tests
- **Documentation**: Examples, tutorials, API docs
- **Connectors**: New log source integrations
- **Performance**: Optimizations for large datasets
- **Features**: User-requested enhancements
- **Bug fixes**: Issue resolutions

### Questions?

- Open an issue with the `question` label
- Check existing documentation in `docs/`
- Review code comments and docstrings

Thank you for contributing! 🚀

