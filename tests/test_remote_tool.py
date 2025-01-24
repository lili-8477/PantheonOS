import asyncio

from magique.client import MagiqueError
from pantheum.remote import tool, ToolSet, connect_remote
from pantheum.tools.web_browse import WebBrowseToolSet

from executor.engine import Engine, ProcessJob


def test_remote_toolset():
    class MyToolSet(ToolSet):
        @tool(job_type="thread")
        def my_tool(self):
            return "Hello, world!"

    my_toolset = MyToolSet("my_toolset")
    assert len(my_toolset.worker.functions) == 1
    

async def test_web_browse_toolset():
    toolset = WebBrowseToolSet("web_browse")

    async def start_toolset():
        await toolset.run()

    with Engine() as engine:
        job = ProcessJob(start_toolset)
        engine.submit(job)
        await job.wait_until_status("running")
        await asyncio.sleep(3)
        s = await connect_remote(toolset.service_id)
        try:
            res = await s.invoke("duckduckgo_search", {"query": "Hello, world!"})
            assert len(res) > 0
            await job.cancel()
            await engine.wait_async()
        except MagiqueError as e:
            print(e)
