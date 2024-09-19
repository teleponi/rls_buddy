# Pytest


## Custom Marker
- `pytest -m "smoke"`: Run all test with marker `smoke`

### Definition
```python
    @pytest.mark.update
    def test_update_tracking():
```

### Usage
```python
    pytest -m "update"
```

### Custom Marker in `pytest.ini`
```ini
    [pytest]
    markers =
        smoke: Run the smoke test
        update: Run the update test
```
