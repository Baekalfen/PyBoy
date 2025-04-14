# PyBoy Automated Testing Setup

This guide explains how to set up and run automated tests for the PyBoy game launcher.

## Prerequisites

- Python 3.12 or higher
- pip (Python package manager)
- git

## Installation

1. Clone the repository:
```bash
git clone https://github.com/isabellarussell26/PyBoy.git
cd PyBoy
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
```

3. Install required dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements_tests.txt
pip install gitpython cryptography
```

## Running Tests

The automated tests are located in the `tests` directory. To run the tests:

```bash
pytest tests/test_game_launcher.py -v
```

This will run all tests for the game launcher, including:
- Game launcher initialization
- Settings window initialization
- Keybind update
- ROM directory change
- Game filtering
- Game launch

## Test Configuration

The tests use a minimal pytest configuration defined in `pytest.ini`:
```ini
[pytest]
addopts = -v
testpaths = tests
```

## Test Coverage

The tests cover the following aspects of the game launcher:
1. Initialization and setup
2. Settings management
3. Keybind configuration
4. ROM directory handling
5. Game filtering functionality
6. Game launching process

## Troubleshooting

If you encounter any issues:

1. Ensure all dependencies are installed correctly
2. Check that you're using the correct Python version
3. Verify that the virtual environment is activated
4. Make sure you have the required ROM files in the correct directory

## Contributing

To add new tests:
1. Create a new test file in the `tests` directory
2. Follow the existing test structure
3. Ensure tests are independent and cover specific functionality
4. Run the test suite to verify your changes

## Continuous Integration

The tests are integrated with GitHub Actions and will run automatically on pull requests to ensure code quality and functionality. 