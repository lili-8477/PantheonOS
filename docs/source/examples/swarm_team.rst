Swarm Team
==========

A dynamic multi-agent system where agents can transfer control to each other based on the conversation context, allowing for flexible and intelligent task routing.

Overview
--------

The Swarm Team demonstrates how to create a team of agents that can dynamically hand off conversations to the most appropriate agent. Each agent has transfer functions that allow them to route conversations to their teammates when needed.

Features
--------

- **Dynamic Agent Selection**: Agents decide when to transfer control
- **Intelligent Routing**: Context-aware handoffs between agents
- **Interactive REPL**: Real-time conversation interface
- **Flexible Control Flow**: Non-linear conversation paths
- **Specialized Expertise**: Each agent handles their domain optimally

Code
----

.. literalinclude:: ../../../examples/team/chat_with_swarm_team.py
   :language: python
   :caption: chat_with_swarm_team.py
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

Running the Team
~~~~~~~~~~~~~~~~

1. Navigate to the examples directory:

   .. code-block:: bash

      cd examples/team

2. Run the swarm team example:

   .. code-block:: bash

      python chat_with_swarm_team.py

3. Start chatting! Type your messages and see how agents intelligently route the conversation.

4. Type 'exit' to quit the interactive session.

Example Usage
-------------

.. code-block:: text

   $ python chat_with_swarm_team.py
   Chat with the team (type 'exit' to quit)
   
   You: I love science fiction novels, especially space operas
   
   Scifi Fan: Great choice! Space operas are amazing. I'd recommend:
   
   1. "Dune" by Frank Herbert - The ultimate space opera with politics, religion, and ecology
   2. "Foundation" series by Isaac Asimov - Galactic empire and psychohistory
   3. "Hyperion Cantos" by Dan Simmons - Mind-bending far-future epic
   
   Would you like more sci-fi recommendations or are you interested in other genres too?
   
   You: Actually, I'm also curious about romance novels
   
   Romance Fan: Perfect! I love talking about romance. Since you enjoy epic storytelling from sci-fi, 
   you might enjoy these romance novels with grand scope:
   
   1. "Outlander" by Diana Gabaldon - Time-traveling historical romance epic
   2. "The Seven Husbands of Evelyn Hugo" - Multi-generational Hollywood romance
   3. "The Invisible Life of Addie LaRue" - Immortal romance spanning centuries
   
   These have the sweeping narratives you might appreciate from space operas!
   
   You: exit

Key Components
--------------

Team Configuration
~~~~~~~~~~~~~~~~~~

- **Team Type**: ``SwarmTeam`` - Enables dynamic agent switching
- **Agents**: 
  - ``Scifi Fan``: Handles science fiction discussions
  - ``Romance Fan``: Manages romance-related conversations
- **Transfer Functions**: Allow agents to hand off control

Agent Transfer System
~~~~~~~~~~~~~~~~~~~~~

- **@agent.tool decorator**: Creates transfer functions
- **transfer_to_romance_fan()**: Scifi Fan can route to Romance Fan
- **transfer_to_scifi_fan()**: Romance Fan can route back to Scifi Fan
- **Context-aware routing**: Agents decide when transfers are appropriate

Interactive Interface
~~~~~~~~~~~~~~~~~~~~~

- **Repl class**: Provides interactive command-line interface
- **Real-time conversation**: Immediate responses and transfers
- **Exit command**: Clean termination with 'exit'

Customization
-------------

You can customize the swarm team by:

1. **Adding more agents with transfer functions**:

   .. code-block:: python

      mystery_fan = Agent(
          name="Mystery Fan",
          instructions="You are a mystery fan.",
          model="gpt-4o-mini",
      )
      
      @scifi_fan.tool
      def transfer_to_mystery_fan():
          return mystery_fan
      
      @mystery_fan.tool
      def transfer_to_scifi_fan():
          return scifi_fan

2. **Creating specialized transfer conditions**:

   .. code-block:: python

      @agent.tool
      def transfer_to_expert(topic: str):
          """Transfer to the appropriate expert based on topic"""
          if "science" in topic.lower():
              return science_agent
          elif "history" in topic.lower():
              return history_agent
          return general_agent

3. **Modifying agent models and instructions**:

   .. code-block:: python

      expert_agent = Agent(
          name="Domain Expert",
          instructions="You are a highly specialized expert. Provide detailed, technical responses.",
          model="gpt-4",  # Use more powerful model for complex tasks
      )

Use Cases
---------

- **Customer Support**: Route inquiries to appropriate specialists
- **Content Creation**: Dynamic collaboration between different expertise areas
- **Educational Assistance**: Subject-specific tutoring with seamless handoffs
- **Research Projects**: Multi-disciplinary investigation with expert routing
- **Creative Writing**: Genre-specific guidance and collaboration
- **Technical Support**: Problem-specific expert assignment

Tips
----

- Transfer functions should be simple and return the target agent
- Agents will automatically decide when transfers are appropriate
- Use descriptive function names that indicate the transfer purpose
- Consider the conversation flow when designing transfer patterns
- Test transfer logic with various conversation scenarios

Next Steps
----------

- Try the :doc:`sequential_team` for ordered processing
- Explore :doc:`swarm_center_team` for centralized coordination
- Learn about :doc:`moa_team` for mixture-of-agents patterns
- Combine with different :doc:`../toolsets/index` for enhanced capabilities