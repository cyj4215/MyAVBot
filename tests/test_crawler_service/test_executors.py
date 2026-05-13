import pytest
from crawler_service.executors.http_executor import HttpExecutor


@pytest.mark.asyncio
async def test_http_executor_fetch_raises_on_bad_url():
    executor = HttpExecutor()
    with pytest.raises(Exception):
        await executor.fetch("http://nonexistent.invalid")
    await executor.close()


@pytest.mark.asyncio
async def test_http_executor_fetch_with_status():
    executor = HttpExecutor()
    status, html = await executor.fetch_with_status("https://example.com")
    assert status == 200
    assert isinstance(html, str)
    assert len(html) > 0
    await executor.close()
