import pytest
import sys
import traceback
from tests.integration.test_crisis_integration import *

@pytest.mark.asyncio
async def test_crisis_mode_gates_entries_debug(bot):
    try:
        await test_crisis_mode_gates_entries(bot)
    except Exception as e:
        traceback.print_exc()

