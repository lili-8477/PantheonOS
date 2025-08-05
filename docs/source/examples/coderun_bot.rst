Code Run Bot
============

A Python code execution agent that can run and execute Python code interactively in a secure environment.

Overview
--------

The Code Run Bot demonstrates how to create an agent with Python code execution capabilities. It uses the PythonInterpreterToolSet to provide a safe, isolated environment for running Python code and returning results.

Features
--------

- **Python Code Execution**: Execute Python code in a secure, isolated environment
- **Interactive Sessions**: Maintain state across multiple code executions
- **Real-time Output**: See code execution results immediately
- **Error Handling**: Proper error reporting for debugging
- **Secure Environment**: Sandboxed execution to prevent system interference

Code
----

.. literalinclude:: ../../../examples/chatbots/coderun_bot.py
   :language: python
   :caption: coderun_bot.py
   :linenos:

How to Run
----------

Prerequisites
~~~~~~~~~~~~~

1. Install Pantheon:

   .. code-block:: bash

      pip install pantheon-agents

2. Set up your OpenAI API key:

   .. code-block:: bash

      export OPENAI_API_KEY=your_api_key_here

Running the Bot
~~~~~~~~~~~~~~~

1. Navigate to the examples directory:

   .. code-block:: bash

      cd examples/chatbots

2. Run the code execution bot:

   .. code-block:: bash

      python coderun_bot.py

3. Start coding! The bot can execute Python code and provide results.

Example Usage
-------------

.. code-block:: text

   $ python coderun_bot.py
   Chat with coderun_bot (type 'exit' to quit)
   
   You: Can you calculate the factorial of 10?
   
   coderun_bot: I'll calculate the factorial of 10 for you.
   
   ```python
   import math
   result = math.factorial(10)
   print(f"The factorial of 10 is: {result}")
   ```
   
   The factorial of 10 is: 3628800
   
   You: Now create a simple plot showing the first 10 factorials
   
   coderun_bot: I'll create a plot showing the first 10 factorials.
   
   ```python
   import matplotlib.pyplot as plt
   import math
   
   numbers = list(range(1, 11))
   factorials = [math.factorial(n) for n in numbers]
   
   plt.figure(figsize=(10, 6))
   plt.plot(numbers, factorials, 'bo-')
   plt.xlabel('Number')
   plt.ylabel('Factorial')
   plt.title('Factorials of Numbers 1-10')
   plt.yscale('log')  # Use log scale due to rapid growth
   plt.grid(True)
   plt.show()
   ```
   
   [Plot is displayed]

Key Components
--------------

Agent Configuration
~~~~~~~~~~~~~~~~~~~

- **Name**: ``coderun_bot``
- **Model**: ``gpt-4.1`` (advanced reasoning model)
- **Tools**: 
  - ``PythonInterpreterToolSet``: For executing Python code

Toolset Features
~~~~~~~~~~~~~~~~

- **Isolated Environment**: Code runs in a separate process
- **State Persistence**: Variables persist across executions
- **Package Support**: Access to common Python packages
- **Output Capture**: Both stdout and visual outputs are captured

Customization
-------------

You can customize the code execution bot by:

1. **Changing the model**:

   .. code-block:: python

      agent = Agent(
          "coderun_bot",
          "You are an AI assistant that can run Python code.",
          model="gpt-4o",  # Use a different model
      )

2. **Modifying instructions**:

   .. code-block:: python

      instructions = """You are a data science assistant that can run Python code.
      Focus on data analysis, visualization, and machine learning tasks.
      Always explain your code and provide insights from the results."""

3. **Adding more toolsets**:

   .. code-block:: python

      from pantheon.toolsets.file_editor import FileEditorToolSet
      
      file_toolset = FileEditorToolSet("file_editor")
      toolsets = [toolset, file_toolset]

Use Cases
---------

- **Data Analysis**: Analyze datasets and generate insights
- **Mathematical Calculations**: Perform complex calculations and proofs
- **Prototyping**: Quickly test algorithms and ideas
- **Educational Tool**: Learn programming through interactive examples
- **Visualization**: Create charts, graphs, and plots
- **Scientific Computing**: Numerical simulations and modeling

Tips
----

- The bot can install packages using pip if needed
- Variables and imports persist across the conversation
- Use descriptive variable names for better code understanding
- The bot can generate and explain complex algorithms
- Visual outputs like plots are displayed automatically

Next Steps
----------

- Try the :doc:`r_bot` for R statistical computing capabilities
- Explore :doc:`shell_bot` for system administration tasks
- Learn about :doc:`../toolsets/python_interpreter` for advanced features
- Combine with :doc:`../team/swarm_team` for collaborative coding