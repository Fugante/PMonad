from __future__ import annotations
from inspect import signature
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
        params = signature(f).parameters
        # TODO: raise error if number of parameters is 0
        if len(params) == 1:
            return Mlist(f(a) for a in self)
        return Mlist(partial(f, a) for a in self)

    async def amap[A, B](self: Mlist[A], f: Callable[A, Awaitable[B]]) -> Mlist[B]:
        params = signature(f).parameters
        # TODO: raise error if number of parameters is 0
        if len(params) == 1:
            return Mlist(await f(a) for a in self)
        return Mlist(partial(f, a) for a in self)

    def apply[A, B](self: Mlist[A], fs: Mlist[Callable[A, B]]) -> Mlist[B]:
        # TODO: validate all functions have same signature
        return Mlist(f(a) for f in fs for a in self)

    def bind[A, B](self: Mlist[A], f: Callable[A, Mlist[B]]) -> Mlist[B]:
        return Mlist(b for lb in (f(a) for a in self) for b in lb)

    def fold[A, B](self: Mlist[A], f: Callable[[A, B], B], b: B) -> B:
        for a in self:
            b = f(a, b)
        return b
