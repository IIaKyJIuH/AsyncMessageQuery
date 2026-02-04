from __future__ import annotations

import asyncio
import functools
from collections.abc import Awaitable, Callable
from typing import overload


@overload
def async_retry[**P, T](
    original_function: Callable[P, Awaitable[T]],
) -> Callable[P, Awaitable[T]]: ...


@overload
def async_retry[**P, T](
    *,
    retries: int = 10,
    delay: float = 1.0,
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]: ...


def async_retry[**P, T](
    original_function: Callable[P, Awaitable[T]] | None = None,
    *,
    retries: int = 10,
    delay: float = 1.0,
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]] | Callable[P, Awaitable[T]]:
    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
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
