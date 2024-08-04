from __future__ import annotations
from functools import partial
from typing import Callable

from .categories import Monad


class IO[A](Monad[A]):
    def __init__(
        self, result: A | None = None, effect: Callable[A] | None = None
    ) -> None:
        self.effect = effect
        self.result = result if effect is None else effect()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(result={repr(self.result)})"

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {self.result}"

    def map[A, B](self: IO[A], f: Callable[A, B]) -> IO[B]:
        try:
            b = f(self.result)
        except ValueError:
            b = partial(f, self.result)
        return IO(result=b)

    def apply[B](self: IO[A], f: IO[Callable[A, B]]) -> IO[B]:
        try:
            b = f.result(self.result)
        except ValueError:
            b = partial(f.result, self.result)
        return IO(result=b)

    def bind[B](self: IO[A], f: Callable[A, IO[B]]) -> IO[B]:
        return f(self.result)


def ioeffect[A](f: Callable[..., A]) -> Callable[IO[A]]:
    def ioeffect(*args, **kwargs):
        return IO(effect=lambda: f(*args, **kwargs))

    return ioeffect
