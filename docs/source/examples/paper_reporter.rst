Paper Reporter
==============

An automated academic paper analysis system that searches, analyzes, and generates comprehensive reports on research papers.

Overview
--------

The Paper Reporter demonstrates how to build an agentic pipeline for academic research. It automatically searches for papers on a given theme, extracts key information, and generates a well-formatted markdown report.

Features
--------

- **Intelligent Query Generation**: Creates optimal search keywords for academic papers
- **Web Search Integration**: Uses DuckDuckGo to find relevant papers
- **Content Extraction**: Automatically extracts paper metadata and summaries  
- **Relevance Filtering**: Ensures papers match the research theme
- **Report Generation**: Creates formatted markdown reports
- **Async Processing**: Efficient parallel processing of multiple papers

Code
----

.. literalinclude:: ../../../examples/paper_reporter/paper_reporter.py
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

      cd examples/paper_reporter

2. Run with default theme:

   .. code-block:: bash

      python paper_reporter.py

3. Or specify a custom theme:

   .. code-block:: bash

      python paper_reporter.py --theme "AI applications in climate science" --output climate_ai_papers.md

Command Line Options
~~~~~~~~~~~~~~~~~~~~

- ``--theme``: Research theme (default: "The applications of LLM-based agents in biology and medicine")
- ``--output``: Output file path for the markdown report
- ``--model``: LLM model to use (default: "gpt-4o-mini")
- ``--results_per_keyword``: Number of search results per keyword (default: 5)

Example Usage
-------------

.. code-block:: text

   $ python paper_reporter.py --theme "LLM agents in healthcare" --output healthcare_report.md
   
   Query keywords:
   ['LLM agents healthcare applications',
    'large language models medical diagnosis',
    'AI agents clinical decision support',
    'transformer models biomedical research',
    'GPT healthcare automation']
   
   Number of items before relation check: 23
   Number of items after relation check: 12
   
   Markdown:
   # LLM Agents in Healthcare: A Comprehensive Review
   
   This report explores the applications of Large Language Model (LLM) based agents...
   
   ## Papers
   
   1. **Clinical Decision Support Using LLM Agents**
      - *Journal*: Nature Medicine
      - *Date*: March 2024
      - *Summary*: This paper presents a novel framework for deploying LLM agents...

Key Components
--------------

Smart Functions
~~~~~~~~~~~~~~~

The system uses decorated functions that leverage LLMs:

1. **gen_query_keywords**: Generates search queries with DuckDuckGo operators
2. **check_content_is_paper**: Validates if content is an academic paper
3. **extract_paper_info**: Extracts metadata (title, journal, date, summary)
4. **check_paper_relation**: Verifies relevance to research theme
5. **format_paper_info**: Creates the final markdown report

Pipeline Flow
~~~~~~~~~~~~~

1. Generate search keywords based on theme
2. Search for papers using each keyword
3. Merge and deduplicate results
4. Crawl paper URLs to get content
5. Process each paper in parallel:
   - Check if it's a valid paper
   - Extract information
   - Verify relevance
6. Format results into markdown report

Customization
-------------

1. **Change the research theme**:

   .. code-block:: python

      theme = "Quantum computing applications in drug discovery"

2. **Use a different model**:

   .. code-block:: python

      model = "gpt-4"  # More accurate but costlier

3. **Adjust search parameters**:

   .. code-block:: python

      results_per_keyword = 10  # More results per search

4. **Add custom extraction fields**:

   .. code-block:: python

      class ContentInfo(BaseModel):
           title: str
           authors: list[str]  # Add author extraction
           doi: str  # Add DOI extraction
           citations: int  # Add citation count

Example Output
--------------

See ``bioagent.md`` for a sample report on LLM applications in biology.

Use Cases
---------

- **Literature Reviews**: Automated survey of research topics
- **Research Monitoring**: Track new papers in specific fields
- **Grant Writing**: Gather relevant citations and summaries
- **Trend Analysis**: Identify emerging research directions
- **Knowledge Base**: Build curated paper collections

Tips
----

- Use specific themes for better results
- Increase ``results_per_keyword`` for comprehensive coverage
- The web crawling step may take time for many papers
- Some papers behind paywalls may not be fully accessible
- Consider adding retries for failed web requests

Advanced Features
-----------------

1. **Custom Search Operators**: Modify query generation to use site-specific searches
2. **Citation Networks**: Extract and analyze paper citations
3. **Author Analysis**: Track specific researchers' publications
4. **Time Filtering**: Focus on recent papers only
5. **Export Formats**: Add BibTeX or JSON export options

Limitations
-----------

- Depends on publicly accessible paper content
- May miss papers not indexed by search engines
- Quality depends on LLM's understanding of academic content
- Rate limits may affect large-scale searches

Next Steps
----------

- Try :doc:`paper_reporter_v2` for enhanced multi-agent version
- Explore :doc:`../team/moa_team` for collaborative analysis
- Read about :doc:`../toolsets/web_browse` for web tools details