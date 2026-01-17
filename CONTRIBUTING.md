# Contributing to Healthcare AI Recommendation System

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Git Workflow](#git-workflow)
- [Code Standards](#code-standards)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)

---

## 🤝 Code of Conduct

### Our Pledge
We are committed to providing a welcoming and inspiring community for all. Please read and adhere to our Code of Conduct:

- Be respectful and inclusive
- Welcome diverse perspectives
- Provide constructive feedback
- Report inappropriate behavior
- Maintain professional communication

### Expected Behavior
- Use welcoming and inclusive language
- Be respectful of differing opinions
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards others

---

## 🎯 How Can I Contribute?

### 1. **Report Bugs** 🐛
- Check if bug already exists in [Issues](../../issues)
- Use bug report template
- Include steps to reproduce
- Provide system information
- Attach screenshots/logs

**Bug Report Template:**
```markdown
## Description
[Clear description of the bug]

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]

## Environment
- OS: [e.g., Windows 10, Ubuntu 20.04]
- Python Version: [e.g., 3.8, 3.9]
- Browser: [if applicable]

## Additional Context
[Any other relevant information]
```

### 2. **Suggest Features/Enhancements** ✨
- Check existing feature requests
- Clearly describe the feature
- Explain why it would be useful
- Provide usage examples
- Discuss implementation approach

**Feature Request Template:**
```markdown
## Summary
[Brief description]

## Motivation
[Why this feature is needed]

## Proposed Solution
[How it should work]

## Example Usage
[Code or workflow example]

## Alternative Solutions
[Any alternatives considered]
```

### 3. **Contribute Code** 💻
- Fix bugs
- Implement new features
- Improve performance
- Enhance documentation
- Add tests

### 4. **Improve Documentation** 📚
- Fix typos
- Clarify explanations
- Add examples
- Improve structure
- Translate content

---

## 🔧 Development Setup

### Prerequisites
- Python 3.8+
- Git
- Virtual environment (recommended)

### Setup Steps

1. **Fork the Repository**
```bash
# Click "Fork" on GitHub
```

2. **Clone Your Fork**
```bash
git clone https://github.com/YOUR-USERNAME/medi_recomm.git
cd medi_recomm
```

3. **Add Upstream Remote**
```bash
git remote add upstream https://github.com/ORIGINAL-OWNER/medi_recomm.git
```

4. **Create Virtual Environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

5. **Install Dependencies**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

6. **Setup Pre-commit Hooks** (Optional)
```bash
pre-commit install
```

---

## 🌿 Git Workflow

### 1. **Create Feature Branch**
```bash
# Update main branch
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/your-feature-name
```

### Branch Naming Conventions
- **Features**: `feature/add-new-model`
- **Bug fixes**: `bugfix/fix-login-issue`
- **Documentation**: `docs/update-readme`
- **Performance**: `perf/optimize-predictions`
- **Tests**: `test/add-unit-tests`

### 2. **Make Changes**
```bash
# Make your changes
# Test thoroughly
# Keep commits logical and atomic
```

### 3. **Stay Updated**
```bash
git fetch upstream
git rebase upstream/main
```

### 4. **Push Changes**
```bash
git push origin feature/your-feature-name
```

### 5. **Create Pull Request**
- Go to GitHub
- Create PR with clear description
- Reference related issues
- Wait for reviews

---

## 📝 Code Standards

### Python Style Guide (PEP 8)

#### Naming Conventions
```python
# Classes: PascalCase
class UserAuthentication:
    pass

# Functions/Methods: snake_case
def calculate_bmi(weight, height):
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3
DATABASE_TIMEOUT = 30

# Private variables: _leading_underscore
_internal_state = None
```

#### Code Organization
```python
"""Module docstring with brief description."""

# Imports (sorted: stdlib, third-party, local)
import os
import sys
from datetime import datetime

import pandas as pd
import numpy as np

from .utils import DataProcessor
from .models import DiseasePredictionModel

# Constants
MAX_USERS = 1000
DEFAULT_TIMEOUT = 30

# Classes
class MyClass:
    """Class docstring."""
    pass

# Functions
def my_function():
    """Function docstring."""
    pass
```

### Docstring Format (Google Style)
```python
def predict_disease(symptoms: list, age: int, gender: str) -> dict:
    """Predict disease based on symptoms and demographics.
    
    Args:
        symptoms: List of symptom strings reported by user
        age: Age of the patient in years
        gender: Gender of patient ('M', 'F', 'Other')
    
    Returns:
        Dictionary containing:
            - diseases: List of predicted diseases sorted by probability
            - confidence: Confidence score (0-1)
            - recommendations: List of recommended actions
    
    Raises:
        ValueError: If symptoms list is empty
        TypeError: If age or gender are of wrong type
    
    Example:
        >>> result = predict_disease(['fever', 'cough'], 35, 'M')
        >>> print(result['diseases'][0])
        'Common Cold'
    """
    pass
```

### Type Hints
```python
from typing import List, Dict, Optional, Tuple, Union

def process_data(
    data: pd.DataFrame,
    threshold: float = 0.5,
    categories: Optional[List[str]] = None
) -> Tuple[pd.DataFrame, Dict[str, float]]:
    """Process data with type hints."""
    pass
```

### Code Quality Tools
```bash
# Format code
black --line-length 99 *.py

# Check style
flake8 . --max-line-length=99

# Type checking
mypy .

# Sort imports
isort .
```

---

## 💬 Commit Messages

### Message Format
```
<type>: <subject>

<body>

<footer>
```

### Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style (formatting, missing semicolons, etc.)
- **refactor**: Code refactoring without feature/bug changes
- **perf**: Performance improvements
- **test**: Adding or updating tests
- **chore**: Build process, dependencies, tools

### Examples
```
feat: add neural network disease prediction model

- Implement TensorFlow-based deep learning model
- Add model training and evaluation pipeline
- Include model persistence with joblib
- Improve disease prediction accuracy by 15%

Fixes #123
```

```
fix: resolve hardcoded file paths

- Replace hardcoded paths with dynamic imports
- Use relative paths for cross-platform compatibility
- Add environment variable support

Fixes #456
```

```
docs: update README with installation steps

- Add detailed prerequisites section
- Include virtual environment setup
- Add troubleshooting section
```

---

## 🔄 Pull Request Process

### Before Submitting PR
- [ ] Fork repository and create feature branch
- [ ] Make changes following code standards
- [ ] Test all changes thoroughly
- [ ] Update documentation
- [ ] Add/update tests
- [ ] Run linters and formatters
- [ ] Rebase on latest main
- [ ] Squash unnecessary commits

### PR Description Template
```markdown
## Description
[Detailed description of changes]

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Related Issues
Fixes #123
Relates to #456

## Testing Done
- [ ] Unit tests added/updated
- [ ] Tested locally
- [ ] Tested on multiple OS (if applicable)

## Screenshots (if applicable)
[Add screenshots]

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] No new warnings generated
- [ ] Tests pass
- [ ] Code is commented
```

### Review Process
1. Automated checks run
2. Maintainers review code
3. Changes may be requested
4. Address feedback and update PR
5. PR is merged once approved

---

## 🧪 Testing Guidelines

### Unit Tests
```python
import unittest
from models import DiseasePredictionModel

class TestDiseasePrediction(unittest.TestCase):
    def setUp(self):
        self.model = DiseasePredictionModel()
    
    def test_prediction_returns_dict(self):
        result = self.model.predict(['fever', 'cough'])
        self.assertIsInstance(result, dict)
    
    def test_confidence_in_range(self):
        result = self.model.predict(['fever'])
        self.assertGreaterEqual(result['confidence'], 0)
        self.assertLessEqual(result['confidence'], 1)
```

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_models.py

# Run with coverage
pytest --cov=src tests/

# Run with verbose output
pytest -v
```

### Test Coverage Target
- Aim for >80% code coverage
- Critical paths should have 100% coverage
- Document why uncovered code exists (if applicable)

---

## 📚 Documentation

### Docstring Requirements
Every public function/class must have:
- Brief description
- Args with types
- Returns with types
- Raises (if applicable)
- Example usage

### README Updates
- Update README.md if changing features
- Keep installation instructions current
- Document new dependencies

### Code Comments
```python
# Good: explains WHY
# We use collaborative filtering instead of content-based to handle
# new users who have no preference history
recommendations = self.cf_engine.recommend(user_id)

# Bad: explains WHAT (code already shows this)
# Get recommendations
recommendations = self.cf_engine.recommend(user_id)
```

---

## 🎓 Learning Resources

### Project Documentation
- [README.md](../README.md) - Project overview
- [docs/](../docs/) - Detailed documentation

### External Resources
- [Python PEP 8](https://www.python.org/dev/peps/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [scikit-learn Documentation](https://scikit-learn.org/)

---

## ❓ Questions?

- 📧 Email: support@healthai.com
- 💬 GitHub Discussions: [Ask questions](../../discussions)
- 🐛 GitHub Issues: [Report bugs](../../issues)

---

## 🙏 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing! Your efforts help make this project better for everyone.

---

**Last Updated**: January 2026  
**Version**: 1.0.0
