# HRM Application Tests

This directory contains the test suite for the HRM (Human Resource Management) application.

## Test Structure

```
tests/
├── __init__.py          # Makes tests a package
├── test_base.py         # Tests for the Base SQLAlchemy class
└── README.md           # This file
```

## Running Tests

### Prerequisites

Make sure pytest is installed:
```bash
pip install pytest
```

### Running All Tests

```bash
# From the project root directory
python -m pytest tests/ -v

# Or use the test runner script
python run_tests.py
```

### Running Specific Test Files

```bash
# Run only Base class tests
python -m pytest tests/test_base.py -v

# Or with the runner script
python run_tests.py test_base.py
```

### Running Specific Test Classes or Methods

```bash
# Run only TestBase class tests
python -m pytest tests/test_base.py::TestBase -v

# Run only a specific test method
python -m pytest tests/test_base.py::TestBase::test_base_class_instantiation_works -v
```

## Test Categories

### Base Class Tests (`test_base.py`)

Tests for the SQLAlchemy `Base` class that serves as the foundation for all ORM models:

#### Happy Path Tests
- **Base class instantiation works**: Verifies the Base class can be instantiated
- **Base inherits DeclarativeBase functionality**: Tests SQLAlchemy 2.0 DeclarativeBase inheritance
- **Base class allows model inheritance**: Verifies models can inherit from Base

#### Input Verification Tests
- **Base class has correct metadata**: Tests metadata object properties and attributes

#### Branching Tests
- **Base class registry functionality**: Tests SQLAlchemy registry and mapper functionality

#### Integration Tests
- **Base works with Flask-SQLAlchemy**: Tests integration with Flask-SQLAlchemy wrapper
- **Base with actual database connection**: Tests with real database (skipped if DATABASE_URL not set)

#### Error Handling Tests
- **Base with invalid model definition**: Tests behavior with models missing required attributes
- **Base duplicate tablename handling**: Tests handling of models with duplicate table names

## Test Configuration

The test suite is configured via `pytest.ini` in the project root:

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
```

## Environment Variables

Some tests may require environment variables:

- `DATABASE_URL`: Required for database integration tests (tests are skipped if not set)
- `SESSION_SECRET`: Required for Flask app initialization

## Adding New Tests

When adding new test files:

1. Name them with the pattern `test_*.py`
2. Create test classes with names starting with `Test`
3. Create test methods with names starting with `test_`
4. Group related tests in classes
5. Use descriptive test method names
6. Add docstrings to explain what each test verifies
7. Clean up any test data/tables created during tests

### Example Test Structure

```python
class TestNewFeature:
    """Test cases for new feature"""
    
    def test_happy_path_scenario(self):
        """Test that normal usage works correctly"""
        # Test implementation
        pass
    
    def test_edge_case_handling(self):
        """Test handling of edge cases"""
        # Test implementation
        pass
    
    def test_error_conditions(self):
        """Test error handling"""
        # Test implementation
        pass
```

## Best Practices

1. **Isolation**: Each test should be independent and not rely on other tests
2. **Cleanup**: Always clean up any resources created during tests
3. **Clear names**: Use descriptive test names that explain what is being tested
4. **Documentation**: Add docstrings to explain complex test scenarios
5. **Assertions**: Use appropriate pytest assertions for better error messages
6. **Fixtures**: Use pytest fixtures for common setup/teardown operations
7. **Mocking**: Use unittest.mock for external dependencies when needed

## Continuous Integration

The tests are designed to run in CI environments. Make sure:

- All dependencies are in `requirements.txt`
- Tests don't require interactive input
- Database tests are properly skipped when DATABASE_URL is not available
- Tests clean up after themselves