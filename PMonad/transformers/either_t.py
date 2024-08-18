from __future__ import annotations
from typing import Callable

from ..categories import Monad, MonadTrans
from ..either import Either, Right


class EitherT[M: Monad, E, A](MonadTrans):
    def __init__(self, ea: M[A]) -> None:
        if not isinstance(ea, Monad):
            raise TypeError("'ma' must be an instance of 'Monad'")
        self._base_monad = type(ea)
        self.value = ea

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={repr(self.value)})"

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {self.value}"

    def run(self: EitherT[M, E, A]) -> M[Either[E, A]]:
        return self.value

    def map[B](self: EitherT[M, E, A], f: Callable[A, B]) -> EitherT[M, E, B]:
        return EitherT(self.run().map(lambda ea: ea.map(f)))

    def apply[B](
        self: EitherT[M, E, A], f: EitherT[M, E, Callable[A, B]]
    ) -> EitherT[M, E, B]:
        def bindf(ea: Either[E, A]) -> M[Either[E, B]]:
            if ea.is_left:
                return self._base_monad(ea)
            return self.run().map(lambda ea_: ea_.map(ea.value))

        return EitherT(self.run().bind(bindf))

    def bind[B](
        self: EitherT[M, E, A], f: Callable[A, EitherT[M, E, B]]
    ) -> EitherT[M, E, B]:
        def bindf(ea: Either[E, A]) -> M[Either[E, B]]:
            if ea.is_left:
                return self._base_monad(ea)
            return f(ea.value).run()

        return EitherT(self.run().bind(bindf))

    @classmethod
    def lift(cls, ea: M[A]) -> EitherT[M, E, A]:
        if not isinstance(ea, Monad):
            raise TypeError("'ea' must be an instance of type 'Monad'")
        return EitherT(ea.map(Right))
