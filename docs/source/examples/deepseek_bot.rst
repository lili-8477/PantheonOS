DeepSeek Bot
============

A DeepSeek-powered code execution agent that demonstrates using DeepSeek's advanced AI model for Python programming and computational tasks.

Overview
--------

The DeepSeek Bot showcases how to integrate DeepSeek's AI model with Pantheon's agent framework. It combines DeepSeek's powerful reasoning capabilities with Python code execution, providing an excellent tool for programming, mathematical analysis, and computational problem-solving.

Features
--------

- **DeepSeek AI Model**: Leverages DeepSeek's advanced reasoning capabilities
- **Python Code Execution**: Execute Python code with DeepSeek's intelligence
- **Strong Mathematical Reasoning**: Excellent at mathematical and logical problems
- **Code Generation**: Advanced code writing and optimization capabilities
- **Interactive Sessions**: Maintain state across multiple code executions
- **Cost-Effective**: Competitive pricing for high-quality AI reasoning

Code
----

.. literalinclude:: ../../../examples/chatbots/deepseek.py
   :language: python
   :caption: deepseek.py
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

      export DEEPSEEK_API_KEY=your_deepseek_api_key_here

3. Ensure you have access to DeepSeek's API through their platform.

Running the Bot
~~~~~~~~~~~~~~~

1. Navigate to the examples directory:

   .. code-block:: bash

      cd examples/chatbots

2. Run the DeepSeek bot:

   .. code-block:: bash

      python deepseek.py

3. Start coding with DeepSeek! The bot can execute Python code using DeepSeek's AI model.

Example Usage
-------------

.. code-block:: text

   $ python deepseek.py
   Chat with coderun_bot (type 'exit' to quit)
   
   You: Can you solve a complex mathematical optimization problem using Python?
   
   coderun_bot: I'll solve a complex optimization problem for you. Let me create an example 
   involving finding the minimum of a non-linear function with constraints.
   
   ```python
   import numpy as np
   from scipy.optimize import minimize
   import matplotlib.pyplot as plt
   
   # Define the objective function (Rosenbrock function as an example)
   def objective(x):
       return (1 - x[0])**2 + 100 * (x[1] - x[0]**2)**2
   
   # Define constraints
   def constraint1(x):
       return x[0] + x[1] - 1  # x + y >= 1
   
   def constraint2(x):
       return x[0]**2 + x[1]**2 - 4  # x² + y² <= 4
   
   # Set up constraints
   con1 = {'type': 'ineq', 'fun': constraint1}
   con2 = {'type': 'ineq', 'fun': lambda x: -constraint2(x)}
   constraints = [con1, con2]
   
   # Initial guess
   x0 = [0, 0]
   
   # Bounds for variables
   bounds = [(-2, 2), (-2, 2)]
   
   # Solve the optimization problem
   result = minimize(objective, x0, method='SLSQP', 
                    bounds=bounds, constraints=constraints)
   
   print("Optimization Result:")
   print(f"Success: {result.success}")
   print(f"Optimal solution: x = {result.x[0]:.4f}, y = {result.x[1]:.4f}")
   print(f"Minimum value: {result.fun:.4f}")
   print(f"Number of iterations: {result.nit}")
   
   # Visualize the result
   x_range = np.linspace(-2, 2, 100)
   y_range = np.linspace(-2, 2, 100)
   X, Y = np.meshgrid(x_range, y_range)
   Z = (1 - X)**2 + 100 * (Y - X**2)**2
   
   plt.figure(figsize=(10, 8))
   plt.contour(X, Y, Z, levels=50, alpha=0.6)
   plt.colorbar(label='Objective Function Value')
   plt.plot(result.x[0], result.x[1], 'ro', markersize=10, label='Optimal Point')
   plt.xlabel('x')
   plt.ylabel('y')
   plt.title('Optimization Problem Visualization')
   plt.legend()
   plt.grid(True, alpha=0.3)
   plt.show()
   ```
   
   You: Now implement a neural network from scratch to classify data
   
   coderun_bot: I'll implement a neural network from scratch using only NumPy to classify data.

Key Components
--------------

Agent Configuration
~~~~~~~~~~~~~~~~~~~

- **Name**: ``coderun_bot``
- **Model**: ``deepseek/deepseek-chat`` (DeepSeek's reasoning-optimized model)
- **Tools**: 
  - ``PythonInterpreterToolSet``: For executing Python code

DeepSeek Model Features
~~~~~~~~~~~~~~~~~~~~~~~

- **Advanced Reasoning**: Excellent at logical and mathematical reasoning
- **Code Proficiency**: Strong capabilities in code generation and debugging
- **Problem Solving**: Systematic approach to complex problem decomposition
- **Mathematical Excellence**: Superior performance on mathematical tasks
- **Optimization Focus**: Good understanding of algorithmic efficiency

Customization
-------------

You can customize the DeepSeek bot by:

1. **Changing model parameters**:

   .. code-block:: python

      agent = Agent(
          "coderun_bot",
          "You are an AI assistant that can run Python code.",
          model="deepseek/deepseek-coder",  # Use specialized coding model
      )

2. **Modifying instructions for specific domains**:

   .. code-block:: python

      instructions = """You are a research scientist that can run Python code.
      Focus on implementing research algorithms, conducting experiments,
      and analyzing results with rigorous scientific methodology."""

3. **Adding complementary tools**:

   .. code-block:: python

      from pantheon.reasoning import reasoning_deepseek_reasoner
      from pantheon.toolsets.file_editor import FileEditorToolSet
      
      tools = [reasoning_deepseek_reasoner]  # Add reasoning capabilities
      file_toolset = FileEditorToolSet("file_editor")

Use Cases
---------

- **Algorithm Development**: Implementing complex algorithms from scratch
- **Mathematical Computing**: Solving advanced mathematical problems
- **Research Implementation**: Converting research papers into working code
- **Optimization Problems**: Finding optimal solutions to complex problems
- **Machine Learning**: Building and training models with detailed explanations
- **Scientific Computing**: Numerical simulations and scientific calculations

Advantages of DeepSeek
----------------------

- **Strong Reasoning**: Excellent at breaking down complex problems
- **Mathematical Proficiency**: Superior handling of mathematical concepts  
- **Code Quality**: Generates clean, well-structured, and efficient code
- **Cost Effectiveness**: Competitive pricing for enterprise-grade AI
- **Specialized Models**: Offers domain-specific models (coding, reasoning)

Tips
----

- DeepSeek excels at systematic problem-solving approaches
- Great for implementing algorithms that require mathematical understanding
- Provides detailed explanations of complex computational processes
- Excellent at optimizing code for performance and efficiency
- Works well with research-oriented programming tasks

Comparison with Other Models
----------------------------

- **vs GPT models**: Often better at mathematical reasoning and systematic coding
- **vs Gemini**: More focused on logical reasoning, less multimodal
- **vs Claude**: Competitive at coding tasks, excellent mathematical capabilities
- **Cost advantage**: Generally more cost-effective than comparable models

Next Steps
----------

- Compare with :doc:`gemini_bot` to see different AI model approaches
- Try :doc:`reasoning_bot` for enhanced reasoning capabilities with DeepSeek
- Explore :doc:`../team/swarm_team` to combine DeepSeek with other models
- Learn about :doc:`../toolsets/python_interpreter` for advanced features