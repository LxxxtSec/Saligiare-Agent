from saligiare.sandbox.base import SandboxRequest, SandboxResult


class FakeSandbox:
    def __init__(self, results: tuple[SandboxResult, ...]) -> None:
        self._results = tuple(results)
        self._index = 0

    def execute(self, request: SandboxRequest) -> SandboxResult:
        del request

        if self._index >= len(self._results):
            raise RuntimeError("fake sandbox has no more results")

        result = self._results[self._index]
        self._index += 1
        return result
