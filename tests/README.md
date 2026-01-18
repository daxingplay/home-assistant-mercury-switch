# Mercury Switch Integration Tests

## Running Tests

Install test dependencies:
```bash
pip install -r tests/requirements.txt
```

Run all tests:
```bash
pytest tests/ -v
```

Run specific test file:
```bash
pytest tests/test_config_flow.py -v
```

## Test Coverage

- **test_config_flow.py**: Tests for configuration flow (user input, validation, duplicate detection)
- **test_init.py**: Tests for integration setup and unload
- **test_sensor.py**: Tests for sensor entities (device info, port stats, VLAN info)
- **test_binary_sensor.py**: Tests for binary sensor entities (port status)

## Test Fixtures

- `mock_mercury_switch_api`: Mocked API connector with successful responses
- `mock_mercury_switch_api_auth_fail`: Mocked API connector with authentication failure
- `mock_mercury_switch_api_connection_error`: Mocked API connector with connection errors
- `mock_config_entry`: Mock Home Assistant config entry
- `mock_switch_infos`: Mock switch information data
