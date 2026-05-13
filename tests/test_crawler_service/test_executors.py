import pytest
from crawler_service.executors.http_executor import HttpExecutor


@pytest.mark.asyncio
async def test_http_executor_fetch_raises_on_bad_url():
    executor = HttpExecutor()
    with pytest.raises(Exception):
        await executor.fetch("http://nonexistent.invalid")
    await executor.close()


@pytest.mark.asyncio
async def test_http_executor_fetch_returns_string():
    executor = HttpExecutor()
    result = await executor.fetch("https://httpbin.org/html")
    assert isinstance(result, str)
    assert len(result) > 0
    await executor.close()
