Think Then Act
=============

A reasoning-action workflow that combines a thinking agent with an action agent, where deep reasoning precedes concrete action to solve complex problems effectively.

Overview
--------

The Think Then Act pattern demonstrates a powerful two-stage workflow where a reasoning agent first deeply analyzes the problem, then passes the analysis to an action agent that provides the final answer or takes concrete steps. This pattern is particularly effective for problems requiring careful analysis before action.

Features
--------

- **Two-Stage Processing**: Clear separation between thinking and acting
- **Deep Reasoning**: Specialized reasoning model for analysis
- **Action Execution**: Dedicated agent for final responses and actions
- **Model Specialization**: Different models optimized for different tasks
- **Structured Response**: Controlled output format (e.g., integer responses)
- **Connect Prompts**: Custom transition messages between stages

Code
----

.. literalinclude:: ../../../examples/team/think_then_act.py
   :language: python
   :caption: think_then_act.py
   :linenos:

How to Run
----------

Prerequisites
~~~~~~~~~~~~~

1. Install Pantheon:

   .. code-block:: bash

      pip install pantheon-agents

2. Set up your API keys. This example uses both DeepSeek and OpenAI:

   .. code-block:: bash

      export OPENAI_API_KEY=your_openai_key_here
      export DEEPSEEK_API_KEY=your_deepseek_key_here

Running the Example
~~~~~~~~~~~~~~~~~~~

1. Navigate to the examples directory:

   .. code-block:: bash

      cd examples/team

2. Run the think-then-act example:

   .. code-block:: bash

      python think_then_act.py

3. The system will process the question "How many 'r's in 'strawberry'?" and return the integer result.

Example Usage
-------------

.. code-block:: text

   $ python think_then_act.py
   
   === Thinking Agent Analysis ===
   
   thinking_agent: Let me carefully analyze the word "strawberry" to count the occurrences of the letter 'r'.
   
   The word "strawberry" is spelled: s-t-r-a-w-b-e-r-r-y
   
   Let me go through each letter:
   1. s - not an 'r'
   2. t - not an 'r'  
   3. r - this is an 'r' (1st occurrence)
   4. a - not an 'r'
   5. w - not an 'r'
   6. b - not an 'r'
   7. e - not an 'r'
   8. r - this is an 'r' (2nd occurrence)
   9. r - this is an 'r' (3rd occurrence)
   10. y - not an 'r'
   
   So I count 3 occurrences of the letter 'r' in "strawberry".
   
   === Action Agent Response ===
   
   action_agent: Based on the thorough analysis, the word "strawberry" contains exactly 3 occurrences of the letter 'r'.
   
   Final Result: 3

Key Components
--------------

Team Configuration
~~~~~~~~~~~~~~~~~~

- **Team Type**: ``SequentialTeam`` with custom connect prompt
- **Processing Order**: Thinking agent → Action agent
- **Connect Prompt**: "Now take actions or give the final answer."
- **Response Format**: Structured output (integer in this example)

Agent Specialization
~~~~~~~~~~~~~~~~~~~~

- **Thinking Agent**: 
  - Model: ``deepseek/deepseek-reasoner`` - Specialized for reasoning
  - Role: Deep analysis and problem breakdown
- **Action Agent**:
  - Model: ``gpt-4o-mini`` - Efficient for action execution
  - Role: Final answers and concrete actions

Workflow Pattern
~~~~~~~~~~~~~~~~

1. **Analysis Phase**: Thinking agent provides detailed reasoning
2. **Transition**: Connect prompt guides the handoff
3. **Action Phase**: Action agent delivers final result
4. **Structured Output**: Controlled response format

Customization
-------------

You can customize the think-then-act pattern by:

1. **Changing the reasoning model**:

   .. code-block:: python

      thinking_agent = Agent(
          name="thinking_agent",
          instructions="You are a deep reasoning agent. Think step by step.",
          model="gpt-4",  # Use GPT-4 for reasoning
      )

2. **Modifying the action agent**:

   .. code-block:: python

      action_agent = Agent(
          name="action_agent", 
          instructions="You provide clear, actionable responses based on the analysis.",
          model="claude-3-sonnet",  # Use different model for actions
      )

3. **Customizing the connect prompt**:

   .. code-block:: python

      team = SequentialTeam(
          [thinking_agent, action_agent],
          connect_prompt="Based on this analysis, provide your final recommendation and next steps.",
      )

4. **Adding specialized thinking patterns**:

   .. code-block:: python

      creative_thinker = Agent(
          name="creative_thinker",
          instructions="""You are a creative thinking agent. Use techniques like:
          - Brainstorming multiple approaches
          - Lateral thinking
          - What-if scenarios
          - Alternative perspectives""",
      )

Use Cases
---------

- **Problem Solving**: Complex analytical problems requiring careful thought
- **Decision Making**: High-stakes decisions needing thorough analysis
- **Mathematical Problems**: Step-by-step reasoning before final answers
- **Strategic Planning**: Analysis phase followed by actionable recommendations
- **Research Tasks**: Deep investigation followed by conclusions
- **Creative Projects**: Ideation phase followed by implementation planning

Tips
----

- Use specialized models for each phase (reasoning vs. action)
- Craft clear connect prompts to guide the transition
- Consider response formats that match your use case
- Test with problems that benefit from separate thinking and acting phases
- Monitor the quality of reasoning before action

Next Steps
----------

- Try the :doc:`sequential_team` for more complex multi-agent workflows
- Explore :doc:`moa_team` for multi-expert analysis patterns
- Learn about :doc:`swarm_team` for dynamic agent coordination
- Combine with different :doc:`../toolsets/index` for enhanced capabilities