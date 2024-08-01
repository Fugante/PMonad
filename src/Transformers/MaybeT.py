from __future__ import annotations
from typing import Callable

from ..categories import Monad, MonadTrans
from ..maybe import Maybe, Just


class MaybeT[A](Monad, MonadTrans):
    def __init__(
        self, base_monad_cls: type, value: A = None
    ) -> MaybeT[Monad[Maybe[A]]]:
        if not issubclass(base_monad_cls, Monad):
            raise ValueError
        self._base_monad = base_monad_cls
        self.value = base_monad_cls(Maybe(value))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={repr(self.value)})"

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {self.value}"

    @property
    def run(self) -> Monad[Maybe[A]]:
        return self.value

    def map[A, B](self: MaybeT[Monad, A], f: Callable[A, B]) -> MaybeT[Monad, B]:
        return self.run.map(lambda m: m.map(f))

    def apply[A, B](
        self: MaybeT[Monad, A], f: MaybeT[Monad, Callable[A, B]]
    ) -> MaybeT[Monad, B]:
        return

    def bind[A, B](
        self: MaybeT[Monad, A], f: Callable[A, MaybeT[Monad, B]]
    ) -> MaybeT[Monad, B]:
        match self.run_MaybeT.value:
            case Just(value=a):
                return f(a)
            case _:
                return MaybeT(self._base_monad, None)
