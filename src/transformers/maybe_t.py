from __future__ import annotations
from typing import Callable

from ..categories import Monad, MonadTrans
from ..maybe import Maybe, Just, Nothing


class MaybeT[M: Monad, A](MonadTrans):
    def __init__(self, m: type, a: A) -> MaybeT[M[Maybe[A]]]:
        # TODO: validate m is an instance of a Monad
        self._base_monad = m
        self.value = m(a).map(Maybe)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={repr(self.value)})"

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {self.value}"

    def run(self) -> M[Maybe[A]]:
        return self.value

    def map[A, B](self: MaybeT[M, A], f: Callable[A, B]) -> MaybeT[M, B]:
        mt = super().__new__(MaybeT, None, None)
        mt._base_monad = self._base_monad
        mt.value = self.run().map(lambda m: m.map(f))
        return mt

    def apply[A, B](
        self: MaybeT[Monad, A], f: MaybeT[Monad, Callable[A, B]]
    ) -> MaybeT[Monad, B]:
        def bindf(mf: Maybe[A]) -> Monad[Maybe[A]]:
            match mf:
                case Nothing():
                    return self._base_monad(Nothing())
                case Just(value=f):
                    return self.run().map(lambda ma: ma.map(f))

        return MaybeT.lift(self.run().bind(bindf))

    def bind[A, B](
        self: MaybeT[M, A], f: Callable[A, MaybeT[M, B]]
    ) -> MaybeT[Monad, B]:
        def bindf(ma: Maybe[A]) -> M[Maybe[B]]:
            match ma:
                case Nothing():
                    return self._base_monad(Nothing())
                case Just(value=a):
                    return f(a).run()

        mt = super().__new__(MaybeT, None, None)
        mt._base_monad = self._base_monad
        mt.value = self.run().bind(bindf)
        return mt

    @classmethod
    def lift(cls, ma: M[A]) -> MaybeT[M, A]:
        # TODO: validate ma is an isinstance of Monad
        mt = super().__new__(cls, None, None)
        mt._base_monad = ma.__class__
        mt.value = ma.map(Maybe)
        return mt
