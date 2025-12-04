class _AsyncContextManager:
    """Context manager for async dependencies"""

    def __init__(self, value, generator=None):
        self.value = value
        self.generator = generator

    async def __aenter__(self):
        return self.value

    async def __aexit__(self, exc_type, exc_val, exc_tb):

        # - Clean up generator if present

        if self.generator:
            try:
                await self.generator.__anext__()
            except StopAsyncIteration:
                pass

        return False


async def test():

    # - Test basic context manager without generator

    cm = _AsyncContextManager("test_value")

    async with cm as value:
        assert value == "test_value"

    # - Test context manager with generator cleanup

    async def test_generator():
        yield "yielded_value"

    gen = test_generator()
    result = await gen.__anext__()

    cm_with_gen = _AsyncContextManager(result, gen)

    async with cm_with_gen as value:
        assert value == "yielded_value"
