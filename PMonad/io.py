from __future__ import annotations
from typing import Callable

from .categories import Monoid, Monad
from .functions import trycall


class IO[A](Monoid, Monad[A]):
    def __init__(
        self, result: A | None = None, effect: Callable[A] | None = None
    ) -> None:
        self.effect = effect
        self.result = result if effect is None else effect()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(result={repr(self.result)})"

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {self.result}"

    @classmethod
    def empty(cls) -> IO[A]:
        return IO()

    def concat(self, s: IO[A]) -> IO[A]:
        return IO(self.result.concat(s.result))

    def map[B](self: IO[A], f: Callable[A, B]) -> IO[B]:
        return IO(result=trycall(f, self.result))

    def apply[B](self: IO[A], f: IO[Callable[A, B]]) -> IO[B]:
        return IO(result=trycall(f.result, self.result))

    def bind[B](self: IO[A], f: Callable[A, IO[B]]) -> IO[B]:
        return f(self.result)


def ioeffect[A](f: Callable[..., A]) -> Callable[IO[A]]:
    def ioeffect(*args, **kwargs):
        return IO(effect=lambda: f(*args, **kwargs))

    return ioeffect


ioprint = ioeffect(print)

ioinput = ioeffect(input)
