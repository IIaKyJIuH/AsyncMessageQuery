from __future__ import annotations

import asyncio
import functools
from collections.abc import Awaitable, Callable
from typing import ParamSpec, TypeVar, overload

_P = ParamSpec("_P")
_T = TypeVar("_T")


@overload
def async_retry(
    original_function: Callable[_P, Awaitable[_T]],
) -> Callable[_P, Awaitable[_T]]: ...


@overload
def async_retry(
    *,
    retries: int = 10,
    delay: float = 1.0,
) -> Callable[[Callable[_P, Awaitable[_T]]], Callable[_P, Awaitable[_T]]]: ...


def async_retry(
    original_function: Callable[_P, Awaitable[_T]] | None = None,
    *,
    retries: int = 10,
    delay: float = 1.0,
) -> (
    Callable[[Callable[_P, Awaitable[_T]]], Callable[_P, Awaitable[_T]]]
    | Callable[_P, Awaitable[_T]]
):
    def decorator(func: Callable[_P, Awaitable[_T]]) -> Callable[_P, Awaitable[_T]]:
        @functools.wraps(func)
        async def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _T:
            attempt = 0
            while True:
                try:
                    return await func(*args, **kwargs)
                except Exception:
                    attempt += 1
                    if attempt >= retries:
                        raise
                    await asyncio.sleep(delay)

        return wrapper

    if original_function is not None:
        return decorator(original_function)

    return decorator
