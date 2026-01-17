# Contributing to Safe Let Stays

Thank you for your interest in contributing to Safe Let Stays! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Code Style](#code-style)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)

## Code of Conduct

Please be respectful and professional in all interactions. We are committed to providing a welcoming and inclusive environment for everyone.

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Set up the development environment (see below)
4. Create a new branch for your feature or bug fix

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Git
- A text editor or IDE (VS Code recommended)

### Local Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/Safe-Let-Stays.git
cd Safe-Let-Stays

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

## Making Changes

### Branch Naming

Use descriptive branch names:

- `feature/add-search-filters` - New features
- `bugfix/fix-login-redirect` - Bug fixes
- `docs/update-readme` - Documentation
- `refactor/cleanup-views` - Code refactoring

### Commit Messages

Write clear, concise commit messages:

```
feat: Add guest capacity filter to search
fix: Correct redirect URL after login
docs: Update deployment instructions
refactor: Extract common context to helper function
```

## Code Style

### Python

- Follow PEP 8 guidelines
- Maximum line length: 120 characters
- Use 4 spaces for indentation
- Use meaningful variable and function names
- Add docstrings to functions and classes

```python
def calculate_booking_total(nightly_rate: Decimal, nights: int, cleaning_fee: Decimal = 0) -> Decimal:
    """
    Calculate the total price for a booking.
    
    Args:
        nightly_rate: The rate per night in GBP.
        nights: Number of nights for the booking.
        cleaning_fee: Optional one-time cleaning fee.
    
    Returns:
        The total booking price.
    """
    return (nightly_rate * nights) + cleaning_fee
```

### HTML/Django Templates

- Use 2 spaces for indentation
- Use meaningful block names
- Comment complex sections

### JavaScript

- Use 2 spaces for indentation
- Use ES6+ syntax where possible
- Document React components

## Testing

### Running Tests

```bash
# Run all tests
python manage.py test yourapp

# Run specific test file
python manage.py test yourapp.tests

# Run with coverage
coverage run --source='yourapp' manage.py test yourapp
coverage report
```

### Writing Tests

- Write tests for all new features
- Write tests for bug fixes
- Aim for meaningful test coverage
- Test edge cases

```python
class PropertyModelTest(TestCase):
    def setUp(self):
        self.property = Property.objects.create(
            title='Test Property',
            price_from=Decimal('100.00'),
            beds=2,
            baths=1,
            capacity=4
        )

    def test_property_slug_generation(self):
        """Test that slug is auto-generated from title."""
        self.assertEqual(self.property.slug, 'test-property')
```

## Submitting Changes

### Before Submitting

1. Run all tests: `python manage.py test yourapp`
2. Check for linting issues: `flake8 yourapp`
3. Update documentation if needed
4. Ensure your branch is up to date with main

### Pull Request Process

1. Push your branch to your fork
2. Open a Pull Request against the main repository
3. Fill out the PR template with:
   - Description of changes
   - Related issue number (if any)
   - Screenshots (for UI changes)
4. Wait for code review
5. Address any feedback
6. Once approved, your PR will be merged

### Pull Request Template

```markdown
## Description
Brief description of what this PR does.

## Related Issue
Fixes #123

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
Describe how you tested the changes.

## Screenshots (if applicable)
Add screenshots here.
```

## Questions?

If you have any questions, please open an issue or reach out to the maintainers.

Thank you for contributing! 🎉
