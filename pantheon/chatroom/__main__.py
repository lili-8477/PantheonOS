import asyncio

import fire
from magique.ai.tools.python import PythonInterpreterToolSet
from magique.ai.toolset import run_toolsets

from . import ChatRoom
from ..remote.memory import MemoryManagerService, RemoteMemoryManager
from ..agent import Agent


async def main(memory_path: str = "./.pantheon-chatroom"):
    memory_service = MemoryManagerService(memory_path)
    asyncio.create_task(memory_service.run())
    await asyncio.sleep(0.5)
    remote_memory_manager = RemoteMemoryManager(memory_service.worker.service_id)
    await remote_memory_manager.connect()
    toolset = PythonInterpreterToolSet("python_interpreter")
    async with run_toolsets([toolset], log_level="WARNING"):
        agent = Agent(
            name="Pantheon",
            instructions="You are a helpful assistant that can answer questions and help with tasks.",
            model="gpt-4o-mini",
        )
        await agent.remote_toolset(toolset.service_id)
        chat_room = ChatRoom(agent, remote_memory_manager)
        await chat_room.run()


if __name__ == "__main__":
    fire.Fire(main)
