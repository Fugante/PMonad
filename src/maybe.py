from __future__ import annotations
from abc import ABC
from functools import partial
from typing import Callable
from .categories import Monoid, Monad, Foldable


class Maybe[A](Monad[A], Monoid, Foldable[A], ABC):
    def __new__(cls, value=None) -> Maybe[A]:
        if value is None:
            return super().__new__(Nothing)
        just = super().__new__(Just)
        just.value = value
        return just

    def __add__(self: Maybe[A], m: Maybe[A]) -> Maybe[A]:
        return self.append(m)

    @property
    def is_just[A](self: Maybe[A]) -> bool:
        return isinstance(self, Just)

    @property
    def is_nothing[A](self: Maybe[A]) -> bool:
        return isinstance(self, Nothing)

    @classmethod
    def mempty(cls, wrapped_class: type) -> Maybe[A]:
        return Nothing(wrapped_class)

    def append(self: Maybe[Monoid], m: Maybe[Monoid]) -> Maybe[Monoid]:
        match (self, m):
            case (Just(value=a1), Just(value=a2)):
                return Just(a1.append(a2))
            case (Just(value=a1), Nothing):
                return Just(value=a1)
            case (Nothing, Just(value=a2)):
                return Just(value=a2)
            case _:
                return Nothing()

    def map[B](self: Maybe[A], f: Callable[A, B]) -> Maybe[B]:
        match self:
            case Just(value=a):
                try:
                    b = f(a)
                except TypeError:
                    b = partial(f, a)
                return Just(b)
            case _:
                return Nothing()

    def apply[B](self: Maybe[A], f: Maybe[Callable[A, B]]) -> Maybe[B]:
        match (self, f):
            case (Just(value=a), Just(value=f)):
                try:
                    b = f(a)
                except TypeError:
                    b = partial(f, a)
                return Just(b)
            case _:
                return Nothing()

    def bind[B](self: Maybe[A], f: Callable[A, Maybe[B]]) -> Maybe[B]:
        match self:
            case Just(value=a):
                return f(a)
            case _:
                return Nothing()

    def fold[B](self: Maybe[A], f: Callable[[A, B], B], b: B) -> B:
        match self:
            case Just(value=a):
                return f(a, b)
            case _:
                return b


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
