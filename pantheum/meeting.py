from typing import List
import asyncio

from pydantic import BaseModel

from .agent import Agent
from .types import Task


class Message(BaseModel):
    source: str
    targets: List[str]
    content: str


class AgentRunner:
    def __init__(self, agent: Agent, public_queue: asyncio.Queue):
        self.agent = agent
        self.public_queue = public_queue
        self.queue = asyncio.Queue()

    async def run(self):
        while True:
            message = await self.queue.get()
            await self.agent.chat(message)


class Meeting:
    def __init__(self, agents: List[Agent]):
        self.agents = {agent.name: agent for agent in agents}
        self.agent_runners = {
            agent.name: AgentRunner(agent, self.public_queue)
            for agent in agents
        }
        self.public_queue = asyncio.Queue()

    async def process_public_queue(self):
        while True:
            message = await self.public_queue.get()

    async def run(self):
        for runner in self.agent_runners.values():
            asyncio.create_task(runner.run())

        asyncio.create_task(self.process_public_queue())

        while True:
            message = await self.queue.get()
            await self.agent.chat(message)


class Team:
    def __init__(
            self,
            leader: Agent,
            members: List[Agent]):
        self.leader = leader
        self.members = members

    async def solve(self, task: Task):
        pass
