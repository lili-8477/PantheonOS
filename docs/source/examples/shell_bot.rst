Shell Bot
=========

A system administration agent that can execute shell commands and perform system-level operations in a secure environment.

Overview
--------

The Shell Bot demonstrates how to create an agent with shell command execution capabilities. It uses the ShellToolSet to provide controlled access to system commands, making it ideal for system administration, file operations, and automation tasks.

Features
--------

- **Shell Command Execution**: Execute shell/bash commands safely
- **System Administration**: Perform system-level operations and monitoring
- **File Operations**: Create, modify, and manage files and directories
- **Process Management**: Monitor and manage system processes
- **Network Operations**: Basic network diagnostics and operations
- **Automation**: Automate repetitive system tasks

Code
----

.. literalinclude:: ../../../examples/chatbots/shell_bot.py
   :language: python
   :caption: shell_bot.py
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

3. Ensure you have appropriate permissions for the commands you want to execute.

Running the Bot
~~~~~~~~~~~~~~~

1. Navigate to the examples directory:

   .. code-block:: bash

      cd examples/chatbots

2. Run the shell bot:

   .. code-block:: bash

      python shell_bot.py

3. Start managing your system! The bot can execute shell commands and provide results.

Example Usage
-------------

.. code-block:: text

   $ python shell_bot.py
   Chat with shell_bot (type 'exit' to quit)
   
   You: Can you show me the current directory and list its contents?
   
   shell_bot: I'll show you the current directory and list its contents.
   
   ```bash
   pwd
   ```
   /home/user/pantheon-agents/examples/chatbots
   
   ```bash
   ls -la
   ```
   total 32
   drwxr-xr-x 2 user user 4096 Jan 15 10:30 .
   drwxr-xr-x 3 user user 4096 Jan 15 10:25 ..
   -rw-r--r-- 1 user user  456 Jan 15 10:30 coderun_bot.py
   -rw-r--r-- 1 user user  398 Jan 15 10:30 shell_bot.py
   -rw-r--r-- 1 user user  421 Jan 15 10:30 r_bot.py
   
   You: Check the system resources and disk usage
   
   shell_bot: I'll check the system resources and disk usage for you.
   
   ```bash
   # Check CPU and memory usage
   top -bn1 | head -5
   ```
   
   ```bash
   # Check disk usage
   df -h
   ```
   
   ```bash
   # Check memory usage
   free -h
   ```
   
   The system is running normally with adequate resources available.

Key Components
--------------

Agent Configuration
~~~~~~~~~~~~~~~~~~~

- **Name**: ``shell_bot``
- **Model**: ``gpt-4.1`` (advanced model for system administration tasks)
- **Tools**: 
  - ``ShellToolSet``: For executing shell commands and system operations

Security Features
~~~~~~~~~~~~~~~~~

- **Sandboxed Execution**: Commands run in a controlled environment
- **Permission Controls**: Respects system permissions and user access
- **Safe Commands**: Focuses on safe, non-destructive operations
- **Output Capture**: Captures both stdout and stderr safely

Customization
-------------

You can customize the shell bot by:

1. **Changing the model**:

   .. code-block:: python

      agent = Agent(
          "shell_bot",
          "You are an AI assistant that can run shell commands.",
          model="gpt-4o",  # Use a different model
      )

2. **Modifying instructions for specific domains**:

   .. code-block:: python

      instructions = """You are a DevOps engineer assistant that can run shell commands.
      Focus on deployment, monitoring, and infrastructure management tasks.
      Always explain the commands before executing them."""

3. **Adding more toolsets**:

   .. code-block:: python

      from pantheon.toolsets.file_editor import FileEditorToolSet
      
      file_toolset = FileEditorToolSet("file_editor")
      toolsets = [toolset, file_toolset]

Use Cases
---------

- **System Monitoring**: Check system resources, processes, and performance
- **File Management**: Create, move, copy, and organize files and directories
- **Log Analysis**: Parse and analyze system and application logs
- **Network Diagnostics**: Test connectivity and network performance
- **Backup Operations**: Create and manage backups of important data
- **Development Support**: Build processes, testing, and deployment automation
- **Troubleshooting**: Diagnose and resolve system issues

Tips
----

- Always understand what a command does before running it
- Use the bot to explain complex shell commands and their options
- The bot can help create shell scripts for automation
- Great for learning system administration concepts
- Be cautious with commands that modify system state
- The bot respects file permissions and user access controls

Security Considerations
-----------------------

- **Limited Scope**: The bot operates within user permissions
- **No Privileged Access**: Cannot execute sudo or root commands by default
- **Safe Defaults**: Focuses on read operations and safe commands
- **Logging**: All commands and outputs are logged for audit purposes

Next Steps
----------

- Try the :doc:`coderun_bot` for combining shell commands with Python
- Explore :doc:`r_bot` for statistical analysis of system data
- Learn about :doc:`../toolsets/shell` for advanced shell features
- Combine with :doc:`../team/swarm_team` for complex automation workflows