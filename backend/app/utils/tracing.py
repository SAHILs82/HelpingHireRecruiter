from __future__ import annotations

import os
from functools import wraps
from typing import Any, Callable, TypeVar, cast

from app.core.config import settings

F = TypeVar("F", bound=Callable[..., Any])

try:
    from langsmith import traceable as langsmith_traceable
except Exception:  # pragma: no cover
    langsmith_traceable = None


def setup_langsmith_tracing() -> bool:
    """
    Enables LangSmith tracing via environment variables if configured.
    Returns True when tracing is enabled.
    """
    if not settings.langsmith_tracing_enabled or not settings.langsmith_api_key:
        return False

    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key
    os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project
    os.environ["LANGSMITH_ENDPOINT"] = settings.langsmith_endpoint
    return True


def traceable(name: str, run_type: str = "chain") -> Callable[[F], F]:
    """
    Wrapper that applies LangSmith traceable decorator when available,
    else falls back to a no-op decorator.
    """

    def decorator(func: F) -> F:
        if langsmith_traceable is not None:
            return cast(F, langsmith_traceable(name=name, run_type=run_type)(func))

        @wraps(func)
        def noop(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        return cast(F, noop)

    return decorator
