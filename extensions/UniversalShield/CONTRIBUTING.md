# Contributing to UniversalShield

Thank you for your interest in contributing! This project is 100% open source.

## How to Contribute

### Adding New Scam Patterns

The easiest way to contribute is by adding new scam patterns:

1. Open `src/scamPatterns.js`
2. Add your pattern to the appropriate category
3. Submit a Pull Request

**Example:**
```javascript
// In cvScams array:
'your new scam phrase here',
```

### Reporting Scams

If you encounter a scam on LinkedIn:
1. Take a screenshot (blur personal info)
2. Open an issue with the scam text
3. We'll add the pattern to our detection

### Code Contributions

1. Fork the repository
2. Create a branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Test locally in Chrome
5. Submit a Pull Request

## Development Setup

```bash
# Clone
git clone https://github.com/jcuberogit/universalshield.git
cd universalshield

# Load in Chrome
1. Open chrome://extensions/
2. Enable Developer mode
3. Click "Load unpacked"
4. Select project folder
```

## Code Style

- Use clear variable names
- Add comments for complex logic
- Keep functions small and focused

## Questions?

Open an issue or start a discussion on GitHub.
