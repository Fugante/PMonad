from __future__ import annotations
from typing import Callable

from ..categories import Monad, MonadTrans
from ..maybe import Maybe


class MaybeT[M: Monad, A](MonadTrans):
    def __init__(self, ma: Monad[A]) -> None:
        if not isinstance(ma, Monad):
            raise TypeError("'ma' must be of type 'Monad'")
        self._base_monad = type(ma)
        self.value = ma

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={repr(self.value)})"

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {self.value}"

    def run(self: MaybeT[M, A]) -> M[Maybe[A]]:
        return self.value

    def map[B](self: MaybeT[M, A], f: Callable[A, B]) -> MaybeT[M, B]:
        mt = super().__new__(MaybeT, None, None)
        mt._base_monad = self._base_monad
        mt.value = self.run().map(lambda m: m.map(f))
        return mt

    def apply[B](
        self: MaybeT[M, A], f: MaybeT[M, Callable[A, B]]
    ) -> MaybeT[M, B]:
        def bindf(ma: Maybe[A]) -> M[Maybe[B]]:
            if ma.is_nothing:
                return self._base_monad(ma)
            return f.run().map(lambda ma_: ma_.map(f(ma.value)))

        return MaybeT(self.run().bind(bindf))

    def bind[B](
        self: MaybeT[M, A], f: Callable[A, MaybeT[M, B]]
    ) -> MaybeT[Monad, B]:
        def bindf(ma: Maybe[A]) -> M[Maybe[B]]:
            if ma.is_nothing:
                return self._base_monad(ma)
            return f(ma.value).run()

        return MaybeT(self.run().bind(bindf))

    @classmethod
    def lift(cls, ma: M[A]) -> MaybeT[M, A]:
        return MaybeT(ma.map(Maybe))
