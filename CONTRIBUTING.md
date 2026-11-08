# 🤝 Contributing to VISIONFORGE X

Thank you for your interest in contributing to VISIONFORGE X! This document provides guidelines and instructions for contributing to the project.

---

## 📋 Table of Contents

- [Code of Conduct](#-code-of-conduct)
- [Getting Started](#-getting-started)
- [Development Setup](#-development-setup)
- [Making Changes](#-making-changes)
- [Commit Guidelines](#-commit-guidelines)
- [Pull Request Process](#-pull-request-process)
- [Reporting Issues](#-reporting-issues)
- [Coding Standards](#-coding-standards)

---

## 🧭 Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md) to maintain a welcoming and inclusive community.

---

## 🚀 Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/your-username/VISIONFORGE-X.git
   cd VISIONFORGE-X/desktop_app
   ```
3. **Create a branch** for your work:
   ```bash
   git checkout -b feature/your-feature-name
   ```

---

## 🛠️ Development Setup

### Prerequisites

- Python 3.11 or higher
- pip
- Git

### Setup Steps

```bash
# Create a virtual environment
python -m venv .venv
.venv\Scripts\activate    # Windows
source .venv/bin/activate # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Install in development mode (optional)
pip install -e .

# Run tests to verify setup
pytest tests/ -v
```

---

## 🔧 Making Changes

### Project Structure

The project is organized into these main areas:

| Directory | Purpose |
|-----------|---------|
| `frontend/` | PySide6 GUI components and pages |
| `backend/` | Vision, AI, pipeline, analytics engines |
| `adapters/` | Device abstraction layer |
| `protocol/` | TCP/UDP communication protocol |
| `tests/` | Test suite |

### Before You Start

1. Check [open issues](https://github.com/VetrivelRavichandiran/VISIONFORGE-X/issues) to see if someone is already working on it
2. For major changes, open an issue or [discussion](https://github.com/VetrivelRavichandiran/VISIONFORGE-X/discussions) first
3. Follow the existing code style and architecture patterns

### Testing Your Changes

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test file
pytest tests/test_vision.py -v
```

All tests must pass before submitting a pull request.

---

## 📝 Commit Guidelines

### Commit Message Format

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `style` | Code style (formatting, no logic change) |
| `refactor` | Code refactoring |
| `test` | Adding or updating tests |
| `chore` | Maintenance tasks |

### Examples

```
feat(vision): add bilateral blur algorithm to Vision Studio
fix(pipeline): resolve validation error on empty pipeline
docs(readme): update installation instructions
refactor(backend): extract common telemetry logic
test(vision): add unit tests for Sobel edge detection
```

---

## 📤 Pull Request Process

1. **Update the README.md** with details of changes if the interface changes (new features, new dependencies, etc.)
2. **Update documentation** in the `documentation/` folder if applicable
3. **Add tests** for new features or bug fixes
4. **Ensure all tests pass** locally before pushing
5. **Update the CHANGELOG.md** with a summary of your changes
6. **Submit the PR** with a clear description:
   - What the change does
   - Why the change is needed
   - How it was tested
   - Any breaking changes

### PR Review

- At least one maintainer must approve the PR
- All CI checks must pass
- The PR must be rebased or merged cleanly with `main`

---

## 🐛 Reporting Issues

### Bug Reports

When reporting a bug, please include:

- **Environment**: OS, Python version, dependency versions
- **Steps to reproduce**
- **Expected behavior**
- **Actual behavior**
- **Logs or error messages**
- **Screenshots** (if applicable)

### Feature Requests

- Describe the feature and its use case
- Explain why it would be useful
- Suggest an implementation approach if you have one

---

## 📐 Coding Standards

### Python Style

- Follow [PEP 8](https://pep8.org/) for Python code
- Use type hints where possible
- Keep functions focused and under 50 lines
- Use docstrings for public functions and classes
- Maximum line length: 100 characters

### Frontend (PySide6)

- Use the design system tokens in `frontend/design_system/tokens.py`
- Reuse components from `frontend/components/`
- Keep page logic in `frontend/pages/<page>/page.py`
- Avoid direct hardware calls in UI code — use backend services

### Backend

- Follow the adapter pattern for device communication
- Validate all inputs before processing
- Log operations at appropriate levels
- Never execute arbitrary code in the pipeline engine

---

## 🙏 Thank You!

Every contribution — code, documentation, bug reports, or discussions — helps make VISIONFORGE X better. We appreciate your time and effort!

---

*This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind are welcome!*
