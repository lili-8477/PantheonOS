import json
from pathlib import Path
from .utils.llm import process_messages_for_store
from .utils.log import logger


class Memory:
    def __init__(self, name: str):
        self.name = name
        self._messages: list[dict] = []

    def save(self, file_path: str):
        with open(file_path, "w") as f:
            json.dump(self._messages, f)

    def load(self, file_path: str):
        with open(file_path, "r") as f:
            self._messages = json.load(f)

    def add_messages(self, messages: list[dict]):
        messages = process_messages_for_store(messages)
        self._messages.extend(messages)

    def get_messages(self):
        return self._messages


class MemoryManager:
    def __init__(self):
        self.memory_store = {}

    def new_memory(self, name: str | None = None) -> Memory:
        if name is None:
            base_name = "New Chat"
            i = 0
            name = f"{base_name} {i}"
            while name in self.memory_store:
                i += 1
                name = f"{base_name} {i}"
        self.memory_store[name] = Memory(name)
        return self.memory_store[name]

    def get_memory(self, name: str) -> Memory:
        return self.memory_store[name]

    def list_memories(self):
        return list(self.memory_store.keys())

    def save(self, dir_path: str | Path):
        path = Path(dir_path)
        if not path.exists():
            path.mkdir(parents=True)
        for name, memory in self.memory_store.items():
            memory.save(path / f"{name}.json")

    def load(self, dir_path: str | Path):
        path = Path(dir_path)
        if not path.exists():
            path.mkdir(parents=True)
        for file in path.glob("*.json"):
            memory = Memory(file.stem)
            try:
                memory.load(file)
                logger.info(f"Loaded memory: {memory.name} from {file}")
                self.memory_store[memory.name] = memory
            except Exception as e:
                logger.error(f"Error loading memory: {file} - {e}")
