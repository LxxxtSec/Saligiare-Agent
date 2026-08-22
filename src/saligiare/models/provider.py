from saligiare.models.base import ModelRequest


class FakeProvider:
    """按固定顺序返回预先保存的文本响应，用于无网络测试。"""

    def __init__(self, responses: tuple[str, ...]) -> None:
        self._responses = tuple(responses)
        self._index = 0
        self._requests: list[ModelRequest] = []

    @property
    def requests(self) -> tuple[ModelRequest, ...]:
        return tuple(self._requests)

    def complete(self, request: ModelRequest) -> str:
        self._requests.append(request)

        if self._index >= len(self._responses):
            raise RuntimeError("fake provider responses are exhausted")

        response = self._responses[self._index]
        self._index += 1
        return response
