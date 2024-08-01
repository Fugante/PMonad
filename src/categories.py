from __future__ import annotations
from abc import ABC
from typing import Callable


class Monoid(ABC):
    @classmethod
    def mempty(cls) -> Monoid: ...

    def append(self: Monoid, m: Monoid) -> Monoid: ...


class Functor[A](ABC):
    def map[A, B](self: Functor[A], f: Callable[A, B]) -> Functor[B]: ...


class Applicative[A](Functor[A], ABC):
    def apply[A, B](
        self: Applicative[A], f: Applicative[Callable[A, B]]
    ) -> Applicative[B]: ...

    def liftA2[A, B, C](
        self: Applicative[A], f: Callable[[A, B], C], fb: Applicative[B]
    ) -> Applicative[C]:
        fb.apply(self.map(f))


class Monad[A](Applicative[A], ABC):
    def bind[A, B](self: Monad[A], f: Callable[A, Monad[B]]) -> Monad[B]: ...


class Foldable[A](ABC):
    def fold[A, B](self: Foldable[A], f: Callable[[A, B], B], b: B) -> B: ...


class MonadTrans[M: Monad, A](Monad, ABC):
    @classmethod
    def lift(cls, ma: Monad[A]) -> MonadTrans[M, A]:
        # TODO: validate ma is an isinstance of Monad
        mt = cls.__new__()
        mt._base_monad = ma.__class__
        mt.value = ma
        return mt
