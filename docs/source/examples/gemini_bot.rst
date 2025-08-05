Gemini Bot
==========

A Google Gemini-powered code execution agent that demonstrates using Google's Gemini 2.0 Flash model for Python programming tasks.

Overview
--------

The Gemini Bot showcases how to integrate Google's Gemini 2.0 Flash model with Pantheon's agent framework. It combines Google's advanced AI capabilities with Python code execution, providing a powerful tool for programming, data analysis, and computational tasks.

Features
--------

- **Gemini 2.0 Flash Model**: Leverages Google's latest multimodal AI model
- **Python Code Execution**: Execute Python code with Gemini's reasoning
- **Fast Performance**: Optimized for quick responses and efficient processing
- **Multimodal Understanding**: Can work with text, code, and other data types
- **Interactive Sessions**: Maintain state across multiple code executions
- **Cost-Effective**: Uses the efficient Flash variant for optimal performance

Code
----

.. literalinclude:: ../../../examples/chatbots/gemini.py
   :language: python
   :caption: gemini.py
   :linenos:

How to Run
----------

Prerequisites
~~~~~~~~~~~~~

1. Install Pantheon:

   .. code-block:: bash

      pip install pantheon-agents

2. Set up your Google AI API key:

   .. code-block:: bash

      export GOOGLE_API_KEY=your_google_api_key_here

3. Ensure you have access to Google's Gemini API through Google AI Studio.

Running the Bot
~~~~~~~~~~~~~~~

1. Navigate to the examples directory:

   .. code-block:: bash

      cd examples/chatbots

2. Run the Gemini bot:

   .. code-block:: bash

      python gemini.py

3. Start coding with Gemini! The bot can execute Python code using Google's AI model.

Example Usage
-------------

.. code-block:: text

   $ python gemini.py
   Chat with coderun_bot (type 'exit' to quit)
   
   You: Can you create a data visualization showing the relationship between two variables?
   
   coderun_bot: I'll create a data visualization showing the relationship between two variables using Python.
   
   ```python
   import matplotlib.pyplot as plt
   import numpy as np
   from scipy import stats
   
   # Generate sample data with a relationship
   np.random.seed(42)
   x = np.random.normal(10, 2, 100)  # Independent variable
   y = 2.5 * x + np.random.normal(0, 3, 100)  # Dependent variable with noise
   
   # Calculate correlation
   correlation, p_value = stats.pearsonr(x, y)
   
   # Create the visualization
   plt.figure(figsize=(10, 6))
   plt.scatter(x, y, alpha=0.6, color='blue', s=50)
   
   # Add trend line
   z = np.polyfit(x, y, 1)
   p = np.poly1d(z)
   plt.plot(x, p(x), "r--", alpha=0.8, linewidth=2)
   
   plt.xlabel('X Variable')
   plt.ylabel('Y Variable')
   plt.title(f'Relationship Between Variables (r = {correlation:.3f})')
   plt.grid(True, alpha=0.3)
   plt.show()
   
   print(f"Correlation coefficient: {correlation:.3f}")
   print(f"P-value: {p_value:.3f}")
   ```
   
   You: Now analyze this data using machine learning to predict Y from X
   
   coderun_bot: I'll use machine learning to create a predictive model for Y based on X.

Key Components
--------------

Agent Configuration
~~~~~~~~~~~~~~~~~~~

- **Name**: ``coderun_bot``
- **Model**: ``gemini/gemini-2.0-flash`` (Google's latest multimodal model)
- **Tools**: 
  - ``PythonInterpreterToolSet``: For executing Python code

Gemini Model Features
~~~~~~~~~~~~~~~~~~~~~

- **Multimodal Capabilities**: Understands text, code, and other formats
- **Fast Processing**: Optimized Flash variant for quick responses  
- **Advanced Reasoning**: Google's latest AI reasoning capabilities
- **Code Understanding**: Excellent at understanding and generating code
- **Context Awareness**: Maintains context across long conversations

Customization
-------------

You can customize the Gemini bot by:

1. **Using different Gemini models**:

   .. code-block:: python

      agent = Agent(
          "coderun_bot",
          "You are an AI assistant that can run Python code.",
          model="gemini/gemini-2.0-pro",  # Use the Pro variant
      )

2. **Modifying instructions for specific tasks**:

   .. code-block:: python

      instructions = """You are a machine learning engineer that can run Python code.
      Focus on data science, ML model development, and statistical analysis.
      Always explain your approach and interpret the results."""

3. **Adding specialized tools**:

   .. code-block:: python

      from pantheon.toolsets.file_editor import FileEditorToolSet
      
      file_toolset = FileEditorToolSet("file_editor")
      toolsets = [toolset, file_toolset]

Use Cases
---------

- **Data Science**: Advanced data analysis and machine learning
- **Scientific Computing**: Complex mathematical and scientific calculations
- **Rapid Prototyping**: Quick development and testing of algorithms
- **Educational Tool**: Learning programming with Google AI assistance
- **Research**: Experimental code development and analysis
- **Multimodal Projects**: Working with various data types and formats

Advantages of Gemini
--------------------

- **Latest Technology**: Access to Google's newest AI capabilities
- **Multimodal Understanding**: Better handling of complex, mixed content
- **Fast Response Times**: Optimized for quick interactions
- **Cost Efficiency**: Flash variant provides good performance at lower cost
- **Google Integration**: Easy integration with other Google services

Tips
----

- Gemini excels at understanding complex, multimodal requests
- The Flash model is optimized for speed while maintaining quality
- Great for iterative development and exploration
- Handles both simple scripts and complex algorithms well
- Excellent at explaining code and providing insights

Next Steps
----------

- Compare with :doc:`deepseek_bot` to see different AI model approaches
- Try :doc:`reasoning_bot` for structured problem-solving with AI
- Explore :doc:`../team/swarm_team` to combine Gemini with other models
- Learn about :doc:`../toolsets/python_interpreter` for advanced features