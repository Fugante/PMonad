from __future__ import annotations
from functools import partial
from typing import Callable

from .categories import Monad, Foldable


class IO[A](Monad, Foldable, Callable):
    def __init__(self, effect: Callable[A]) -> None:
        self.executed = False
        self.effect = effect
        self.result = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(effect={repr(self.effect)})"

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {self.effect}"

    def __enter__(self, *args, **kwargs) -> A:
        self()
        return self.result

    def __exit__(self, *args, **kwargs) -> None:
        return

    def __call__(self) -> None:
        if self.executed:
            raise ValueError
        self.result = self.effect()
        self.executed = True

    def map[A, B](self: IO[A], f: Callable[A, B]) -> IO[B]:
        if not self.executed:
            self()
        return IO(f(self.value))

    def apply[A, B](self: IO[A], f: IO[Callable[A, B]]) -> IO[B]:
        if not self.executed:
            self()
        if not f.executed:
            f()
        return IO(f.result(self.result))

    def bind[A, B](self: IO[A], f: Callable[A, IO[B]]) -> IO[B]:
        if not self.executed:
            self()
        io = f(self.result)
        io()
        return io


def ioeffect[A](f: Callable[..., A]) -> Callable[IO[A]]:
    def effect(*args, **kwargs):
        return IO(partial(f, *args, **kwargs))

    return effect
