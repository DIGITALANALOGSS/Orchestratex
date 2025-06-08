# Orchestratex Test Suite

This directory contains the test suite for the Orchestratex project. Tests are organized into several categories:

## Directory Structure

- `ui/`: End-to-end UI tests using Playwright
  - `test_voice_interface.spec.ts`: Tests for the voice interface component
- `unit/`: Unit tests for individual components
- `integration/`: Integration tests for system components
- `security/`: Security-related tests
- `performance/`: Performance and load testing
- `workflows/`: End-to-end workflow tests
- `agents/`: Tests specific to agent functionality
- `models/`: Tests for ML/AI models
- `chaos/`: Chaos engineering tests
- `data/`: Test data and fixtures

## Running Tests

### UI Tests
```bash
# Install dependencies
npm install

# Run UI tests
npx playwright test
```

### Python Tests
```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest tests/

# Run specific test category
pytest tests/unit/  # Unit tests
pytest tests/integration/  # Integration tests
```

## Test Organization

### UI Tests
- Uses Playwright for browser automation
- Tests focus on user interactions and visual elements
- Parallel execution enabled for faster testing
- Tests are organized by feature

### Unit Tests
- Tests individual components in isolation
- Uses pytest for test execution
- Mocks external dependencies
- Focuses on component logic

### Integration Tests
- Tests interactions between components
- Uses real dependencies where possible
- Verifies system flows

### Security Tests
- Tests security features and configurations
- Includes authentication and authorization tests
- Tests for common security vulnerabilities

### Performance Tests
- Measures system performance
- Tests load handling
- Verifies response times

### Chaos Tests
- Tests system resilience
- Simulates failure scenarios
- Verifies recovery mechanisms
