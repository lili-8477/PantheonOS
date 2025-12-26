from pantheon.agent import Agent
from pantheon.endpoint import ToolsetProxy
from pantheon.utils.log import logger
from .template_manager import get_template_manager
from .models import TeamConfig, AgentConfig
from pantheon.settings import get_settings


async def create_agent(
    endpoint_service,
    name: str,
    instructions: str,
    model: str,
    icon: str,
    toolsets: list[str] | None = None,
    mcp_servers: list[str] | None = None,
    description: str | None = None,
    enable_mcp: bool = True,
    **kwargs,
) -> Agent:
    """Create an agent from a template with all providers (toolsets and MCP servers).

    Args:
        endpoint_service: The endpoint service to use for the agent.
        name: The name of the agent.
        instructions: The instructions for the agent.
        model: The model to use for the agent.
        icon: The icon to use for the agent.
        toolsets: List of toolset names to add to the agent.
        mcp_servers: List of MCP server names to add to the agent.
        description: Optional description of the agent's purpose and capabilities.
    """
    agent = Agent(
        name=name,
        instructions=instructions,
        model=model,
        icon=icon,
        description=description,
    )
    agent.not_loaded_toolsets = []
    toolsets_added = []
    mcp_server_added = []
    toolsets = list(toolsets or [])
    mcp_servers = list(mcp_servers or [])
    # ===== Add ToolSet providers from config =====

    for toolset_name in toolsets:
        # Special handling: "task" toolset is local-only (not via Endpoint)
        if toolset_name == "task":
            try:
                from pantheon.toolsets.task import TaskToolSet

                task_toolset = TaskToolSet()
                await agent.toolset(task_toolset)
                toolsets_added.append(toolset_name)
                logger.debug(f"Agent '{name}': Added local TaskToolSet")
            except Exception as e:
                logger.error(f"Agent '{name}': Failed to add local TaskToolSet: {e}")
                agent.not_loaded_toolsets.append(toolset_name)
            continue

        try:
            # Create ToolsetProxy for remote toolsets
            proxy = ToolsetProxy.from_endpoint(endpoint_service, toolset_name)

            from pantheon.providers import ToolSetProvider

            toolset_provider = ToolSetProvider(proxy)
            await toolset_provider.initialize()

            # Add provider to agent
            await agent.toolset(toolset_provider)
            toolsets_added.append(toolset_name)

        except Exception as e:
            logger.error(f"Agent '{name}': Failed to add toolset '{toolset_name}': {e}")
            agent.not_loaded_toolsets.append(toolset_name)

    # ===== Add MCP provider from unified gateway =====
    # All MCP servers are accessible via the unified gateway at /mcp
    # with prefixed tool names (e.g., context7_resolve_library_id)

    if enable_mcp and get_settings().enable_mcp_tools:
        try:
            from pantheon.utils.misc import call_endpoint_method
            from pantheon.providers import MCPProvider

            # Get unified gateway URI (special name="mcp" returns gateway info)
            result = await call_endpoint_method(
                endpoint_service,
                endpoint_method_name="manage_service",
                action="get",
                service_type="mcp",
                name="mcp",  # Special: returns unified gateway URI
            )

            if not result.get("success"):
                raise UserWarning(
                    f"Failed to get unified gateway: {result.get('message', 'Unknown error')}"
                )

            unified_uri = result.get("service", {}).get("uri")
            if not unified_uri:
                raise UserWarning("Unified gateway has no URI configured")

            # Use singleton MCPProvider for the unified gateway
            mcp_provider = MCPProvider.get_instance(unified_uri)
            await mcp_provider.initialize()

            # Add as single "mcp" provider (all tools accessible via prefix)
            await agent.mcp("mcp", mcp_provider)
            mcp_server_added.append("mcp")
            logger.debug(
                f"Agent '{name}': Connected to unified MCP gateway at {unified_uri}"
            )

        except UserWarning as e:
            logger.warning(f"Agent '{name}': {e}")
        except Exception as e:
            logger.error(f"Agent '{name}': Failed to add unified MCP provider: {e}")

    logger.info(
        f"Agent {name} added toolsets: {toolsets_added} mcp_servers: {mcp_server_added}"
    )
    return agent


async def create_agents_from_template(
    endpoint_service, agent_configs: dict, enable_mcp: bool = True
) -> list:
    """Create agents from agent configs."""
    agents = []

    for agent_config in agent_configs.values():
        agent = await create_agent(
            endpoint_service, enable_mcp=enable_mcp, **agent_config
        )
        agents.append(agent)

    return agents


async def create_team_from_template(
    endpoint_service,
    template_id: str,
    learning_config: dict | None = None,
    check_toolsets: bool = True,
    enable_mcp: bool = True,
):
    """Create a PantheonTeam from a template.

    This is the primary factory function for creating teams, suitable for:
    - Benchmark testing
    - Programmatic team creation
    - Learning pipeline team initialization

    Workflow:
    1. Loads the team template by ID
    2. Prepares agent configurations
    3. Optionally checks toolset availability
    4. Creates agents with endpoint connection
    5. Optionally initializes ACE learning/injection resources
    6. Returns a fully initialized PantheonTeam

    Args:
        endpoint_service: The endpoint service for toolset/MCP connections
        template_id: Team template ID (e.g., "default", "data_research_team")
        learning_config: Override for ACE configuration dict. Merged with settings.
                        Keys: enable_learning, enable_injection, learning_model, etc.
        check_toolsets: If True, warns about unavailable toolsets

    Returns:
        PantheonTeam: Fully initialized team ready to run

    Raises:
        ValueError: If template not found

    Example (Pure Learning):
        >>> team = await create_team_from_template(
        ...     endpoint_service,
        ...     "default",
        ...     learning_config={"enable_learning": True, "enable_injection": False},
        ... )

    Example (Pure Injection):
        >>> team = await create_team_from_template(
        ...     endpoint_service,
        ...     "default",
        ...     learning_config={"enable_learning": False, "enable_injection": True},
        ... )
    """
    from pantheon.team import PantheonTeam
    from pantheon.utils.misc import call_endpoint_method

    # 1. Build effective learning config
    _config = get_settings().get_learning_config()
    if learning_config:
        _config.update(learning_config)

    enable_learning = _config.get("enable_learning", False)
    enable_injection = _config.get("enable_injection", enable_learning)

    # 2. Load template
    template_manager = get_template_manager()
    team_config = template_manager.get_template(template_id)
    if not team_config:
        raise ValueError(f"Team template '{template_id}' not found")

    # 3. Prepare team agents
    (
        agent_configs,
        required_toolsets,
        required_mcp_servers,
    ) = template_manager.prepare_team(team_config)

    # 4. Log required toolsets (auto-start handles missing ones on first use)
    if check_toolsets and required_toolsets:
        logger.debug(f"Team '{template_id}' requires toolsets: {required_toolsets}")

    # 5. Create agents
    agents = await create_agents_from_template(
        endpoint_service, agent_configs, enable_mcp=enable_mcp
    )

    # 6. Initialize learning resources
    skillbook = None
    learning_pipeline = None

    if enable_learning or enable_injection:
        from pantheon.internal.learning import create_learning_resources

        skillbook, learning_pipeline = create_learning_resources(config=_config)

    # 7. Create and setup team
    team = PantheonTeam(
        agents=agents,
        learning_pipeline=learning_pipeline,
    )
    await team.async_setup()

    # 8. Inject skills externally (after team creation, before run)
    if skillbook is not None and enable_injection:
        from pantheon.internal.learning import inject_skills_to_team

        await inject_skills_to_team(team, skillbook)

    logger.info(f"Team '{template_id}' created with {len(agents)} agents")
    return team
