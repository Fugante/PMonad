from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Callable

from .functions import const, identity


class Semigroup(ABC):
    def append(self: Semigroup, s: Semigroup) -> Semigroup: ...


class Monoid(Semigroup, ABC):
    @classmethod
    def mempty(cls, wrapped_class: type) -> Monoid: ...


class Functor[A](ABC):
    @abstractmethod
    def map[B](self: Functor[A], f: Callable[A, B]) -> Functor[B]: ...

    def map_replace[B](self: Functor[A], b: B) -> Functor[B]:
        return self.map(const(b))


class Applicative[A](Functor[A], ABC):
    @abstractmethod
    def apply[B](
        self: Applicative[A], f: Applicative[Callable[A, B]]
    ) -> Applicative[B]: ...

    def liftA2[B, C](
        self: Applicative[A], f: Callable[[A, B], C], fb: Applicative[B]
    ) -> Applicative[C]:
        return fb.apply(self.map(f))

    def rapply[B](self: Applicative[A], b: Applicative[B]) -> Applicative[B]:
        return b.apply(self.map_replace(identity))

    def lapply[B](self: Applicative[A], b: Applicative[B]) -> Applicative[A]:
        return self.liftA2(const, b)


class Monad[A](Applicative[A], ABC):
    @abstractmethod
    def bind[B](self: Monad[A], f: Callable[A, Monad[B]]) -> Monad[B]: ...

    def then[B](self: Monad[A], mb: Monad[B]) -> Monad[B]:
        return mb


class Foldable[A](ABC):
    @abstractmethod
    def fold[A, B](self: Foldable[A], f: Callable[[A, B], B], b: B) -> B: ...


class MonadTrans[M: Monad, A](Monad, ABC):
    @abstractmethod
    def run(self: MonadTrans[M, A]) -> M[A]: ...

    @classmethod
    @abstractmethod
    def lift(cls, ma: Monad[A]) -> MonadTrans[M, A]: ...
