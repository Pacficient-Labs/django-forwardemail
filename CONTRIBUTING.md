# Contributing to django-forwardemail

Thank you for your interest in contributing to django-forwardemail! This guide will help you get started and ensure your contributions are effective.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Django 4.2+
- Git
- uv (recommended) or pip

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/django-forwardemail.git
   cd django-forwardemail
   ```

2. **Set up Development Environment**
   ```bash
   # Using uv (recommended)
   uv sync --extra dev
   
   # Or using pip
   pip install -e ".[dev]"
   ```

3. **Run Tests**
   ```bash
   uv run pytest
   # or
   python -m pytest
   ```

## 📋 How to Report Issues

### Before Creating an Issue

1. **Search Existing Issues**: Check if your issue already exists
2. **Read Documentation**: Review the README and documentation
3. **Check Troubleshooting Guide**: Look for common solutions
4. **Test with Latest Version**: Ensure you're using the latest version

### Creating Effective Issues

#### 🐛 Bug Reports
Use the bug report template and include:
- **Clear Description**: What happened vs. what you expected
- **Reproduction Steps**: Detailed steps to reproduce the issue
- **Code Sample**: Minimal code that demonstrates the problem
- **Environment Details**: Django version, Python version, OS
- **Error Messages**: Full traceback if applicable

**Example of a Good Bug Report:**
```markdown
## Bug Description
EmailService.send_email() fails with Site.DoesNotExist when no request context is provided

## Expected Behavior
The service should automatically detect the current site or use a fallback

## Actual Behavior
Raises Site.DoesNotExist exception

## Steps to Reproduce
1. Install django-forwardemail
2. Configure EmailConfiguration in admin
3. Call EmailService.send_email() from a management command
4. See error

## Code Sample
```python
# management/commands/send_notification.py
from django_forwardemail.services import EmailService

EmailService.send_email(
    to='user@example.com',
    subject='Test',
    text='Test message'
)
```

## Error Message
```
Site.DoesNotExist: Site matching query does not exist.
```

## Environment
- Django: 4.2.7
- django-forwardemail: 1.0.0
- Python: 3.11.0
```

#### ✨ Feature Requests
Use the feature request template and include:
- **Problem Statement**: What limitation are you facing?
- **Proposed Solution**: What feature would solve this?
- **Use Case**: Specific example of how you'd use it
- **Implementation Ideas**: If you have technical suggestions

#### ❓ Questions
Use the question template and include:
- **Clear Question**: What specifically do you need help with?
- **Context**: What are you trying to achieve?
- **What You've Tried**: Show your attempts and code
- **Expected Outcome**: What result are you hoping for?

## 🔧 Best Practices for Issues

### Writing Clear Titles
- ❌ "Email not working"
- ✅ "[BUG] EmailService.send_email() fails with Site.DoesNotExist in management commands"

- ❌ "Add feature"
- ✅ "[FEATURE] Add support for bulk email sending"

### Providing Context
- **Environment**: Always include Django, Python, and package versions
- **Configuration**: Share relevant settings (remove sensitive data)
- **Code**: Provide minimal, complete examples
- **Logs**: Include full error messages and tracebacks

### Being Specific
- Instead of "it doesn't work", describe exactly what happens
- Instead of "sometimes fails", provide specific conditions
- Instead of "should be better", explain the specific improvement

## 🛠️ Contributing Code

### Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Follow existing code style
   - Add tests for new functionality
   - Update documentation if needed

3. **Run Tests and Linting**
   ```bash
   uv run pytest
   uv run ruff check .
   uv run mypy .
   ```

4. **Commit Changes**
   ```bash
   git commit -m "feat: add bulk email sending support"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

### Code Standards
- Follow PEP 8 style guidelines
- Use type hints for all functions
- Write comprehensive docstrings
- Add tests for new functionality
- Maintain backward compatibility

### Testing
- Write unit tests for all new features
- Ensure all tests pass
- Test with multiple Django versions if applicable
- Include integration tests for complex features

## 📚 Documentation

### When to Update Documentation
- Adding new features
- Changing existing behavior
- Fixing bugs that affect usage
- Adding configuration options

### Documentation Standards
- Use clear, concise language
- Provide code examples
- Include common use cases
- Update README if needed

## 🏷️ Issue Labels

Understanding our label system:

### Type Labels
- `bug`: Something isn't working correctly
- `enhancement`: New feature or improvement
- `question`: Help or clarification needed
- `documentation`: Documentation improvements

### Priority Labels
- `critical`: Urgent issues affecting production
- `high`: Important issues that should be addressed soon
- `medium`: Standard priority
- `low`: Nice to have improvements

### Status Labels
- `needs-triage`: New issue that needs review
- `needs-reproduction`: Bug that needs reproduction steps
- `help-wanted`: Community contributions welcome
- `good-first-issue`: Good for new contributors

## 🤝 Community Guidelines

### Be Respectful
- Use welcoming and inclusive language
- Be respectful of differing viewpoints
- Accept constructive criticism gracefully
- Focus on what's best for the community

### Be Helpful
- Provide detailed information in issues
- Help others when you can
- Share your knowledge and experience
- Be patient with newcomers

### Be Professional
- Keep discussions on-topic
- Avoid personal attacks or harassment
- Use appropriate language
- Respect maintainer decisions

## 📞 Getting Help

If you need help with contributing:

1. **Check Existing Issues**: Look for similar questions
2. **Create a Question Issue**: Use the question template
3. **Join Discussions**: Participate in GitHub Discussions
4. **Be Patient**: Maintainers are volunteers

## 🙏 Recognition

Contributors are recognized in:
- Release notes for significant contributions
- README contributors section
- GitHub contributor graphs

Thank you for helping make django-forwardemail better! 🎉
