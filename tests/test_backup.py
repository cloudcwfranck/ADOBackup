import pytest
from unittest.mock import MagicMock, patch

# Use absolute import path
from src.adobackup.core.backup_engine import BackupEngine

@pytest.fixture
def mock_engine():
    with patch('azure.devops.connection.Connection'):
        yield BackupEngine(MagicMock())

def test_backup_init(mock_engine):
    assert isinstance(mock_engine, BackupEngine)