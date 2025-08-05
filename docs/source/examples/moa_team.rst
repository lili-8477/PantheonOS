MoA Team
========

A Mixture of Agents (MoA) team that combines multiple expert perspectives through layered processing, where specialists provide initial responses and an aggregator synthesizes the final answer.

Overview
--------

The MoA (Mixture of Agents) Team demonstrates a powerful pattern where multiple expert agents independently analyze a problem, and an aggregator agent synthesizes their diverse perspectives into a comprehensive response. This approach leverages collective intelligence for complex problem-solving.

Features
--------

- **Multi-Expert Analysis**: Multiple specialists provide independent perspectives
- **Layered Processing**: Multiple rounds of refinement and analysis
- **Intelligent Aggregation**: Synthesis of diverse expert opinions
- **Domain Expertise**: Specialized knowledge from different fields
- **Comprehensive Solutions**: Rich, multi-faceted responses
- **Configurable Layers**: Adjustable depth of analysis

Code
----

.. literalinclude:: ../../../examples/team/chat_with_moa_team.py
   :language: python
   :caption: chat_with_moa_team.py
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

2. Run the MoA team example:

   .. code-block:: bash

      python chat_with_moa_team.py

3. The team will automatically process the question "What is life?" and show responses from all experts followed by the aggregated answer.

Example Usage
-------------

.. code-block:: text

   $ python chat_with_moa_team.py
   
   Processing question: "What is life?"
   
   === Expert Responses (Layer 1) ===
   
   biologist: From a biological perspective, life is characterized by several key properties:
   
   1. **Organization**: Living things are highly organized structures
   2. **Metabolism**: They obtain and use energy to maintain themselves
   3. **Growth and Development**: They grow and change over time
   4. **Reproduction**: They can create offspring
   5. **Response to Environment**: They react to stimuli
   6. **Homeostasis**: They maintain internal stability
   7. **Evolution**: They adapt and change over generations
   
   physicist: From a physics standpoint, life represents a fascinating departure from equilibrium:
   
   1. **Entropy Reduction**: Living systems create order from disorder
   2. **Energy Dissipation**: Life requires continuous energy flow
   3. **Thermodynamic Processes**: Metabolic reactions follow physical laws
   4. **Information Processing**: DNA stores and processes information
   5. **Emergence**: Complex behaviors arise from simple physical interactions
   6. **Non-equilibrium Systems**: Life exists far from thermodynamic equilibrium
   
   computer_scientist: From a computational perspective, life can be understood as:
   
   1. **Information Processing**: DNA as a program, cells as processors
   2. **Self-Replication**: Ability to copy and execute code
   3. **Algorithms**: Biological processes as computational algorithms
   4. **Networks**: Complex interconnected systems
   5. **Emergence**: Simple rules creating complex behaviors
   6. **Adaptation**: Learning and optimization over time
   
   === Aggregated Response ===
   
   aggregator: Synthesizing these expert perspectives, life emerges as a remarkable phenomenon that can be understood through multiple complementary lenses:
   
   **Biological Foundation**: Life is fundamentally characterized by organization, metabolism, growth, reproduction, environmental response, homeostasis, and evolution.
   
   **Physical Reality**: Life represents a unique thermodynamic phenomenon - organized systems that maintain order by continuously dissipating energy, existing far from equilibrium while following physical laws.
   
   **Computational Nature**: Life operates as sophisticated information processing systems, with DNA serving as both data storage and executable code, creating complex behaviors through algorithmic processes.
   
   **Unified Understanding**: Life is best understood as an emergent property that arises when physical matter organizes into self-maintaining, self-replicating, information-processing systems that can adapt and evolve. It represents the intersection of chemistry, physics, and information science - a bridge between the inanimate and the complex.
   
   This multi-disciplinary view reveals life as both a natural phenomenon following universal laws and a unique emergent property that transcends simple physical or chemical descriptions.

Key Components
--------------

Team Architecture
~~~~~~~~~~~~~~~~~

- **Team Type**: ``MoATeam`` - Mixture of Agents with aggregation
- **Expert Agents**: Multiple specialists with domain expertise
- **Aggregator Agent**: Synthesizes expert responses
- **Processing Layers**: Configurable depth (default: 2 layers)

Expert Specialists
~~~~~~~~~~~~~~~~~~

- **Biologist**: Biological and life sciences perspective
- **Physicist**: Physical sciences and thermodynamics viewpoint  
- **Computer Scientist**: Computational and algorithmic analysis
- **Aggregator**: Information synthesis and integration specialist

Processing Flow
~~~~~~~~~~~~~~~

- **Parallel Processing**: All experts analyze the question simultaneously
- **Independent Analysis**: Each expert provides their domain perspective
- **Aggregation Phase**: Aggregator synthesizes all expert responses
- **Layered Refinement**: Multiple rounds for complex questions

Customization
-------------

You can customize the MoA team by:

1. **Adding more expert agents**:

   .. code-block:: python

      philosopher = Agent(
          name="philosopher",
          instructions="You are a philosopher. Analyze questions from philosophical perspectives.",
      )
      
      psychologist = Agent(
          name="psychologist", 
          instructions="You are a psychologist. Provide psychological insights.",
      )
      
      team = MoATeam([biologist, physicist, computer_scientist, philosopher, psychologist], aggregator, layers=2)

2. **Adjusting processing layers**:

   .. code-block:: python

      # Single layer for simple questions
      team = MoATeam([expert1, expert2, expert3], aggregator, layers=1)
      
      # Multiple layers for complex analysis
      team = MoATeam([expert1, expert2, expert3], aggregator, layers=3)

3. **Specialized aggregation**:

   .. code-block:: python

      specialized_aggregator = Agent(
          name="research_synthesizer",
          instructions="""You are a research synthesizer. Your role is to:
          1. Identify common themes across expert responses
          2. Highlight unique insights from each domain
          3. Resolve any contradictions or conflicts
          4. Present a unified, comprehensive conclusion
          5. Note areas where further research might be needed""",
      )

Use Cases
---------

- **Research Analysis**: Multi-disciplinary investigation of complex topics
- **Strategic Planning**: Business decisions requiring diverse expertise
- **Medical Consultation**: Multiple medical specialists reviewing cases
- **Academic Research**: Interdisciplinary studies and publications
- **Policy Development**: Multi-stakeholder analysis and recommendations
- **Creative Projects**: Diverse perspectives on artistic or design challenges

Tips
----

- Use experts with genuinely different domain knowledge
- Ensure the aggregator can effectively synthesize diverse viewpoints
- Consider increasing layers for highly complex questions
- Test with questions that benefit from multiple perspectives
- Monitor for redundancy vs. complementary insights

Next Steps
----------

- Try the :doc:`sequential_team` for ordered processing workflows
- Explore :doc:`swarm_team` for dynamic agent coordination
- Learn about :doc:`swarm_center_team` for centralized routing
- Combine with :doc:`think_then_act` for reasoning-action patterns