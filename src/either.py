from __future__ import annotations
from abc import ABC
from functools import partial
from typing import Callable

from .categories import Semigroup, Monad


class Either[E, A](Semigroup, Monad[A], ABC):
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={repr(self.value)})"

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {self.value}"

    def __add__(self: Either[E, A], e: Either[E, A]) -> Either[E, A]:
        return self.append(e)

    @property
    def is_right(self: Either[E, A]) -> bool:
        return isinstance(self, Right)

    @property
    def is_left(self: Either[E, A]) -> bool:
        return isinstance(self, Left)

    def append(self: Either[E, A], e: Either[E, A]) -> Either[E, A]:
        match self, e:
            case Left(), e:
                return e
            case Right(), _:
                return self

    def map[B](self: Either[E, A], f: Callable[A, B]) -> Either[E, B]:
        match self:
            case Right(value=a):
                try:
                    b = f(a)
                except TypeError:
                    b = partial(f, a)
                return Right(b)
            case _:
                return self

    def apply[B](self: Either[E, A], f: Either[E, Callable[A, B]]) -> Either[E, B]:
        match self, f:
            case Left(), _:
                return self
            case _, Left():
                return f
            case Right(value=a), Right(value=f):
                try:
                    b = f(a)
                except TypeError:
                    b = partial(f, a)
                return Right(b)

    def bind[B](self: Either[E, A], f: Callable[A, Either[E, B]]) -> Either[E, B]:
        match self:
            case Right(value=a):
                return f(a)
            case _:
                return self


class Left[E](Either):
    def __init__(self, value: E) -> None:
        self.value = value


class Right[A](Either):
    def __init__(self, value: A) -> None:
        self.value = value
