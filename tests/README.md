# PyGuardPoint Test Suite

Comprehensive test suite for pyGuardPoint SDK using pytest.

## Test Structure

```
tests/
├── conftest.py              # Pytest fixtures and configuration
├── test_cardholders.py      # Cardholder CRUD operations
├── test_cards.py            # Card operations
├── test_api_endpoints.py    # Various API endpoints (areas, events, etc.)
├── test_error_handling.py   # Error scenarios and edge cases
└── README.md               # This file
```

## Setup

### Prerequisites

```bash
pip install pytest pytest-timeout pytest-asyncio
cd /path/to/pyGuardPoint
```

### Configuration

Tests use the public test server at `https://sensoraccess.duckdns.org` with default credentials.

Configure via environment variables (optional):

```bash
export GP_HOST="https://sensoraccess.duckdns.org"
export GP_USER="admin"
export GP_PASS="admin"
export GP_TLS_P12=""              # Optional: path to certificate
export GP_TLS_P12_PWD=""          # Optional: certificate password
```

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Category

```bash
# Cardholder tests only
pytest tests/test_cardholders.py

# Card tests only
pytest tests/test_cards.py

# API endpoint tests only
pytest tests/test_api_endpoints.py

# Error handling tests only
pytest tests/test_error_handling.py
```

### Run with Markers

```bash
# Integration tests only (default)
pytest -m integration

# Destructive tests (creates/modifies data)
pytest -m destructive

# Async tests
pytest -m async

# Exclude destructive tests
pytest -m "not destructive"

# Only integration tests
pytest -m integration
```

### Run with Verbosity

```bash
# Verbose output
pytest -v

# Very verbose (show all test names)
pytest -vv

# Show print statements
pytest -s

# Show local variables on failure
pytest -l
```

### Run with Filtering

```bash
# Run only cardholder creation tests
pytest tests/test_cardholders.py::TestCardholderCRUD::test_create_cardholder

# Run tests matching pattern
pytest -k "create"

# Run tests NOT matching pattern
pytest -k "not delete"

# Run specific test class
pytest tests/test_cardholders.py::TestCardholderCRUD
```

## Test Coverage

### Test Categories

#### 1. **test_cardholders.py** - Cardholder Operations
- ✅ Create cardholder
- ✅ Create with personal details
- ✅ Read by UID
- ✅ Update properties
- ✅ Delete cardholder
- ✅ Search by name/email/site
- ✅ Error handling (nonexistent, duplicates)
- ✅ Data integrity (cards collection, personal details)

**Classes**: TestCardholderCRUD, TestCardholderRetrieval, TestCardholderErrorHandling

#### 2. **test_cards.py** - Card Operations
- ✅ Create card
- ✅ Get card by UID
- ✅ Update card
- ✅ Delete card
- ✅ List all cards
- ✅ Card validation (types, status)
- ✅ Cardholder card relationships

**Classes**: TestCardOperations, TestCardValidation

#### 3. **test_api_endpoints.py** - API Endpoints
- ✅ Areas (get, list, by UID)
- ✅ Access Events (get, pagination)
- ✅ Alarm Events (get, list)
- ✅ Security Groups (get, list, by UID)
- ✅ Readers (get, list, by UID)
- ✅ Alarm Zones (get, list, by UID)
- ✅ Departments (get, list, by UID)
- ✅ Sites (get, list, by UID)
- ✅ Access Groups (get, list, by UID)
- ✅ Weekly Programs (get, list, by UID)
- ✅ Count operations

**Classes**: TestAreasAPI, TestAccessEventsAPI, TestSecurityGroupsAPI, TestReadersAPI, TestAlarmZonesAPI, TestDepartmentsAPI, TestSitesAPI, TestAccessGroupsAPI, TestWeeklyProgramsAPI, TestCardholdersCountAPI

#### 4. **test_error_handling.py** - Error Scenarios
- ✅ Authentication errors (bad credentials)
- ✅ Connection errors (bad host)
- ✅ Resource not found (nonexistent UIDs)
- ✅ Data validation (special chars, unicode, length)
- ✅ List edge cases (zero/negative limits, large limits)
- ✅ Search edge cases (empty terms, special chars)
- ✅ Concurrent operations (update while listing)

**Classes**: TestAuthenticationErrors, TestResourceNotFound, TestDataValidation, TestListOperations, TestConcurrentOperations

## Fixtures

### Provided by conftest.py

#### Configuration
- **config** - Test server configuration (host, credentials, timeout)

#### Clients
- **gp_sync** - Synchronous GuardPoint client
- **gp_async** - Asynchronous GuardPoint client (async fixture)

#### Test Data
- **test_cardholder** - Basic cardholder object
- **test_cardholder_pd** - Cardholder with personal details

#### Cleanup
- **cleanup_cardholders** - Auto-deletes created cardholders after test
- **cleanup_cards** - Auto-deletes created cards after test

### Usage Example

```python
def test_something(gp_sync, test_cardholder, cleanup_cardholders):
    # test_cardholder is a fresh Cardholder object
    # gp_sync is connected GuardPoint client
    # cleanup_cardholders automatically removes created objects
    
    uid = gp_sync.new_card_holder(test_cardholder)
    cleanup_cardholders.append(gp_sync.get_card_holder(uid=uid))
```

## Cleanup Behavior

Tests are designed to be **self-cleaning**:

1. **Cleanup Fixtures** - Automatically delete all created resources
2. **Unique Identifiers** - Each test gets a unique ID for data isolation
3. **Error Recovery** - Cleanup happens even if test fails

Cleanup happens in this order:
1. Cards created during test are deleted
2. Cardholders created during test are deleted
3. Fixture cleanup runs (in reverse order of creation)

## Test Execution Flow

```
Session Start
│
├─ conftest.py loaded
│  ├─ TestConfig created
│  └─ Fixtures registered
│
├─ For each test:
│  ├─ Setup fixtures
│  ├─ Run test
│  ├─ Cleanup fixtures
│  └─ Log results
│
└─ Session End
   └─ Summary printed
```

## Expected Test Results

### Passing Tests
All tests should pass against the test server at `https://sensoraccess.duckdns.org` with default credentials.

### Skipped Tests
Some tests may be skipped if:
- Server is unavailable
- Feature not available on server version
- Async tests in non-async environment

### Failed Tests
Failures indicate:
- Bug in pyGuardPoint SDK
- Test environment issue
- API incompatibility

## Performance Considerations

- **Timeout**: 30 seconds per test (configurable in pytest.ini)
- **Cleanup**: Runs after each test (add ~1-2s per test)
- **Network**: Tests depend on internet connectivity to test server
- **Total Runtime**: ~3-5 minutes for full suite (depends on server)

### Optimization Tips

```bash
# Run only fast tests
pytest --timeout=5

# Run in parallel (requires pytest-xdist)
pip install pytest-xdist
pytest -n auto

# Skip cleanup (risky, for debugging only)
pytest -m "not destructive"
```

## Common Issues

### Connection Refused
```
Error: Connection refused to https://sensoraccess.duckdns.org
```
**Solution**: Check internet connection, verify test server is reachable

### Authentication Failed
```
GuardPointUnauthorized: Invalid credentials
```
**Solution**: Verify GP_USER and GP_PASS environment variables

### Timeout
```
TIMEOUT: Exceeded 30 seconds
```
**Solution**: Increase timeout in pytest.ini, check network latency

### Port Already in Use
```
OSError: [Errno 48] Address already in use
```
**Solution**: Close other applications, wait for cleanup

## Extending Tests

### Add New Test

```python
@pytest.mark.integration
class TestMyFeature:
    """Test my feature."""
    
    def test_something(self, gp_sync, cleanup_cardholders):
        """Test description."""
        # Create test data
        ch = Cardholder()
        ch.firstName = "Test"
        uid = gp_sync.new_card_holder(ch)
        
        # Add to cleanup
        cleanup_cardholders.append(gp_sync.get_card_holder(uid=uid))
        
        # Assert something
        assert uid is not None
```

### Add New Fixture

Edit conftest.py:

```python
@pytest.fixture
def my_fixture(gp_sync):
    """My custom fixture."""
    # Setup
    data = gp_sync.get_something()
    
    yield data
    
    # Teardown (optional)
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: PyGuardPoint Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt pytest
      - run: pytest tests/ -m integration
```

## Troubleshooting

### Debug Single Test

```bash
pytest tests/test_cardholders.py::TestCardholderCRUD::test_create_cardholder -vvs
```

### Show Full Traceback

```bash
pytest --tb=long
```

### Save Test Results

```bash
pytest --html=report.html --self-contained-html
```

### Log File

```
tests/pytest.log
```

## Security Note

Tests use default credentials on public test server. Never run against production with these fixtures.

For production testing, create isolated test fixtures with unique credentials.
