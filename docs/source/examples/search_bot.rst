Search Bot
==========

A web search agent that can search the internet using DuckDuckGo and crawl web pages for detailed information.

Overview
--------

The Search Bot demonstrates how to create an agent with web browsing capabilities. It combines DuckDuckGo search functionality with web crawling to provide comprehensive information retrieval.

Features
--------

- **Web Search**: Uses DuckDuckGo API for privacy-focused web searches
- **Web Crawling**: Can fetch and parse content from specific URLs
- **Interactive Chat**: Provides a conversational interface for queries
- **Real-time Information**: Access to current web content

Code
----

.. literalinclude:: ../../../examples/chatbots/search_bot.py
   :language: python
   :caption: search_bot.py
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

Running the Bot
~~~~~~~~~~~~~~~

1. Navigate to the examples directory:

   .. code-block:: bash

      cd examples/chatbots

2. Run the search bot:

   .. code-block:: bash

      python search_bot.py

3. Start chatting! The bot will respond to your queries with web search results.

Example Usage
-------------

.. code-block:: text

   $ python search_bot.py
   Chat with search_engine_expert (type 'exit' to quit)
   
   You: What are the latest developments in quantum computing?
   
   search_engine_expert: Let me search for the latest information on quantum computing developments...
   
   [The agent searches DuckDuckGo and provides recent findings]
   
   You: Can you get more details from the IBM quantum computing page?
   
   search_engine_expert: I'll crawl the IBM quantum computing page for more detailed information...
   
   [The agent crawls the specified page and extracts relevant content]

Key Components
--------------

Agent Configuration
~~~~~~~~~~~~~~~~~~~

- **Name**: ``search_engine_expert``
- **Model**: ``gpt-4o-mini`` (cost-effective model)
- **Tools**: 
  - ``duckduckgo_search``: For web searches
  - ``web_crawl``: For fetching page content

Customization
-------------

You can customize the search bot by:

1. **Changing the model**:

   .. code-block:: python

      search_engine_expert = Agent(
          model="gpt-4",  # Use a more powerful model
          ...
      )

2. **Modifying instructions**:

   .. code-block:: python

      instructions = """You are a research assistant specializing in 
      academic papers. Focus on finding peer-reviewed sources and 
      scientific publications."""

3. **Adding more tools**:

   .. code-block:: python

      from pantheon.toolsets.file_editor import read_file, write_to_file
      
      tools = [duckduckgo_search, web_crawl, read_file, write_to_file]

Use Cases
---------

- **Research Assistant**: Gather information on specific topics
- **News Aggregator**: Find latest news and developments
- **Fact Checker**: Verify information from multiple sources
- **Content Discovery**: Find relevant websites and resources

Tips
----

- Be specific in your search queries for better results
- Use the web crawl feature to dive deeper into interesting results
- The bot can handle follow-up questions based on previous searches
- Consider rate limits when making multiple searches

Next Steps
----------

- Try the :doc:`coderun_bot` for code execution capabilities
- Explore :doc:`../team/swarm_team` to combine search with other agents
- Read about :doc:`../toolsets/web_browse` for more web tools