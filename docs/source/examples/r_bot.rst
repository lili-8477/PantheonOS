R Bot
=====

An R statistical computing agent that can execute R code for data analysis, statistical modeling, and visualization.

Overview
--------

The R Bot demonstrates how to create an agent with R programming capabilities. It uses the RInterpreterToolSet to provide access to R's powerful statistical computing environment, making it ideal for data analysis, statistical modeling, and scientific computing tasks.

Features
--------

- **R Code Execution**: Execute R code in a secure, isolated R environment
- **Statistical Analysis**: Access to R's comprehensive statistical libraries
- **Data Visualization**: Create plots and charts using R's visualization capabilities
- **Interactive Sessions**: Maintain R workspace state across multiple executions
- **Package Management**: Install and use R packages as needed
- **Data Import/Export**: Work with various data formats supported by R

Code
----

.. literalinclude:: ../../../examples/chatbots/r_bot.py
   :language: python
   :caption: r_bot.py
   :linenos:

How to Run
----------

Prerequisites
~~~~~~~~~~~~~

1. Install Pantheon:

   .. code-block:: bash

      pip install pantheon-agents

2. Install R on your system:

   .. code-block:: bash

      # Ubuntu/Debian
      sudo apt-get install r-base
      
      # macOS with Homebrew
      brew install r
      
      # Windows: Download from https://cran.r-project.org/

3. Set up your OpenAI API key:

   .. code-block:: bash

      export OPENAI_API_KEY=your_api_key_here

Running the Bot
~~~~~~~~~~~~~~~

1. Navigate to the examples directory:

   .. code-block:: bash

      cd examples/chatbots

2. Run the R bot:

   .. code-block:: bash

      python r_bot.py

3. Start analyzing data! The bot can execute R code and provide statistical insights.

Example Usage
-------------

.. code-block:: text

   $ python r_bot.py
   Chat with r_bot (type 'exit' to quit)
   
   You: Can you perform a basic statistical analysis on some sample data?
   
   r_bot: I'll create some sample data and perform a basic statistical analysis.
   
   ```r
   # Create sample data
   set.seed(123)
   data <- rnorm(100, mean = 50, sd = 10)
   
   # Basic statistics
   summary(data)
   
   # Standard deviation
   sd(data)
   
   # Create a histogram
   hist(data, main = "Distribution of Sample Data", 
        xlab = "Values", col = "lightblue", breaks = 20)
   ```
   
   You: Now can you fit a linear regression model and show the results?
   
   r_bot: I'll create some sample data with a relationship and fit a linear regression model.
   
   ```r
   # Create data with a linear relationship
   x <- 1:50
   y <- 2 * x + rnorm(50, 0, 5)  # y = 2x + noise
   
   # Fit linear model
   model <- lm(y ~ x)
   
   # Show model summary
   summary(model)
   
   # Create scatter plot with regression line
   plot(x, y, main = "Linear Regression Example")
   abline(model, col = "red", lwd = 2)
   
   # Show R-squared
   cat("R-squared:", summary(model)$r.squared, "\n")
   ```

Key Components
--------------

Agent Configuration
~~~~~~~~~~~~~~~~~~~

- **Name**: ``r_bot``
- **Model**: ``gpt-4o`` (advanced model for complex R programming)
- **Tools**: 
  - ``RInterpreterToolSet``: For executing R code and statistical analysis

R Environment Features
~~~~~~~~~~~~~~~~~~~~~~

- **Statistical Functions**: Access to R's comprehensive statistical library
- **Data Manipulation**: Data frames, vectors, and matrix operations
- **Visualization**: Base R graphics and support for ggplot2
- **Package Ecosystem**: Install and use CRAN packages
- **Workspace Persistence**: Variables and objects persist across executions

Customization
-------------

You can customize the R bot by:

1. **Changing the model**:

   .. code-block:: python

      agent = Agent(
          "r_bot",
          "You are an AI assistant that can run R code.",
          model="gpt-4.1",  # Use a different model
      )

2. **Modifying instructions for specific domains**:

   .. code-block:: python

      instructions = """You are a biostatistics expert that can run R code.
      Focus on medical data analysis, survival analysis, and clinical trial
      statistics. Always interpret results in a medical context."""

3. **Adding more toolsets**:

   .. code-block:: python

      from pantheon.toolsets.file_editor import FileEditorToolSet
      
      file_toolset = FileEditorToolSet("file_editor")
      toolsets = [toolset, file_toolset]

Use Cases
---------

- **Statistical Analysis**: Hypothesis testing, ANOVA, regression analysis
- **Data Science**: Exploratory data analysis and predictive modeling
- **Bioinformatics**: Genomic data analysis and biological statistics
- **Financial Analysis**: Time series analysis and risk modeling
- **Market Research**: Survey data analysis and statistical reporting
- **Academic Research**: Statistical analysis for research papers
- **Quality Control**: Statistical process control and quality metrics

Tips
----

- The bot can install R packages using install.packages() if needed
- R objects and variables persist throughout the conversation
- Use descriptive variable names for better code understanding
- The bot can generate complex statistical models and interpret results
- Plots and visualizations are displayed automatically
- Great for both exploratory analysis and formal statistical testing

Next Steps
----------

- Try the :doc:`coderun_bot` for Python-based data analysis
- Explore :doc:`shell_bot` for system-level data processing
- Learn about :doc:`../toolsets/r_interpreter` for advanced R features
- Combine with :doc:`../team/swarm_team` for multi-language data analysis