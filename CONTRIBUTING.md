# Contributing Guide

Thank you for considering contributing to the Product Marketplace project!

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/product-marketplace.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes
6. Commit: `git commit -m "Add your feature"`
7. Push: `git push origin feature/your-feature-name`
8. Create a Pull Request

## Development Setup

Follow the instructions in QUICKSTART.md to set up your development environment.

## Code Style

### Python (Backend)
- Follow PEP 8 style guide
- Use Black for formatting: `black .`
- Use meaningful variable names
- Add docstrings to functions and classes
- Keep functions small and focused

### TypeScript/JavaScript (Frontend)
- Follow ESLint rules
- Use TypeScript for type safety
- Use functional components with hooks
- Keep components small and reusable
- Use meaningful prop names

## Commit Messages

Follow conventional commits format:

```
type(scope): subject

body

footer
```

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation changes
- style: Code style changes (formatting)
- refactor: Code refactoring
- test: Adding tests
- chore: Maintenance tasks

Examples:
```
feat(products): add product image upload
fix(auth): resolve token refresh issue
docs(readme): update installation instructions
```

## Testing

### Backend Tests
```bash
cd backend
python manage.py test
```

### Before Submitting
- [ ] All tests pass
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] No console errors or warnings
- [ ] Tested on multiple browsers (if frontend)

## Pull Request Process

1. Update README.md with details of changes if needed
2. Update documentation if you changed APIs
3. Add tests for new features
4. Ensure all tests pass
5. Request review from maintainers

## Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How has this been tested?

## Checklist
- [ ] Tests pass
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

## Reporting Bugs

Use GitHub Issues with the following information:

**Bug Report Template:**
```markdown
## Description
Clear description of the bug

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. See error

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Screenshots
If applicable

## Environment
- OS: [e.g., Windows 10]
- Browser: [e.g., Chrome 96]
- Version: [e.g., 1.0.0]
```

## Feature Requests

Use GitHub Issues with the following information:

**Feature Request Template:**
```markdown
## Feature Description
Clear description of the feature

## Use Case
Why is this feature needed?

## Proposed Solution
How should it work?

## Alternatives Considered
Other approaches you've thought about
```

## Code Review Process

1. Maintainers will review your PR
2. Address any feedback
3. Once approved, your PR will be merged
4. Your contribution will be credited

## Community Guidelines

- Be respectful and inclusive
- Help others learn and grow
- Provide constructive feedback
- Follow the code of conduct

## Questions?

Feel free to open an issue for questions or reach out to maintainers.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
