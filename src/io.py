from __future__ import annotations
from functools import partial
from typing import Callable

from .categories import Monad, Foldable


class IO[A](Monad[A], Foldable[A], Callable[[...], A]):
    def __init__(
        self, result: A | None = None, effect: Callable[A] | None = None
    ) -> None:
        self.executed = False
        self.effect = effect
        self.result = result

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(result={repr(self.result)})"

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {self.result}"

    def __enter__(self, *args, **kwargs) -> A:
        self()
        return self.result

    def __exit__(self, *args, **kwargs) -> None:
        return

    def __call__(self) -> None:
        if self.executed:
            raise ValueError
        if not isinstance(self.effect, Callable):
            self.executed = True
            return
        self.result = self.effect()
        self.executed = True

    def map[A, B](self: IO[A], f: Callable[A, B]) -> IO[B]:
        if not self.executed:
            self()
        try:
            b = f(self.result)
        except ValueError:
            b = partial(f, self.result)
        self.result = b
        return self

    def apply[A, B](self: IO[A], f: IO[Callable[A, B]]) -> IO[B]:
        if not self.executed:
            self()
        if not f.executed:
            f()
        try:
            b = f.result(self.result)
        except ValueError:
            b = partial(f.result, self.result)
        self.result = b
        return self

    def bind[A, B](self: IO[A], f: Callable[A, IO[B]]) -> IO[B]:
        if not self.executed:
            self()
        io = f(self.result)
        return io


def ioeffect[A](f: Callable[..., A]) -> Callable[IO[A]]:
    def ioeffect(*args, **kwargs):
        return IO(effect=lambda: f(*args, **kwargs))

    return ioeffect
