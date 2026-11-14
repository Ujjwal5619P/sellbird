
import asyncio

from sellbird.config import BrainConfig
from sellbird.brain import Brain
from sellbird.state import StateManager


async def main():
    state = StateManager()
    brain = Brain(
        state,
        BrainConfig(provider="ollama", model="qwen3:4b"),
    )

    print("Checking Ollama preflight...")
    error = await brain.preflight()
    print("Preflight:", error or "SUCCESS")

    if not error:
        print("Testing actual inference...")
        response = await brain.think(
            "Reply with exactly: SELLBIRD_OLLAMA_OK",
            timeout=120,
        )
        print("Response:", response)



if __name__ == "__main__":
    asyncio.run(main())
