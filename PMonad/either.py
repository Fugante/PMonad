from __future__ import annotations
from abc import ABC
from typing import Callable

from .categories import Semigroup, Monad
from .functions import trycall


class Either[E, A](Semigroup, Monad[A], ABC):
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={repr(self.value)})"

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {self.value}"

    @property
    def is_right(self: Either[E, A]) -> bool:
        return isinstance(self, Right)

    @property
    def is_left(self: Either[E, A]) -> bool:
        return isinstance(self, Left)

    def concat(self: Either[E, A], e: Either[E, A]) -> Either[E, A]:
        return self if self.is_right else e

    def map[B](self: Either[E, A], f: Callable[A, B]) -> Either[E, B]:
        return Right(trycall(f, self.value)) if self.is_right else self

    def apply[B](self: Either[E, A], f: Either[E, Callable[A, B]]) -> Either[E, B]:
        if self.is_left:
            return self
        if f.is_left:
            return f
        return Right(trycall(f.value, self.value))

    def bind[B](self: Either[E, A], f: Callable[A, Either[E, B]]) -> Either[E, B]:
        return f(self.value) if self.is_right else self


class Left[E](Either):
    def __init__(self, value: E) -> None:
        self.value = value


class Right[A](Either):
    def __init__(self, value: A) -> None:
        self.value = value


def either[E, A, B](fa: Callable[A, B], fe: Callable[E, B], ea: Either[E, A]) -> B:
    return trycall(fa, ea.value) if ea.is_right else trycall(fe, ea.value)


def from_left[E, A](e: E, ea: Either[E, A]) -> E:
    return ea.value if ea.is_left else e


def from_right[E, A](a: A, ea: Either[E, A]) -> A:
    return ea.value if ea.is_right else a
