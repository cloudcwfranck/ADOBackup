import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture(scope="module")
def test_config():
    return {
        "pat": "dummy_pat",
        "organization": "test_org",
        "storage_connection_string": "test_conn_str",
        "container_name": "test_container"
    }