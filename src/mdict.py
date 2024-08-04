from __future__ import annotations
from functools import partial
from typing import Callable

from .categories import Monoid, Monad, Foldable


class Mdict[T, A](dict, Monoid, Monad, Foldable):
    def __init__(self, value: dict[T, A] = None) -> None:
        super().__init__(value if value is not None else {})

    def __add__(self: Mdict[T, A], m: Mdict[T, A]) -> Mdict[T, A]:
        return self.append(m)

    @classmethod
    def mempty(cls) -> Mdict[T, A]:
        return cls()

    def append(self: Mdict[T, A], m: Mdict[T, A]) -> Mdict[T, A]:
        return self.update(m)

    def map[A, B](self: Mdict[T, A], f: Callable[A, B]) -> Mdict[T, B]:
        bs = Mdict()
        for t, a in self.items():
            try:
                b = f(a)
            except TypeError:
                b = partial(f, a)
            bs[t] = b
        return bs

    def apply[A, B](
        self: Mdict[Monoid, A], f: Mdict[Monoid, Callable[A, B]]
    ) -> Mdict[Monoid, B]:
        # TODO: raise error if self and f are not Monoids
        d = Mdict()
        for m1, a in self.items():
            for m2, f in f.items():
                try:
                    b = f(a)
                except TypeError:
                    b = partial(f, a)
                d[m1.mappend(m2)] = b
        return d

    def bind[A, B](self: Mdict[T, A], f: Callable[A, Mdict[T, B]]) -> Mdict[T, B]:
        d1 = Mdict()
        for a in self.values():
            d1.update(f(a))
        return d1

    def fold[A, B](self: Mdict[T, A], f: Callable[[A, B], B], b: B) -> B:
        for a in self.values():
            b = f(a, b)
        return b
