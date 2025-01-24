from . import WebBrowseToolSet
from ...utils.log import logger
import asyncio

toolset = WebBrowseToolSet("web_browse")
logger.info(f"Remote Server: {toolset.worker.server_uri}")
logger.info(f"Service ID: {toolset.service_id}")
asyncio.run(toolset.run())
