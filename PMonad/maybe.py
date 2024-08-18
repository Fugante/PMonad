from __future__ import annotations
from abc import ABC
from typing import Callable

from .categories import Monoid, Monad, Foldable
from .functions import trycall


class Maybe[A](Monad[A], Monoid, Foldable[A], ABC):
    def __new__(cls, value=None) -> Maybe[A]:
        if value is None:
            return super().__new__(Nothing)
        just = super().__new__(Just)
        just.value = value
        return just

    @property
    def is_just[A](self: Maybe[A]) -> bool:
        return isinstance(self, Just)

    @property
    def is_nothing[A](self: Maybe[A]) -> bool:
        return isinstance(self, Nothing)

    @classmethod
    def empty(cls) -> Maybe[A]:
        return Nothing()

    def concat(self: Maybe[Monoid], m: Maybe[Monoid]) -> Maybe[Monoid]:
        match (self, m):
            case (Just(value=a1), Just(value=a2)):
                return Just(a1 + a2)
            case (Just(value=a1), Nothing):
                return Just(value=a1)
            case (Nothing, Just(value=a2)):
                return Just(value=a2)
            case _:
                return Nothing()

    def map[B](self: Maybe[A], f: Callable[A, B]) -> Maybe[B]:
        return Just(trycall(f, self.value)) if self.is_just else Nothing()

    def apply[B](self: Maybe[A], f: Maybe[Callable[A, B]]) -> Maybe[B]:
        if self.is_just and f.is_just:
            return Just(trycall(f.value, self.value))
        return Nothing()

    def bind[B](self: Maybe[A], f: Callable[A, Maybe[B]]) -> Maybe[B]:
        return f(self.value) if self.is_just else Nothing()

    def fold[B](self: Maybe[A], f: Callable[[A, B], B], b: B) -> B:
        return f(self.value, b) if self.is_just else b


class Just[A](Maybe[A]):
    def __init__(self, value: A) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={repr(self.value)})"

    def __str__(self) -> str:
        return f"Just {self.value}"


class Nothing[A](Maybe[A]):
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __str(self) -> str:
        return self.__class__.__name__
