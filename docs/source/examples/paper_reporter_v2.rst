Paper Reporter V2
=================

Enhanced academic paper analysis system with task-based workflow and improved extraction capabilities.

Overview
--------

Paper Reporter V2 is an improved version that uses Pantheon's Task and TasksSolver framework for more structured paper collection and analysis. It provides better content extraction, filtering, and report generation with automatic retry logic.

Features
--------

- **Task-Based Workflow**: Structured approach using TasksSolver
- **Enhanced Extraction**: Better paper metadata and content extraction
- **Automatic Retries**: Ensures sufficient papers are collected
- **File Management**: Integrated file reading/writing capabilities
- **Quality Filtering**: Multi-stage filtering for relevant papers
- **Progress Tracking**: Step-by-step task execution visibility

Code
----

.. literalinclude:: ../../../examples/paper_reporter_v2/paper_reporter.py
   :language: python
   :caption: paper_reporter.py
   :linenos:

How to Run
----------

Prerequisites
~~~~~~~~~~~~~

1. Install Pantheon and dependencies:

   .. code-block:: bash

      pip install pantheon-agents
      python -m playwright install --with-deps chromium

2. Set up your OpenAI API key:

   .. code-block:: bash

      export OPENAI_API_KEY=your_api_key_here

Running the Reporter
~~~~~~~~~~~~~~~~~~~~

1. Navigate to the examples directory:

   .. code-block:: bash

      cd examples/paper_reporter_v2

2. Run the reporter:

   .. code-block:: bash

      python paper_reporter.py

3. The report will be saved to ``report.md`` in the current directory

Example Usage
-------------

.. code-block:: text

   $ python paper_reporter.py
   
   Task: Collect papers
   Step 1: Generating keywords for theme...
   Step 2: Searching for papers (found 35 results)...
   Step 3: Filtering to keep only academic papers...
   Step 4: Crawling URLs and extracting content...
   Step 5: Filtering by relevance to theme...
   Step 6: Counting papers (22 papers found)...
   Step 8: Writing markdown report to ./report.md...
   
   Task completed successfully!

Key Components
--------------

Task Definition
~~~~~~~~~~~~~~~

The system uses a single comprehensive task with 8 steps:

1. Generate search keywords
2. Search for at least 30 papers
3. Filter to keep only academic papers
4. Extract detailed information from each paper
5. Filter by theme relevance
6. Count filtered papers
7. Retry if less than 20 papers found
8. Write final markdown report

Enhanced Functions
~~~~~~~~~~~~~~~~~~

**crawl_and_extract**: Combines web crawling with content extraction:

.. code-block:: python

   async def crawl_and_extract(urls: list[str]) -> list[str]:
       contents = await web_crawl(urls)
       extracted_contents = []
       for content in contents:
           extracted_content = await extract_content(content)
           extracted_contents.append(extracted_content)
       return extracted_contents

Agent Configuration
~~~~~~~~~~~~~~~~~~~

- **Name**: Search Agent
- **Model**: GPT-4 (more powerful than V1)
- **Tools**: Web search, crawling, file operations
- **Role**: Search engine expert

Differences from V1
-------------------

1. **Architecture**: Uses Task/TasksSolver instead of smart functions
2. **Workflow**: Single comprehensive task vs multiple function calls
3. **Extraction**: Dedicated extraction step for better quality
4. **Retry Logic**: Automatic retry if insufficient papers
5. **File Operations**: Built-in file management tools
6. **Model**: Uses GPT-4 for better accuracy

Customization
-------------

1. **Change the theme**:

   .. code-block:: python

      theme = "Quantum machine learning algorithms"

2. **Adjust paper requirements**:

   .. code-block:: python

      task = Task(
          "Collect papers",
          f"""...find at least 50 papers...
          ...If the papers after filtering are not enough(less than 30)..."""
      )

3. **Modify extraction fields**:

   .. code-block:: python

      @smart_func(model="gpt-4o-mini")
      async def extract_content(content: str) -> str:
           """Extract: authors, title, journal, date, abstract,
           keywords, methodology, key findings, citations"""

4. **Add custom filtering**:

   .. code-block:: python

      # Add to task instructions
      "Filter papers by impact factor > 5"
      "Only include papers from last 3 years"

Example Output
--------------

The generated ``report.md`` includes:

.. code-block:: markdown

   # The Applications of LLM-based Agents in Biology and Medicine
   
   ## Summary
   This report compiles recent research on LLM applications in biological and medical fields...
   
   ## Papers (22 total)
   
   ### 1. LLM-Powered Drug Discovery Pipeline
   - **Authors**: Smith, J., Chen, L., et al.
   - **Journal**: Nature Biotechnology
   - **Date**: March 2024
   - **Abstract**: We present a novel LLM-based system for accelerating drug discovery...
   - **URL**: [Link to paper](https://...)

Use Cases
---------

- **Systematic Reviews**: Comprehensive literature surveys
- **Grant Proposals**: Gather supporting research
- **Trend Analysis**: Track emerging research areas
- **Competitive Intelligence**: Monitor field developments
- **Knowledge Management**: Build research databases

Advantages Over V1
------------------

- **Better Structure**: Clear task-based workflow
- **Higher Quality**: GPT-4 provides better extraction
- **More Robust**: Automatic retry ensures sufficient results
- **Progress Visibility**: Step-by-step execution tracking
- **File Integration**: Direct file operations support

Tips
----

- The task-based approach provides better debugging
- Monitor each step to identify bottlenecks
- Adjust paper count thresholds based on topic specificity
- Consider adding caching for repeated searches
- Export results in multiple formats if needed

Advanced Features
-----------------

1. **Custom Tasks**: Break down into multiple specialized tasks
2. **Parallel Agents**: Use multiple agents for faster processing
3. **Citation Analysis**: Add citation network extraction
4. **Quality Scoring**: Implement paper quality metrics
5. **Incremental Updates**: Add new papers to existing reports

Troubleshooting
---------------

- **Insufficient Papers**: Broaden search keywords or reduce threshold
- **Extraction Errors**: Check if papers are behind paywalls
- **Slow Performance**: Reduce concurrent crawling requests
- **Memory Issues**: Process papers in smaller batches

Next Steps
----------

- Explore :doc:`../team/sequential_team` for multi-stage processing
- Try :doc:`../agent/agent_api` for custom agent creation
- Read about :doc:`../toolsets/file_editor` for file operations