# GraphQLNomad - Development Setup Guide

This document provides information about the current setup and how to work with the GraphQLNomad project.

## Project Structure

GraphQLNomad is a dual-distribution package:
- **Python Package**: Primary distribution via PyPI
- **NPM Wrapper**: Node.js wrapper for npm installation (requires Python/pipx)

## Prerequisites

### For Python Development
- Python 3.6 or higher (tested with 3.10 and 3.12)
- pip (Python package manager)

### For NPM Wrapper Development
- Node.js (tested with v20.x)
- npm (tested with v10.x)

## Installation

### Development Installation (Python)

1. Clone the repository:
```bash
git clone https://github.com/CYBWithFlourish/GraphQLNomad.git
cd GraphQLNomad
```

2. Install in editable mode:
```bash
pip install -e .
```

3. Verify installation:
```bash
graphqlnomad --version
python -m graphqlnomad --help
```

### Production Installation

#### From PyPI (Recommended)
```bash
pipx install graphqlnomad
```

#### From NPM
```bash
npm install -g graphqlnomad
```

## Project Files

### Python Package Files
- `graphqlnomad/`: Main package directory
  - `__init__.py`: Package initialization (empty)
  - `__main__.py`: Module entry point
  - `nomad.py`: Main implementation (GraphQLNomad class and CLI logic)
- `setup.py`: Python package configuration
- `requirements.txt`: Python dependencies (requests, colorama)

### NPM Wrapper Files
- `package.json`: NPM package configuration
- `run.js`: Node.js wrapper script that spawns the Python CLI

### Configuration Files
- `.gitignore`: Git ignore patterns
- `.npmignore`: NPM publish ignore patterns
- `.github/workflows/ci-workflow.yml`: GitHub Actions CI/CD pipeline

## Development Workflow

### Code Quality

The project uses `flake8` for Python code linting:

```bash
# Install flake8
pip install flake8

# Run critical error checks (must pass)
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Run full linting (warnings only)
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
```

**Current Status**: All critical errors are fixed. Some non-critical style warnings remain (69 warnings as of latest update).

### Testing

Basic tests are run via the CI pipeline:
```bash
# Test module execution
python -m graphqlnomad --help

# Test CLI entry point
graphqlnomad --version
```

### CI/CD Pipeline

The project uses GitHub Actions for continuous integration:
- **Trigger**: Push or PR to main branch
- **Python Version**: 3.10
- **Steps**:
  1. Checkout repository
  2. Setup Python
  3. Install dependencies (pip, flake8, package)
  4. Lint with flake8
  5. Run basic module test
  6. Test CLI entry point

See `.github/workflows/ci-workflow.yml` for details.

## Common Issues and Solutions

### Issue: NPM configuration error
**Error**: `npm error config prefix cannot be changed from project config`

**Solution**: This was caused by a user-specific `.npmrc` file in the repository. It has been removed and added to `.gitignore`. If you need local npm configuration, create `.npmrc` in your home directory instead.

### Issue: Import errors after changes
**Solution**: Reinstall the package in editable mode:
```bash
pip install -e .
```

### Issue: Flake8 warnings
**Note**: The CI uses `--exit-zero` for the full flake8 check, so warnings don't fail the build. Critical errors (E9, F63, F7, F82) must be fixed.

## Making Changes

1. **Before making changes**: Run linting to understand baseline
2. **Make minimal changes**: Focus on the specific issue
3. **Test locally**: Run the package and verify functionality
4. **Run linting**: Ensure no new critical errors are introduced
5. **Commit and push**: The CI will automatically run tests

## Dependencies

### Python Dependencies
- `requests`: HTTP client for GraphQL requests
- `colorama`: Terminal color output

### Development Dependencies
- `flake8`: Code linting and style checking

## Package Distribution

### Publishing to PyPI
The package uses `setup.py` with setuptools. Version is currently 1.0.0.

### Publishing to NPM
The npm package is a lightweight wrapper that depends on the Python package being available via pipx. The `postinstall` script automatically installs the Python package.

## Important Notes

1. **`.npmrc` should NOT be committed**: User-specific npm configuration belongs in the user's home directory, not the repository.

2. **The npm package requires Python**: The npm distribution is a convenience wrapper - it requires Python and pipx to be installed.

3. **Version synchronization**: Keep version numbers in sync across:
   - `setup.py`
   - `package.json`
   - `graphqlnomad/nomad.py` (in BANNER and argument parser)

4. **Code style**: The codebase uses compact Python style with some single-line conditionals. While this generates flake8 warnings, it's acceptable as long as critical errors are avoided.

## Support and Contributing

For issues and feature requests, visit:
https://github.com/CYBWithFlourish/GraphQLNomad/issues

See README.md for contribution guidelines.
