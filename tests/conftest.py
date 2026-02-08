from pathlib import Path

import pytest

_DATA_DIR = Path(__file__).parent / "data"


@pytest.fixture
def test_data_dir() -> Path:
    """Return the path to the test data directory."""
    return _DATA_DIR


@pytest.fixture
def baseline_dir() -> Path:
    """Return the path to the baseline HTML fixtures."""
    return _DATA_DIR / "html" / "baseline"


@pytest.fixture
def variants_dir() -> Path:
    """Return the path to the variant HTML fixtures."""
    return _DATA_DIR / "html" / "variants"
