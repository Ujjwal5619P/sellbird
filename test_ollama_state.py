import asyncio
import tempfile
from pathlib import Path

from sellbird.state import StateManager


async def main():
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = str(Path(temp_dir) / "test.db")
        state = StateManager(db_path)

        await state.init_db()

        await state.increment_usage("ollama")

        print("Ollama calls:", await state.get_usage_today("ollama"))
        print("Claude calls:", await state.get_usage_today("claude"))
        print("Codex calls:", await state.get_usage_today("codex"))

        summary = await state.get_state_summary()
        print("Provider usage:", summary["usage_today_by_provider"])


asyncio.run(main())