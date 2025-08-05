Swarm Center Team
=================

A centralized multi-agent system with a triage agent that coordinates and routes conversations to the most appropriate specialized agents based on request analysis.

Overview
--------

The Swarm Center Team demonstrates a hub-and-spoke architecture where a central triage agent analyzes incoming requests and intelligently routes them to specialized agents. This pattern provides centralized coordination while maintaining agent expertise.

Features
--------

- **Centralized Coordination**: Triage agent manages all routing decisions
- **Intelligent Request Analysis**: Context-aware agent selection
- **Remote Agent Support**: Integration with distributed agent systems
- **Specialized Expertise**: Focused agents for specific domains
- **Interactive REPL**: Real-time conversation interface
- **Scalable Architecture**: Easy to add new specialized agents

Code
----

.. literalinclude:: ../../../examples/team/chat_with_swarm_center_team.py
   :language: python
   :caption: chat_with_swarm_center_team.py
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

3. For remote agents, ensure the remote agent service is running:

   .. code-block:: bash

      # In a separate terminal, start the remote agent service
      python -m pantheon.remote.service

Running the Team
~~~~~~~~~~~~~~~~

1. Navigate to the examples directory:

   .. code-block:: bash

      cd examples/team

2. Run the swarm center team example:

   .. code-block:: bash

      python chat_with_swarm_center_team.py

3. Start chatting! The triage agent will analyze your requests and route them appropriately.

4. Type 'exit' to quit the interactive session.

Example Usage
-------------

.. code-block:: text

   $ python chat_with_swarm_center_team.py
   Chat with the team (type 'exit' to quit)
   
   You: I need recommendations for science fiction books
   
   Triage: I can see you're looking for science fiction book recommendations. 
   Let me connect you with our sci-fi specialist.
   
   [Routing to Scifi Fan...]
   
   remote_agent_scifi_fan: Excellent! I'd be happy to recommend some great science fiction books:
   
   1. "The Expanse" series by James S.A. Corey - Realistic space politics and physics
   2. "Klara and the Sun" by Kazuo Ishiguro - Beautiful AI consciousness story
   3. "Project Hail Mary" by Andy Weir - Thrilling space survival adventure
   4. "The Fifth Season" by N.K. Jemisin - Award-winning fantasy-sci-fi blend
   
   What specific sci-fi subgenres interest you most?
   
   You: Actually, I'm more interested in romance novels now
   
   Triage: I notice you've shifted to romance novels. Let me route you to our romance specialist.
   
   [Routing to Romance Fan...]
   
   Romance Fan: Perfect! I love helping with romance recommendations. Here are some fantastic options:
   
   1. "Beach Read" by Emily Henry - Contemporary with emotional depth
   2. "The Spanish Love Deception" by Elena Armas - Fake dating academic romance
   3. "People We Meet on Vacation" by Emily Henry - Friends-to-lovers perfection
   4. "The Kiss Quotient" by Helen Hoang - Neurodiverse representation
   
   Would you prefer contemporary, historical, or fantasy romance?
   
   You: exit

Key Components
--------------

Team Architecture
~~~~~~~~~~~~~~~~~

- **Team Type**: ``SwarmCenterTeam`` - Centralized coordination model
- **Triage Agent**: Central coordinator that analyzes and routes requests
- **Specialized Agents**: 
  - ``remote_agent_scifi_fan``: Remote agent for sci-fi expertise
  - ``Romance Fan``: Local agent for romance discussions

Agent Types
~~~~~~~~~~~

- **RemoteAgent**: Distributed agent running on separate service
- **Local Agent**: Standard agent running in the same process
- **Triage Agent**: Coordinator with routing intelligence

Coordination Pattern
~~~~~~~~~~~~~~~~~~~~

- **Hub-and-Spoke**: All communication flows through the triage agent
- **Context Analysis**: Triage agent understands request intent
- **Smart Routing**: Automatic selection of appropriate specialist
- **Seamless Handoffs**: Smooth transitions between agents

Customization
-------------

You can customize the swarm center team by:

1. **Adding more specialized agents**:

   .. code-block:: python

      mystery_fan = Agent(
          name="Mystery Fan", 
          instructions="You are a mystery novel expert.",
          model="gpt-4o-mini",
      )
      
      tech_expert = RemoteAgent("remote_tech_expert")
      
      team = SwarmCenterTeam(triage, [scifi_fan, romance_fan, mystery_fan, tech_expert])

2. **Enhancing triage intelligence**:

   .. code-block:: python

      advanced_triage = Agent(
          name="Advanced Triage",
          instructions="""You are an intelligent triage agent. Analyze requests and route to:
          - scifi_fan: Science fiction, space, technology topics
          - romance_fan: Romance, relationships, love stories
          - mystery_fan: Mystery, thriller, detective stories
          - tech_expert: Programming, software, technical questions
          Provide brief context about why you're routing to each agent.""",
          model="gpt-4",
      )

3. **Creating domain-specific routing**:

   .. code-block:: python

      # Specialized agents for different domains
      medical_expert = RemoteAgent("medical_expert")
      legal_expert = RemoteAgent("legal_expert") 
      financial_expert = Agent(
          name="Financial Expert",
          instructions="You are a financial advisor and investment expert.",
      )

Use Cases
---------

- **Customer Service**: Intelligent routing to appropriate support specialists
- **Consultation Services**: Multi-domain expert networks
- **Educational Platforms**: Subject-specific tutoring systems
- **Technical Support**: Problem-category-specific expert assignment
- **Content Creation**: Genre or topic-specific writing assistance
- **Research Coordination**: Multi-disciplinary research team management

Tips
----

- The triage agent should have clear routing logic in its instructions
- Remote agents provide scalability for distributed deployments
- Consider load balancing when using multiple agents of the same type
- Test routing decisions with various request types
- Monitor agent utilization to optimize team composition

Next Steps
----------

- Try the :doc:`sequential_team` for ordered processing workflows
- Explore :doc:`swarm_team` for peer-to-peer agent coordination
- Learn about :doc:`moa_team` for mixture-of-agents patterns
- Set up :doc:`../remote/index` for distributed agent architectures