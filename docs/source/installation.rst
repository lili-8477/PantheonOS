Installation
============

This guide will help you install Pantheon and set up your environment.

Basic Installation
------------------

Install from PyPI
~~~~~~~~~~~~~~~~~

.. note::

   Pantheon is not yet available on PyPI. Please use the source installation method below.

.. code-block:: bash

   pip install pantheon-agents  # Coming soon!

Install from Source
~~~~~~~~~~~~~~~~~~~

For the latest development version:

.. code-block:: bash

   git clone https://github.com/aristoteleo/pantheon-agents.git
   cd pantheon-agents
   pip install -e .

Dependencies
------------

Core dependencies are automatically installed with the package:

- Python 3.10+
- asyncio support
- Various LLM client libraries

Optional dependencies for specific toolsets:

- **Python code execution**: Installed by default
- **R support**: Requires R installation
- **Web browsing**: Included via pantheon-toolsets

Next Steps
----------

- :doc:`quickstart` - Create your first agent
- :doc:`examples/index` - Explore example implementations