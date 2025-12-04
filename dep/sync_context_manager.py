class _SyncContextManager:
    """Context manager for sync dependencies"""

    def __init__(self, value, generator=None):
        self.value = value
        self.generator = generator

    def __enter__(self):
        return self.value

    def __exit__(self, exc_type, exc_val, exc_tb):

        # - Clean up generator if present

        if self.generator:
            try:
                next(self.generator)
            except StopIteration:
                pass

        return False


def test():

    # - Test basic context manager without generator

    cm = _SyncContextManager("test_value")

    with cm as value:
        assert value == "test_value"

    # - Test context manager with generator cleanup

    def test_generator():
        yield "yielded_value"

    gen = test_generator()
    result = next(gen)

    cm_with_gen = _SyncContextManager(result, gen)

    with cm_with_gen as value:
        assert value == "yielded_value"
