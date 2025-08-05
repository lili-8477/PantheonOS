Guess Number Game
=================

An interactive number guessing game demonstrating agent tool usage and iterative problem-solving.

Overview
--------

The Guess Number Game showcases how agents can use custom tools to interact with external systems. The agent attempts to guess a randomly generated number between 1 and 100 using a binary search strategy.

Features
--------

- **Custom Tool Integration**: Demonstrates how to create and use custom tools
- **Iterative Problem Solving**: Agent learns from feedback to refine guesses
- **Automatic Strategy**: Agent typically uses binary search for efficiency
- **Simple Yet Effective**: Shows core concepts in a minimal example

Code
----

.. literalinclude:: ../../../examples/guess_number.py
   :language: python
   :caption: guess_number.py
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

Running the Game
~~~~~~~~~~~~~~~~

1. Navigate to the examples directory:

   .. code-block:: bash

      cd examples

2. Run the game:

   .. code-block:: bash

      python guess_number.py

3. Watch as the agent attempts to guess the number!

Example Usage
-------------

.. code-block:: text

   $ python guess_number.py
   Start guessing, the truth is 42
   Guess: 50
   You guessed too high!
   Guess: 25
   You guessed too low!
   Guess: 37
   You guessed too low!
   Guess: 43
   You guessed too high!
   Guess: 40
   You guessed too low!
   Guess: 42
   You guessed the number correctly!
   I successfully guessed the number! It was 42.

Key Components
--------------

Custom Tool Function
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def validate_guess(guess: int) -> str:
       if guess == number:
           return "You guessed the number correctly!"
       elif guess < number:
           return "You guessed too low!"
       else:
           return "You guessed too high!"

The ``validate_guess`` function:

- Takes an integer guess as input
- Compares it to the target number
- Returns feedback to guide the agent

Agent Configuration
~~~~~~~~~~~~~~~~~~~

- **Name**: ``guesser``
- **Instructions**: Simple directive to guess the number
- **Tools**: Custom ``validate_guess`` function
- **Model**: Uses default model (gpt-4o-mini)

Customization
-------------

1. **Change the number range**:

   .. code-block:: python

      number = random.randint(1, 1000)  # Larger range
      resp = await agent.run("Guess the number between 1 and 1000.")

2. **Add more complex feedback**:

   .. code-block:: python

      def validate_guess(guess: int) -> str:
           diff = abs(guess - number)
           if guess == number:
               return "Correct!"
           elif diff <= 5:
               return f"Very close! {'Higher' if guess < number else 'Lower'}"
           elif diff <= 20:
               return f"Getting warm! {'Higher' if guess < number else 'Lower'}"
           else:
               return f"Cold! {'Higher' if guess < number else 'Lower'}"

3. **Track number of attempts**:

   .. code-block:: python

      attempts = 0
      
      def validate_guess(guess: int) -> str:
           global attempts
           attempts += 1
           # ... validation logic ...
           return f"Attempt {attempts}: {msg}"

Use Cases
---------

- **Tool Usage Demo**: Teaching how agents interact with custom tools
- **Strategy Testing**: Observing agent problem-solving approaches
- **Interactive Games**: Building more complex game mechanics
- **Debugging Practice**: Understanding agent decision-making

How It Works
------------

1. A random number is generated between 1 and 100
2. The agent receives the task to guess the number
3. The agent makes an initial guess (usually 50)
4. The ``validate_guess`` tool provides feedback
5. The agent adjusts its strategy based on feedback
6. Process repeats until the correct number is found

Agent Strategy
--------------

Most agents will naturally adopt a binary search approach:

1. Start with the middle value (50)
2. If too high, try the middle of the lower range
3. If too low, try the middle of the upper range
4. Continue halving the search space

This typically finds the answer in 6-7 guesses maximum.

Tips
----

- The agent usually discovers optimal strategies independently
- You can guide strategy through more detailed instructions
- Adding memory or context can create more sophisticated games
- Consider adding hints or clues for more complex variations

Variations
----------

1. **Multiple Players**: Have multiple agents compete
2. **Reverse Game**: Agent picks number, you guess
3. **Pattern Guessing**: Guess sequences or patterns
4. **Word Guessing**: Adapt for Hangman-style games

Next Steps
----------

- Explore :doc:`paper_reporter` for a more complex application
- Try :doc:`../team/swarm_team` for multi-agent games
- Read about :doc:`../agent/agent_api` for tool creation details