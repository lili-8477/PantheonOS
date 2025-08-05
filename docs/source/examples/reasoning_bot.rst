Reasoning Bot
=============

An AI assistant with advanced reasoning capabilities using DeepSeek's reasoning model to solve complex problems through structured thinking.

Overview
--------

The Reasoning Bot demonstrates how to create an agent with enhanced reasoning abilities. It uses DeepSeek's reasoning model combined with specialized reasoning tools to break down complex problems and provide detailed, step-by-step solutions.

Features
--------

- **Advanced Reasoning**: Uses DeepSeek's reasoning model for complex problem solving
- **Structured Thinking**: Breaks down problems into logical steps
- **Reasoning Tools**: Specialized tools for enhanced analytical capabilities
- **Step-by-Step Solutions**: Provides detailed explanations of reasoning process
- **Complex Problem Handling**: Tackles mathematical, logical, and analytical challenges

Code
----

.. literalinclude:: ../../../examples/chatbots/reasoning_bot.py
   :language: python
   :caption: reasoning_bot.py
   :linenos:

How to Run
----------

Prerequisites
~~~~~~~~~~~~~

1. Install Pantheon:

   .. code-block:: bash

      pip install pantheon-agents

2. Set up your DeepSeek API key:

   .. code-block:: bash

      export DEEPSEEK_API_KEY=your_api_key_here

3. Ensure you have access to DeepSeek models through your API configuration.

Running the Bot
~~~~~~~~~~~~~~~

1. Navigate to the examples directory:

   .. code-block:: bash

      cd examples/chatbots

2. Run the reasoning bot:

   .. code-block:: bash

      python reasoning_bot.py

3. Start asking complex questions! The bot will use structured reasoning to solve them.

Example Usage
-------------

.. code-block:: text

   $ python reasoning_bot.py
   Chat with reasoning_bot (type 'exit' to quit)
   
   You: If I have 100 people in a room and each person shakes hands with every other person exactly once, how many handshakes occur?
   
   reasoning_bot: Let me solve this step by step using reasoning.
   
   [Using reasoning tool]
   
   I need to find the number of unique handshakes when 100 people each shake hands with every other person exactly once.
   
   Step 1: Understanding the problem
   - We have 100 people
   - Each person shakes hands with every other person
   - Each handshake involves exactly 2 people
   - We need to count unique handshakes (not double count A-B and B-A)
   
   Step 2: Mathematical approach
   This is a combination problem. We need to choose 2 people from 100 people.
   The formula is C(n,2) = n! / (2!(n-2)!) = n(n-1)/2
   
   Step 3: Calculation
   C(100,2) = 100 × 99 / 2 = 9900 / 2 = 4950
   
   Therefore, there will be 4,950 unique handshakes.
   
   You: Now solve this logic puzzle: Three friends Alice, Bob, and Carol are wearing different colored hats (red, blue, green). Alice says "I'm not wearing red", Bob says "I'm wearing blue", and Carol says "I'm not wearing green". If exactly one person is lying, what color hat is each person wearing?

Key Components
--------------

Agent Configuration
~~~~~~~~~~~~~~~~~~~

- **Name**: ``reasoning_bot``
- **Model**: ``deepseek/deepseek-chat`` (DeepSeek's reasoning-optimized model)
- **Tools**: 
  - ``reasoning_deepseek_reasoner``: Specialized reasoning tool for complex problem solving

Reasoning Capabilities
~~~~~~~~~~~~~~~~~~~~~~

- **Logical Analysis**: Breaks down complex logical problems
- **Mathematical Reasoning**: Handles mathematical proofs and calculations
- **Step-by-Step Thinking**: Shows detailed reasoning process
- **Problem Decomposition**: Breaks large problems into manageable parts

Customization
-------------

You can customize the reasoning bot by:

1. **Changing the model**:

   .. code-block:: python

      reasoning_bot = Agent(
          name="reasoning_bot",
          instructions="You are an AI assistant with reasoning abilities.",
          model="gpt-4o",  # Use a different reasoning model
          tools=[reasoning_deepseek_reasoner],
      )

2. **Modifying instructions for specific domains**:

   .. code-block:: python

      instructions = """You are a mathematical reasoning assistant.
      Focus on solving complex mathematical problems, proofs, and
      logical puzzles. Always show your step-by-step reasoning
      and explain each logical step clearly."""

3. **Adding domain-specific context**:

   .. code-block:: python

      instructions = """You are a scientific reasoning assistant
      with expertise in physics and chemistry. Use reasoning to
      solve complex scientific problems and explain natural phenomena."""

Use Cases
---------

- **Mathematical Problem Solving**: Complex equations, proofs, and theorems
- **Logic Puzzles**: Riddles, brain teasers, and logical challenges
- **Strategic Planning**: Breaking down complex decisions into steps
- **Scientific Analysis**: Hypothesis testing and experimental design
- **Philosophical Questions**: Ethical dilemmas and thought experiments
- **Educational Support**: Teaching complex concepts through reasoning

Tips
----

- Ask complex, multi-step questions to see the reasoning in action
- The bot works best with problems that benefit from structured thinking
- Use follow-up questions to dive deeper into specific reasoning steps
- The reasoning tool helps with problems requiring logical deduction
- Best suited for analytical rather than creative tasks

Next Steps
----------

- Try the :doc:`coderun_bot` to combine reasoning with code execution
- Explore :doc:`../team/swarm_team` to combine reasoning with other capabilities
- Learn about :doc:`../toolsets/reasoning` for advanced reasoning features
- Combine with :doc:`search_bot` for research-backed reasoning