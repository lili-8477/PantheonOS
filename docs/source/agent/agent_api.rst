Agent API
=========

The Agent class is the core component of Pantheon, providing a flexible interface for creating AI-powered agents with tools, memory, and collaboration capabilities.

Agent Class
-----------

.. code-block:: python

   from pantheon.agent import Agent

Constructor
~~~~~~~~~~~

.. code-block:: python

   Agent(
       name: str,
       instructions: str,
       model: str | list[str] = "gpt-4.1-mini",
       icon: str = '🤖',
       tools: list[Callable] | None = None,
       response_format: Any | None = None,
       use_memory: bool = True,
       memory: Memory | None = None,
       tool_timeout: int = 600,  # 10 minutes
       force_litellm: bool = False,
       max_tool_content_length: int | None = 100000,
   )

**Parameters:**

- ``name`` (str): Unique identifier for the agent
- ``instructions`` (str): System instructions defining agent behavior  
- ``model`` (str | list[str]): LLM model(s) to use. Can be a single model or list of fallback models (default: "gpt-4.1-mini")
- ``icon`` (str): Emoji icon for the agent (default: '🤖')
- ``tools`` (list[Callable]): List of tool functions the agent can use
- ``response_format`` (Any): Pydantic model for structured output
- ``use_memory`` (bool): Whether to use conversation memory (default: True)
- ``memory`` (Memory): Memory instance for persistence
- ``tool_timeout`` (int): Timeout for tool execution in seconds (default: 600)
- ``force_litellm`` (bool): Force using LiteLLM even for OpenAI models (default: False)
- ``max_tool_content_length`` (int): Maximum length of tool output content (default: 100000)

Core Methods
------------

run()
~~~~~

Execute the agent with a message and get a response. This is the primary method for interacting with an agent.

.. code-block:: python

   async def run(
       msg: AgentInput,
       response_format: Any | None = None,
       tool_use: bool = True,
       context_variables: dict | None = None,
       process_chunk: Callable | None = None,
       process_step_message: Callable | None = None,
       check_stop: Callable | None = None,
       memory: Memory | None = None,
       use_memory: bool | None = None,
       update_memory: bool = True,
       tool_timeout: int | None = None,
       model: str | None = None,
       allow_transfer: bool = True,
   ) -> AgentResponse | AgentTransfer

**Parameters:**

- ``msg`` (AgentInput): The input message. Can be:
  
  - ``str``: Simple text message
  - ``BaseModel``: Pydantic model instance (converted to JSON)
  - ``list[str | BaseModel | dict]``: Multiple messages
  - ``AgentResponse``: Response from another agent
  - ``AgentTransfer``: Transfer from another agent
  - ``VisionInput``: Image with text prompt
  
- ``response_format`` (Any): Pydantic model for structured output
- ``tool_use`` (bool): Whether to allow tool usage (default: True)
- ``context_variables`` (dict): Variables accessible to tools and agent
- ``process_chunk`` (Callable): Function called for each streaming chunk
- ``process_step_message`` (Callable): Function called for each step (tool calls, responses)
- ``check_stop`` (Callable): Function to check if execution should stop
- ``memory`` (Memory): Override the agent's default memory
- ``use_memory`` (bool): Whether to use memory for this run
- ``update_memory`` (bool): Whether to update memory with this conversation
- ``tool_timeout`` (int): Override default tool timeout in seconds
- ``model`` (str): Override the agent's default model
- ``allow_transfer`` (bool): Whether to allow transfers to other agents

**Returns:**

- ``AgentResponse``: Contains the agent's response content and details
- ``AgentTransfer``: If the agent transfers to another agent

**Examples:**

.. code-block:: python

   # Simple text message
   response = await agent.run("Hello! How are you?")
   print(response.content)
   
   # With context variables
   response = await agent.run(
       "Process the user data",
       context_variables={"user_id": "123", "session": "abc"}
   )
   
   # Structured output
   from pydantic import BaseModel
   
   class Analysis(BaseModel):
       sentiment: str
       score: float
       keywords: list[str]
   
   response = await agent.run(
       "Analyze: I absolutely love this product!",
       response_format=Analysis
   )
   analysis = response.content  # This is an Analysis instance
   print(f"Sentiment: {analysis.sentiment}, Score: {analysis.score}")
   
   # Multiple messages
   response = await agent.run([
       "First, calculate 2+2",
       "Then multiply the result by 10"
   ])
   
   # With streaming
   async def print_chunk(chunk):
       if "content" in chunk:
           print(chunk["content"], end="", flush=True)
   
   response = await agent.run(
       "Write a short story",
       process_chunk=print_chunk
   )
   
   # Without memory
   response = await agent.run(
       "What is 2+2?",
       use_memory=False  # This conversation won't be remembered
   )
   
   # With images (VisionInput)
   from pantheon.utils.vision import vision_input
   
   vision_msg = vision_input(
       prompt="What's in this image?",
       image_paths=["photo.jpg"],
       from_path=True
   )
   response = await agent.run(vision_msg)
   
   # Agent transfer handling
   response = await agent.run("Transfer me to the expert")
   if isinstance(response, AgentTransfer):
       # Handle transfer to another agent
       expert_agent = get_agent(response.to_agent)
       response = await expert_agent.run(response)

tool()
~~~~~~

Add a tool function to the agent. Tools are functions that the agent can call during execution.

.. code-block:: python

   def tool(
       func: Callable, 
       key: str | None = None
   ) -> Agent

**Parameters:**

- ``func`` (Callable): The function to add as a tool
- ``key`` (str): Optional custom name for the tool (defaults to function name)

**Returns:**

- ``Agent``: Returns self for method chaining

**Examples:**

.. code-block:: python

   # Using decorator syntax
   @agent.tool
   def calculate(expression: str) -> float:
       """Evaluate a mathematical expression."""
       return eval(expression)  # In production, use safe evaluation
   
   # Adding with custom key
   def web_search(query: str) -> list[str]:
       """Search the web for information."""
       return search_engine.search(query)
   
   agent.tool(web_search, key="search")
   
   # Method chaining
   agent = Agent(name="assistant", instructions="You are helpful")
   agent.tool(calculate).tool(web_search)
   
   # Tools can access context variables
   @agent.tool
   def get_user_info(field: str, context_variables: dict) -> str:
       """Get user information from context."""
       user_id = context_variables.get("user_id")
       return database.get_user_field(user_id, field)

toolset()
~~~~~~~~~

Add a complete toolset to the agent. A toolset is a collection of related tools packaged together.

.. code-block:: python

   def toolset(
       toolset: ToolSet
   ) -> Agent

**Parameters:**

- ``toolset`` (ToolSet): A ToolSet instance containing multiple tools

**Returns:**

- ``Agent``: Returns self for method chaining

**Examples:**

.. code-block:: python

   from pantheon.toolsets.python import PythonInterpreterToolSet
   from pantheon.toolsets.web_browse import WebBrowseToolSet
   
   # Add Python interpreter capabilities
   python_tools = PythonInterpreterToolSet("python_env")
   agent.toolset(python_tools)
   
   # Add multiple toolsets
   web_tools = WebBrowseToolSet()
   agent.toolset(python_tools).toolset(web_tools)
   
   # The agent now has access to all tools in both toolsets

remote_toolset()
~~~~~~~~~~~~~~~~

Connect to a remote toolset service. This allows the agent to use tools running on different machines or in the same process.

.. code-block:: python

   async def remote_toolset(
       service_id_or_name: str,
       server_url: str | list[str] | None = None,
       **kwargs
   ) -> Agent

**Parameters:**

- ``service_id_or_name`` (str): The service ID or name to connect to. **Important**: It's recommended to use the service ID for precise targeting. If using service name, ensure it's unique - otherwise a random service with that name will be selected.
- ``server_url`` (str | list[str]): URL(s) of the Magique server. If not provided, uses default Magique servers
- ``**kwargs``: Additional connection parameters passed to ``connect_remote``

**Returns:**

- ``Agent``: Returns self for method chaining

**Service ID vs Service Name:**

- **Service ID**: Unique identifier (UUID) that precisely targets a specific service instance
- **Service Name**: Human-readable name that may not be unique. If multiple services have the same name, one will be randomly selected

**Usage Patterns:**

There are two main ways to use remote toolsets:

**1. Same Process (Local)** - Start toolset in your script:

.. code-block:: python

   from pantheon.agent import Agent
   from pantheon.toolsets.python import PythonInterpreterToolSet
   from pantheon.toolsets.utils.toolset import run_toolsets
   
   # Create and start toolset locally
   toolset = PythonInterpreterToolSet("python_env")
   
   async with run_toolsets([toolset]):
       agent = Agent(
           name="coderun_bot",
           instructions="You are an AI assistant that can run Python code."
       )
       
       # Connect using the service_id
       await agent.remote_toolset(toolset.service_id)
       
       # Now the agent can execute Python code
       response = await agent.run("Calculate fibonacci(10)")

**2. Separate Process/Machine** - Connect to remote toolset:

.. code-block:: python

   # On remote machine, start toolset via command line:
   # python -m pantheon.toolsets.python --service-name "prod-python-01"
   # Output: Service Name: prod-python-01
   #         Service ID: fb7b1900-c660-4618-8c29-4bf6a2d35a37
   
   # On local machine:
   agent = Agent(
       name="analyst",
       instructions="You analyze data using Python."
   )
   
   # RECOMMENDED: Connect using the service ID (precise targeting)
   await agent.remote_toolset("fb7b1900-c660-4618-8c29-4bf6a2d35a37")
   
   # ALTERNATIVE: Connect by name (only if name is unique)
   await agent.remote_toolset("prod-python-01")
   
   # WARNING: If multiple services have the same name
   # This will randomly select one of them:
   await agent.remote_toolset("python-interpreter")  # Not recommended for production

**Starting Toolsets from Command Line:**

.. code-block:: bash

   # Start Python interpreter toolset (with default name)
   python -m pantheon.toolsets.python
   # Output: Service Name: python-interpreter
   #         Service ID: fb7b1900-c660-4618-8c29-4bf6a2d35a37
   
   # Start with custom service name
   python -m pantheon.toolsets.python --service-name "my-python-env"
   # Output: Service Name: my-python-env
   #         Service ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
   
   # Start R interpreter toolset  
   python -m pantheon.toolsets.r --service-name "data-analysis-r"
   
   # Start shell toolset
   python -m pantheon.toolsets.shell --service-name "secure-shell"

**Custom Magique Server:**

.. code-block:: python

   # If running your own Magique server
   await agent.remote_toolset(
       "python-interpreter",
       server_url="ws://localhost:8765"
   )
   
   # Multiple servers for redundancy
   await agent.remote_toolset(
       "python-interpreter", 
       server_url=[
           "ws://server1:8765",
           "ws://server2:8765"
       ]
   )

chat()
~~~~~~

Start an interactive REPL (Read-Eval-Print Loop) chat session with the agent. This provides a command-line interface for chatting with the agent.

.. code-block:: python

   async def chat(
       message: str | dict | None = None
   ) -> None

**Parameters:**

- ``message`` (str | dict): Optional initial message to start the conversation

**Examples:**

.. code-block:: python

   # Start interactive chat
   await agent.chat()
   # User can now type messages and see responses
   
   # Start with an initial message
   await agent.chat("Hello! What can you help me with?")
   
   # Start with a complex message
   await agent.chat({
       "role": "user",
       "content": "Let's work on a Python project together"
   })

The chat interface provides:

- Interactive conversation with the agent
- Automatic conversation history
- Tool execution visualization
- Graceful exit with Ctrl+C or typing 'exit'

serve()
~~~~~~~

Serve the agent as a remote service that other agents or applications can connect to. This turns the agent into a network-accessible service.

.. code-block:: python

   async def serve(
       **kwargs
   ) -> str

**Parameters:**

- ``**kwargs``: Service configuration options including:
  
  - ``host`` (str): Host to bind to (default: "0.0.0.0")
  - ``port`` (int): Port to listen on (default: auto-assigned)
  - ``auth_token`` (str): Optional authentication token
  - ``ssl_cert`` (str): Path to SSL certificate
  - ``ssl_key`` (str): Path to SSL key

**Returns:**

- ``str``: The service ID that clients can use to connect

**Examples:**

.. code-block:: python

   # Basic serving
   service_id = await agent.serve()
   print(f"Agent serving with ID: {service_id}")
   
   # Serve on specific port
   service_id = await agent.serve(
       host="0.0.0.0",
       port=8080
   )
   
   # Serve with authentication
   service_id = await agent.serve(
       port=8443,
       auth_token="my-secret-token"
   )
   
   # Client code (on another machine)
   from pantheon.agent import RemoteAgent
   
   remote_agent = RemoteAgent(service_id)
   response = await remote_agent.run("Hello remote agent!")
   
   # Or with explicit URL
   remote_agent = RemoteAgent(
       "http://agent-server:8080",
       auth_token="my-secret-token"
   )

Tool Requirements
~~~~~~~~~~~~~~~~~

Tools must follow these requirements:

1. **Type Hints**: All parameters must have type annotations
2. **Docstring**: Must include a description
3. **Return Value**: Should return JSON-serializable data

.. code-block:: python

   @agent.tool
   def good_tool(
       text: str,
       count: int = 10,
       include_metadata: bool = False
   ) -> Dict[str, Any]:
       """
       Process text with specified parameters.
       
       Args:
           text: The text to process
           count: Number of results to return
           include_metadata: Whether to include metadata
           
       Returns:
           Dictionary with processed results
       """
       results = process_text(text, count)
       
       if include_metadata:
           results["metadata"] = get_metadata()
           
       return results

Memory Integration
------------------

Conversation Memory
~~~~~~~~~~~~~~~~~~~

Agents automatically track conversation history with built-in memory:

.. code-block:: python

   from pantheon.agent import Agent
   from pantheon.memory import Memory
   
   # Memory is enabled by default
   agent = Agent(
       name="assistant",
       instructions="You are a helpful assistant.",
       use_memory=True  # Default
   )
   
   # Conversations are automatically remembered
   await agent.run("Remember my name is Alice")
   await agent.run("What's my name?")
   # Agent responds: "Your name is Alice"
   
   # Disable memory for specific runs
   await agent.run(
       "This won't be remembered",
       use_memory=False
   )
   
   # Use custom memory instance
   custom_memory = Memory("user_session_123")
   agent = Agent(
       name="assistant",
       instructions="You are a helpful assistant.",
       memory=custom_memory
   )

Memory Persistence
~~~~~~~~~~~~~~~~~~

Save and load conversation history:

.. code-block:: python

   # Save memory to file
   agent.memory.save("conversation.json")
   
   # Load memory from file
   loaded_memory = Memory.load("conversation.json")
   agent = Agent(
       name="assistant",
       instructions="You are a helpful assistant.",
       memory=loaded_memory
   )
   
   # Access message history directly
   messages = agent.memory.get_messages()
   print(f"Conversation has {len(messages)} messages")
   
   # Add custom data to memory
   agent.memory.extra_data["user_preferences"] = {
       "theme": "dark",
       "language": "en"
   }

Advanced Features
-----------------

Context Variables
~~~~~~~~~~~~~~~~~

Pass additional context to agents and tools:

.. code-block:: python

   response = await agent.run(
       "Get my profile information",
       context_variables={
           "user_id": "123",
           "session_id": "abc",
           "user_role": "admin",
           "timestamp": datetime.now()
       }
   )
   
   # Access context variables in tools
   @agent.tool
   def get_user_data(field: str, context_variables: dict) -> str:
       """Get user data based on context."""
       user_id = context_variables.get("user_id")
       return fetch_user_field(user_id, field)

Model Fallback
~~~~~~~~~~~~~~

Agents can be configured with multiple models for automatic fallback:

.. code-block:: python

   # Single model with automatic fallback to gpt-4.1-mini
   agent = Agent(
       name="assistant",
       model="gpt-4.1",  # Falls back to gpt-4.1-mini if this fails
       instructions="You are a helpful assistant"
   )
   
   # Multiple models in priority order
   agent = Agent(
       name="analyst",
       model=["o3", "gpt-4.1", "gpt-4.1-mini"],
       instructions="Analyze data and provide insights"
   )
   
   # The agent will automatically try each model in order if errors occur

.. _model-selection-providers:

Model Selection and Providers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pantheon agents support virtually any mainstream LLM provider through LiteLLM integration. You just need to provide the corresponding API token for your chosen provider.

**Supported Providers:**

Pantheon supports a wide range of LLM providers including OpenAI, Anthropic, Google, AWS Bedrock, Azure, Cohere, and many more. For a complete list of supported providers, refer to the `LiteLLM documentation <https://docs.litellm.ai/docs/providers>`_.

**Configuration Examples:**

1. **OpenAI (Default)**

.. code-block:: python

   # Using OpenAI models (default provider)
   agent = Agent(
       name="assistant",
       model="gpt-4.1",  # or "gpt-4.1-mini", "o3", etc.
       instructions="You are a helpful assistant."
   )
   # Requires: OPENAI_API_KEY environment variable

2. **Anthropic**

.. code-block:: python

   # Using Anthropic's Claude models
   agent = Agent(
       name="claude_assistant",
       model="anthropic/claude-3-opus-20240229",  # or "anthropic/claude-3-sonnet-20240229"
       instructions="You are a helpful assistant."
   )
   # Requires: ANTHROPIC_API_KEY environment variable

3. **Other Providers**

.. code-block:: python

   # Google Gemini
   agent = Agent(
       name="gemini_agent",
       model="gemini/gemini-pro",
       instructions="Analyze data and provide insights."
   )
   # Requires: GEMINI_API_KEY environment variable
   
   # AWS Bedrock
   agent = Agent(
       name="bedrock_agent",
       model="bedrock/anthropic.claude-3-sonnet-20240229-v1:0",
       instructions="Process documents efficiently."
   )
   # Requires: AWS credentials configured

**Model Selection by Use Case:**

.. code-block:: python

   # For complex reasoning
   reasoning_agent = Agent(
       name="analyzer",
       model="o3",  # OpenAI's reasoning model
       instructions="Analyze complex problems step by step."
   )
   
   # For quick responses
   fast_agent = Agent(
       name="assistant",
       model="gpt-4.1-mini",  # Fast and cost-effective
       instructions="Provide quick, helpful responses."
   )
   
   # For creative tasks
   creative_agent = Agent(
       name="writer",
       model="anthropic/claude-3-opus-20240229",  # Strong creative capabilities
       instructions="Write engaging and creative content."
   )

Structured Output
~~~~~~~~~~~~~~~~~

Get structured responses using Pydantic models:

.. code-block:: python

   from pydantic import BaseModel
   from typing import List
   
   class TaskPlan(BaseModel):
       title: str
       steps: List[str]
       estimated_time: int  # in minutes
       difficulty: str
   
   # Set response format in constructor
   agent = Agent(
       name="planner",
       instructions="You create detailed task plans",
       response_format=TaskPlan
   )
   
   # Or override per run
   response = await agent.run(
       "Plan a machine learning project",
       response_format=TaskPlan
   )
   
   plan = response.content  # This is a TaskPlan instance
   print(f"Title: {plan.title}")
   print(f"Steps: {plan.steps}")

Streaming Responses
~~~~~~~~~~~~~~~~~~~

Process responses as they stream in:

.. code-block:: python

   # Simple streaming
   async def print_stream(chunk):
       if "content" in chunk:
           print(chunk["content"], end="", flush=True)
   
   await agent.run(
       "Write a story about AI",
       process_chunk=print_stream
   )
   
   # Handle different chunk types
   async def handle_chunk(chunk):
       if chunk.get("begin"):
           print("Starting response...")
       elif "content" in chunk:
           print(chunk["content"], end="")
       elif chunk.get("tool_call"):
           print(f"\nCalling tool: {chunk['tool_call']['name']}")
   
   await agent.run(
       "Calculate the factorial of 10",
       process_chunk=handle_chunk
   )

Best Practices
--------------

1. **Clear Instructions**: Write specific, actionable instructions that define the agent's role and behavior
2. **Tool Design**: Create focused tools with clear docstrings and type hints
3. **Model Selection**: Use appropriate models for the task complexity (e.g., gpt-4.1-mini for simple tasks, o3 for complex reasoning)
4. **Memory Usage**: Enable memory for conversational agents, disable for stateless operations
5. **Error Handling**: Configure model fallbacks and handle tool timeouts gracefully
6. **Context Variables**: Use context variables to pass session-specific data to tools
7. **Response Format**: Use structured output (Pydantic models) when you need predictable response schemas

Example Patterns
----------------

**Research Assistant**

.. code-block:: python

   from pantheon.agent import Agent
   from pantheon.toolsets.web_browse import duckduckgo_search, web_crawl
   
   researcher = Agent(
       name="researcher",
       instructions="""You are an expert researcher. You:
       - Search for accurate, up-to-date information
       - Verify facts from multiple sources
       - Always cite your sources
       - Provide balanced perspectives""",
       model="gpt-4.1",
       tools=[duckduckgo_search, web_crawl]
   )

**Data Analyst with Remote Tools**

.. code-block:: python

   analyst = Agent(
       name="data_analyst",
       instructions="You analyze data and create visualizations.",
       model=["gpt-4.1", "gpt-4.1-mini"]  # Fallback models
   )
   
   # Connect to remote Python environment
   await analyst.remote_toolset(
       "python-compute",
       server_url="http://compute-cluster:8000"
   )

**Interactive Assistant**

.. code-block:: python

   assistant = Agent(
       name="assistant",
       instructions="You are a helpful, friendly assistant.",
       icon="🤝",
       use_memory=True  # Remember conversations
   )
   
   # Start interactive chat
   await assistant.chat("Hello! How can I help you today?")