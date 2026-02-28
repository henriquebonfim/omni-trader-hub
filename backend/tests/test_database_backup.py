"""
Tests for database backup functionality.
"""

import pytest
import subprocess
from unittest.mock import patch, MagicMock
from src.database.postgres import PostgresDatabase

@pytest.mark.asyncio
async def test_backup_db_success():
    """Test successful database backup."""
    db = PostgresDatabase(connection_string="postgresql://user:pass@localhost:5432/testdb")
    
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        
        await db.backup_db()
        
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        cmd = args[0]
        
        assert cmd[0] == "pg_dump"
        assert "-h" in cmd
        assert "-p" in cmd
        assert "-U" in cmd
        assert "-d" in cmd
        assert "PGPASSWORD" in kwargs["env"]

@pytest.mark.asyncio
async def test_backup_db_failure():
    """Test database backup failure handling."""
    db = PostgresDatabase(connection_string="postgresql://user:pass@localhost:5432/testdb")
    
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(1, "pg_dump", stderr="Connection failed")
        
        # Should not raise exception, but log error
        await db.backup_db()
        
        mock_run.assert_called_once()
