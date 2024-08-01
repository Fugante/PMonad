from __future__ import annotations
from typing import Callable, Iterable, Awaitable

from .categories import Monoid, Monad, Foldable


class MList[A](list, Monoid, Monad, Foldable):
    def __init__(self, iterable: Iterable[A] = None) -> None:
        super().__init__(iterable if iterable is not None else [])

    def __add_(self: MList[A], m: MList[A]) -> MList[A]:
        return self.mappend(m)

    @classmethod
    def mempty(cls) -> MList[A]:
        return MList([])

    def mappend(self: MList[A], m: MList[A]) -> MList[A]:
        return self + m

    def map[A, B](self: MList[A], f: Callable[A, B]) -> MList[B]:
        return [f(a) for a in self]

    async def amap[A, B](self: MList[A], f: Callable[A, Awaitable[B]]) -> MList[B]:
        return [await f(a) for a in self]

    def apply[A, B](self: MList[A], fs: MList[Callable[A, B]]) -> MList[B]:
        return MList(f(a) for f in fs for a in self)

    def bind[A, B](self: MList[A], f: Callable[A, MList[B]]) -> MList[B]:
        return MList(b for lb in (f(a) for a in self) for b in lb)

    def fold[A, B](self: MList[A], f: Callable[[A, B], B], b: B) -> B:
        for a in self:
            b = f(a, b)
        return b
