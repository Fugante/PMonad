from __future__ import annotations
from typing import Callable

from .categories import Monoid, Monad, Foldable


class MDict[T, A](dict, Monoid, Monad, Foldable):
    def __init__(self, value: dict[T, A] = None) -> None:
        super().__init__(value if value is not None else {})

    def __add__(self: MDict[T, A], m: MDict[T, A]) -> MDict[T, A]:
        return self.mappend(m)

    @classmethod
    def mempty(cls) -> MDict[T, A]:
        return cls()

    def append(self: MDict[T, A], m: MDict[T, A]) -> MDict[T, A]:
        return self.update(m)

    def map[A, B](self: MDict[T, A], f: Callable[A, B]) -> MDict[T, B]:
        return MDict({t: f(a) for (t, a) in self.items()})

    def apply[A, B](
        self: MDict[Monoid, A], f: MDict[Monoid, Callable[A, B]]
    ) -> MDict[Monoid, B]:
        d = MDict()
        for m1, a in self.items():
            for m2, f in f.items():
                d[m1.mappend(m2)] = f(a)
        return d

    def bind[A, B](self: MDict[T, A], f: Callable[A, MDict[T, B]]) -> MDict[T, B]:
        d1 = MDict()
        for a in self.values():
            d1.update(f(a))
        return d1

    def fold[A, B](self: MDict[T, A], f: Callable[A, B, B], b: B) -> B:
        for a in self.values():
            b = f(a, b)
        return b
