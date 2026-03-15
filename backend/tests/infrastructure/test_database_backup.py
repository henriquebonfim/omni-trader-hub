"""Tests for Memgraph backup functionality."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.database.memgraph import MemgraphDatabase


@pytest.mark.asyncio
async def test_backup_db_success():
    """Backup command runs successfully and returns timestamp."""
    db = MemgraphDatabase(host="localhost", port=7687)

    mock_result = AsyncMock()
    mock_result.single.return_value = {"ok": 1}

    mock_session = AsyncMock()
    mock_session.run.return_value = mock_result

    mock_driver = MagicMock()
    session_cm = AsyncMock()
    session_cm.__aenter__.return_value = mock_session
    mock_driver.session.return_value = session_cm

    db._driver = mock_driver

    backup_id = await db.backup_db()

    assert isinstance(backup_id, str)
    mock_session.run.assert_awaited_once_with("CREATE SNAPSHOT;")


@pytest.mark.asyncio
async def test_backup_db_failure():
    """Backup errors are raised."""
    db = MemgraphDatabase(host="localhost", port=7687)

    mock_session = AsyncMock()
    mock_session.run.side_effect = Exception("Backup failed")

    mock_driver = MagicMock()
    session_cm = AsyncMock()
    session_cm.__aenter__.return_value = mock_session
    mock_driver.session.return_value = session_cm

    db._driver = mock_driver

    with pytest.raises(Exception, match="Backup failed"):
        await db.backup_db()
