from __future__ import annotations
from functools import partial
from typing import Callable, Iterable, Awaitable

from .categories import Monoid, Monad, Foldable


class Mlist[A](list, Monoid, Monad, Foldable):
    def __init__(self, iterable: Iterable[A] | None = None) -> None:
        super().__init__(iterable if iterable is not None else [])

    @classmethod
    def mempty(cls) -> Mlist[A]:
        return Mlist([])

    def map[A, B](self: Mlist[A], f: Callable[A, B]) -> Mlist[B]:
        bs = []
        for a in self:
            try:
                b = f(a)
            except TypeError:
                b = partial(f, a)
            bs.append(b)
        return Mlist(bs)

    async def amap[A, B](self: Mlist[A], f: Callable[A, Awaitable[B]]) -> Mlist[B]:
        bs = []
        for a in self:
            try:
                b = await f(a)
            except TypeError:
                b = partial(f, a)
            bs.append(b)
        return Mlist(bs)

    def apply[A, B](self: Mlist[A], fs: Mlist[Callable[A, B]]) -> Mlist[B]:
        bs = []
        for a in self:
            for f in fs:
                try:
                    b = f(a)
                except TypeError:
                    b = partial(f, a)
                bs.append(b)
        return Mlist(bs)

    def bind[A, B](self: Mlist[A], f: Callable[A, Mlist[B]]) -> Mlist[B]:
        return Mlist(b for lb in (f(a) for a in self) for b in lb)

    def fold[A, B](self: Mlist[A], f: Callable[[A, B], B], b: B) -> B:
        for a in self:
            b = f(a, b)
        return b
