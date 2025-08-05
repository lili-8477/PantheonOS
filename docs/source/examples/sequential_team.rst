Sequential Team
===============

A collaborative multi-agent system where agents work in sequence, passing results from one to the next to solve complex tasks through step-by-step collaboration.

Overview
--------

The Sequential Team demonstrates how to create a team of agents that work together in a predetermined order. Each agent contributes their expertise in sequence, building upon the previous agent's output to provide comprehensive solutions.

Features
--------

- **Sequential Processing**: Agents process tasks in a defined order
- **Collaborative Intelligence**: Multiple perspectives on a single problem
- **Cumulative Knowledge**: Each agent builds upon previous responses
- **Specialized Roles**: Different agents with distinct expertise areas
- **Simple Setup**: Easy to configure and extend with additional agents

Code
----

.. literalinclude:: ../../../examples/team/chat_with_seq_team.py
   :language: python
   :caption: chat_with_seq_team.py
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

2. Run the sequential team example:

   .. code-block:: bash

      python chat_with_seq_team.py

3. The team will automatically process the request and show responses from each agent in sequence.

Example Usage
-------------

.. code-block:: text

   $ python chat_with_seq_team.py
   
   Processing request: "Recommend me some books."
   
   scifi_fan: I'd love to recommend some fantastic science fiction books! Here are some must-reads:
   
   1. "Dune" by Frank Herbert - Epic space opera with political intrigue
   2. "The Left Hand of Darkness" by Ursula K. Le Guin - Thought-provoking gender exploration
   3. "Neuromancer" by William Gibson - Cyberpunk classic that defined the genre
   4. "The Martian" by Andy Weir - Hard sci-fi survival story
   5. "Foundation" by Isaac Asimov - Grand-scale galactic empire saga
   
   romance_fan: Building on those great sci-fi recommendations, here are some wonderful romance novels:
   
   1. "Pride and Prejudice" by Jane Austen - Timeless classic with wit and charm
   2. "The Hating Game" by Sally Thorne - Modern enemies-to-lovers workplace romance
   3. "Outlander" by Diana Gabaldon - Time-traveling historical romance
   4. "Beach Read" by Emily Henry - Contemporary romance with depth
   5. "The Seven Husbands of Evelyn Hugo" by Taylor Jenkins Reid - Multi-generational love story
   
   You now have recommendations spanning both science fiction and romance genres!

Key Components
--------------

Team Configuration
~~~~~~~~~~~~~~~~~~

- **Team Type**: ``SequentialTeam`` - Processes agents in order
- **Agents**: 
  - ``scifi_fan``: Specializes in science fiction recommendations
  - ``romance_fan``: Specializes in romance recommendations

Agent Roles
~~~~~~~~~~~

- **Scifi Fan**: Provides science fiction book recommendations and analysis
- **Romance Fan**: Offers romance novel suggestions and insights
- **Sequential Flow**: Romance fan builds upon sci-fi fan's recommendations

Customization
-------------

You can customize the sequential team by:

1. **Adding more agents**:

   .. code-block:: python

      mystery_fan = Agent(
          name="mystery_fan",
          instructions="You are a mystery fan. You like to read mystery books.",
      )
      
      team = SequentialTeam([scifi_fan, romance_fan, mystery_fan])

2. **Changing agent specializations**:

   .. code-block:: python

      data_scientist = Agent(
          name="data_scientist",
          instructions="You are a data scientist. Analyze problems from a data perspective.",
      )
      
      business_analyst = Agent(
          name="business_analyst", 
          instructions="You are a business analyst. Provide business insights.",
      )

3. **Modifying the connection flow**:

   .. code-block:: python

      team = SequentialTeam(
          [agent1, agent2, agent3],
          connect_prompt="Please build upon the previous analysis and add your perspective."
      )

Use Cases
---------

- **Multi-perspective Analysis**: Get different viewpoints on complex topics
- **Content Creation**: Collaborative writing and editing workflows
- **Research Tasks**: Sequential investigation of topics
- **Decision Making**: Step-by-step evaluation processes
- **Educational Content**: Building comprehensive explanations
- **Product Development**: Multi-stage design and review processes

Tips
----

- Agents work in the order they're defined in the list
- Each agent sees the full conversation history
- Use specialized instructions to define clear roles
- Consider the logical flow when ordering agents
- The final agent's response is typically the most comprehensive

Next Steps
----------

- Try the :doc:`swarm_team` for dynamic agent selection
- Explore :doc:`swarm_center_team` for centralized coordination
- Learn about :doc:`moa_team` for mixture-of-agents patterns
- Combine with :doc:`think_then_act` for reasoning workflows