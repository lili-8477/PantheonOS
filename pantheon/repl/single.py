import asyncio

from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

from ..agent import Agent
from ..utils.misc import print_agent_message


class Repl:
    def __init__(self, agent: Agent):
        """REPL for a single agent."""
        self.agent = agent
        self.console = Console()

    def print_greeting(self):
        self.console.print(
            "[bold]Welcome to the Pantheon REPL![/bold]\n" +
            "You can start by typing a message or type 'exit' to exit.\n"
        )
        # print current agent
        self.console.print("[bold]Current agent:[/bold]")
        self.console.print(f"  - [blue]{self.agent.name}[/blue]")
        # print agent instructions
        self.console.print(f"    - [green]Instructions:[/green] {self.agent.instructions}")
        # print agent tools
        if self.agent.functions:
            self.console.print("    - [green]Tools:[/green]")
            for func in self.agent.functions.values():
                self.console.print(f"      - {func.__name__}")
        if self.agent.toolset_proxies:
            self.console.print("    - [green]Remote ToolSets:[/green]")
            for proxy in self.agent.toolset_proxies.values():
                self.console.print(f"      - {proxy.service_info.service_name}")

        self.console.print()

    async def print_message(self):
        while True:
            message = await self.agent.events_queue.get()
            print_agent_message(
                self.agent.name,
                message,
                self.console,
                print_assistant_message=False,
            )

    async def run(self, message: str | dict | None = None):
        import logging
        logging.getLogger().setLevel(logging.WARNING)

        self.print_greeting()
        print_task = asyncio.create_task(self.print_message())

        def ask_user():
            message = Prompt.ask("[red][bold]User[/bold][/red]")
            self.console.print()
            return message

        if message is None:
            message = ask_user()
            if message == "exit":
                return
        else:
            self.console.print(f"[red][bold]User[/bold][/red]: {message}\n")

        while True:
            self.console.print(f"[blue][bold]{self.agent.name}[/bold][/blue]: ")

            def process_chunk(chunk: dict):
                content = chunk.get("content")
                if content is not None:
                    self.console.print(content, end="")
        
            await self.agent.run(
                message,
                process_chunk=process_chunk,
            )

            self.console.print("\n")
            message = ask_user()
            if message == "exit":
                break

        print_task.cancel()


if __name__ == "__main__":
    agent = Agent(
        "agent",
        "You are a helpful assistant."
    )
    repl = Repl(agent)
    asyncio.run(repl.run())