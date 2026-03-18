# Contributing to Service Manager

Thank you for your interest in contributing to Service Manager! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Feature Requests](#feature-requests)

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Keep discussions professional and on-topic

## Getting Started

### 1. Fork the Repository

```bash
# Click "Fork" on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/service-manager.git
cd service-manager
```

### 2. Create a Branch

```bash
# Create a branch for your feature/fix
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-123
```

### 3. Set Up Development Environment

```bash
# Install dependencies
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 polkit

# Test the application
python3 service_manager.py
```

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the behavior
- **Expected vs actual behavior**
- **Screenshots** if applicable
- **Environment details**:
  - OS version (e.g., Ubuntu 22.04)
  - Python version
  - GTK version

**Example:**
```markdown
**Bug**: Application crashes when stopping multiple services

**Steps to Reproduce:**
1. Select 5+ services
2. Click "Stop Selected"
3. Enter password
4. Application crashes

**Expected:** Services stop without crash
**Actual:** Application exits with error

**Environment:**
- Ubuntu 22.04
- Python 3.10.6
- GTK 3.24.33
```

### Feature Requests

Feature requests are welcome! Please include:

- **Clear description** of the feature
- **Use case** - why this feature would be useful
- **Examples** of how it would work
- **Alternatives** you've considered

### Submitting Code

1. **Make your changes** following coding standards
2. **Test thoroughly** - ensure no regressions
3. **Commit with clear messages** (see below)
4. **Push to your fork**
5. **Open a Pull Request**

## Coding Standards

### Python Style

- Follow [PEP 8](https://pep8.org/)
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use type hints where appropriate

### Code Organization

```python
# Imports first
import gi
import subprocess

# Then constants
DEFAULT_SERVICES = {...}

# Then classes
class ServiceManagerWindow(Gtk.Window):
    def __init__(self):
        # Constructor code
    
    def public_method(self):
        """Docstring for public methods."""
        pass
    
    def _private_method(self):
        """Leading underscore for internal methods."""
        pass
```

### Commit Messages

Follow conventional commits format:

```
feat: add service search functionality
fix: resolve crash when stopping multiple services
docs: update README with installation instructions
style: format code according to PEP 8
refactor: improve service loading performance
test: add unit tests for service filtering
```

### Documentation

- Add docstrings to all public methods
- Comment complex logic
- Update README if adding new features
- Keep inline comments minimal but clear

## Pull Request Process

1. **Update documentation** if needed
2. **Test your changes** on multiple Ubuntu versions if possible
3. **Ensure CI passes** (when configured)
4. **Request review** from maintainers
5. **Address feedback** promptly
6. **Squash commits** if requested

### PR Checklist

Before submitting your PR:

- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Tests pass (when applicable)
- [ ] Documentation updated
- [ ] No merge conflicts
- [ ] Commit messages are clear

## Development Workflow

```bash
# 1. Sync with upstream
git remote add upstream https://github.com/ORIGINAL_OWNER/service-manager.git
git fetch upstream
git rebase upstream/main

# 2. Create feature branch
git checkout -b feature/my-feature

# 3. Make changes and commit
git add .
git commit -m "feat: add new feature"

# 4. Push to your fork
git push origin feature/my-feature

# 5. Create PR on GitHub
```

## Questions?

- Open an issue for questions
- Check existing issues for answers
- Join discussions in GitHub Discussions

## Thank You!

Your contributions make Service Manager better for everyone. We appreciate your time and effort!

---

*This contributing guide was inspired by projects like GitHub, Atom, and Electron.*
