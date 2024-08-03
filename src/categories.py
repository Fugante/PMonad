from __future__ import annotations
from abc import ABC
from typing import Callable


class Semigroup(ABC):
    def append(self: Semigroup, s: Semigroup) -> Semigroup: ...


class Monoid(Semigroup, ABC):
    @classmethod
    def mempty(cls) -> Monoid: ...


class Functor[A](ABC):
    def map[B](self: Functor[A], f: Callable[A, B]) -> Functor[B]: ...


class Applicative[A](Functor[A], ABC):
    def apply[B](
        self: Applicative[A], f: Applicative[Callable[A, B]]
    ) -> Applicative[B]: ...

    def liftA2[B, C](
        self: Applicative[A], f: Callable[[A, B], C], fb: Applicative[B]
    ) -> Applicative[C]:
        fb.apply(self.map(f))


class Monad[A](Applicative[A], ABC):
    def bind[B](self: Monad[A], f: Callable[A, Monad[B]]) -> Monad[B]: ...

    def then[B](self: Monad[A], mb: Monad[B]) -> Monad[B]:
        return mb


class Foldable[A](ABC):
    def fold[A, B](self: Foldable[A], f: Callable[[A, B], B], b: B) -> B: ...


class MonadTrans[M: Monad, A](Monad, ABC):
    @classmethod
    def lift(cls, ma: Monad[A]) -> MonadTrans[M, A]: ...
