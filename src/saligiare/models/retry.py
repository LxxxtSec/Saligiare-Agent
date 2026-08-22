from saligiare.models.base import ModelRequest, TextModelProvider


class ProviderError(RuntimeError):
    """模型 Provider 可以向上层报告的已分类错误。"""


class TransientProviderError(ProviderError):
    """可能因限流、临时网络或服务端暂时不可用而恢复的错误。"""


class PermanentProviderError(ProviderError):
    """不应通过重复请求解决的错误，例如认证或请求格式错误。"""


class RetryingProvider:
    def __init__(
        self,
        provider: TextModelProvider,
        max_attempts: int = 3,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")

        self._provider = provider
        self._max_attempts = max_attempts

    def complete(self, request: ModelRequest) -> str:
        for attempt in range(self._max_attempts):
            try:
                return self._provider.complete(request)
            except TransientProviderError:
                if attempt + 1 == self._max_attempts:
                    raise
            except ProviderError:
                raise

        raise RuntimeError("provider retry loop exited unexpectedly")
